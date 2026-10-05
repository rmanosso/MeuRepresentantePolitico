"""Importação dos dados abertos oficiais do TSE (candidaturas, bens e resultados)."""
import csv
import io
import json
import re
import zipfile
from datetime import date, datetime
from pathlib import Path

import requests

from . import config, resultados

NULOS = {"#NULO", "#NULO#", "#NE", "NÃO DIVULGÁVEL", ""}


def baixar(url: str, forcar: bool = False) -> Path:
    """Baixa um arquivo para o cache, só repetindo o download se o TSE o atualizou."""
    config.CACHE.mkdir(exist_ok=True)
    destino = config.CACHE / url.rsplit("/", 1)[-1]
    meta = destino.with_suffix(destino.suffix + ".json")
    cabecalhos = {}
    if destino.exists() and meta.exists() and not forcar:
        cabecalhos["If-Modified-Since"] = json.loads(meta.read_text())["last_modified"]
    resp = requests.get(url, headers=cabecalhos, stream=True, timeout=120)
    if resp.status_code == 304:
        print(f"  sem mudanças: {destino.name}")
        return destino
    resp.raise_for_status()
    with open(destino, "wb") as f:
        for bloco in resp.iter_content(1 << 16):
            f.write(bloco)
    meta.write_text(json.dumps({"url": url, "last_modified": resp.headers.get("Last-Modified", "")}))
    print(f"  baixado: {destino.name} ({destino.stat().st_size // 1024} KB, TSE: {resp.headers.get('Last-Modified')})")
    return destino


def ler_csv_zip(caminho, nome_arquivo):
    with zipfile.ZipFile(caminho) as z:
        with z.open(nome_arquivo) as f:
            for linha in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
                yield {k: (None if v.strip() in NULOS else v.strip()) for k, v in linha.items()}


def _idade(nascimento: str | None) -> int | None:
    if not nascimento:
        return None
    try:
        n = datetime.strptime(nascimento, "%d/%m/%Y").date()
    except ValueError:
        return None
    ref = date.fromisoformat(config.DATA_ELEICAO)
    return ref.year - n.year - ((ref.month, ref.day) < (n.month, n.day))


def _titulo(texto: str | None) -> str | None:
    """'FULANO DE TAL' -> 'Fulano de Tal' (mantendo preposições em minúsculas)."""
    if not texto:
        return texto
    minusculas = {"de", "da", "do", "das", "dos", "e"}
    partes = texto.lower().split()
    return " ".join(p if (i and p in minusculas) else re.sub(r"[^\W\d_]", lambda m: m.group().upper(), p, count=1)
                    for i, p in enumerate(partes))


def _bens(caminho) -> dict[str, float]:
    totais: dict[str, float] = {}
    for b in ler_csv_zip(caminho, f"bem_candidato_{config.ANO}_BRASIL.csv"):
        try:
            valor = float((b["VR_BEM_CANDIDATO"] or "0").replace(".", "").replace(",", "."))
        except ValueError:
            continue
        totais[b["SQ_CANDIDATO"]] = totais.get(b["SQ_CANDIDATO"], 0.0) + valor
    return totais


def _pilar(cargo: str) -> str | None:
    for chave, p in config.PILARES.items():
        if cargo in p["cargos"]:
            return chave
    return None


def _sem_substituidos(candidatos: list[dict], rotulo: str) -> list[dict]:
    """O TSE mantém no arquivo o registro substituído e o substituto com o mesmo número.

    Fica o registro APTO (quando a situação já foi divulgada) ou, na falta dela,
    o de SQ_CANDIDATO mais recente (registros com votos na totalização têm prioridade); o nome anterior é guardado em 'substitui'.
    """
    grupos: dict[tuple, list[dict]] = {}
    for c in candidatos:
        grupos.setdefault((c["uf"], c["cargo"], c["numero"]), []).append(c)
    saida, descartados = [], 0
    for grupo in grupos.values():
        grupo.sort(key=lambda c: ("votos" in c, c["situacao_candidatura"] == "APTO", int(c["id"])), reverse=True)
        escolhido = grupo[0]
        anteriores = [c["nome_urna"] for c in grupo[1:] if c["nome_urna"] != escolhido["nome_urna"]]
        if anteriores:
            escolhido["substitui"] = anteriores
        descartados += len(grupo) - 1
        saida.append(escolhido)
    if descartados:
        print(f"  {descartados} registro(s) substituído(s) com o mesmo número descartado(s) ({rotulo})")
    return saida


def importar(forcar: bool = False) -> dict:
    """Retorna {'gerado_em': ..., 'candidatos': [...]} com os dados públicos e objetivos do TSE.

    Dados pessoais sensíveis (CPF, título de eleitor, e-mail, data de nascimento
    completa) são descartados aqui e nunca chegam ao site (LGPD).
    """
    print("Importando dados do TSE…")
    arq_cand = baixar(config.URL_CANDIDATOS, forcar)
    arq_bens = baixar(config.URL_BENS, forcar)
    bens = _bens(arq_bens)
    totalizacao = resultados.importar()

    # Uma linha por candidato e turno: fica a do turno mais recente.
    por_sq: dict[str, dict] = {}
    gerado_em = None
    for l in ler_csv_zip(arq_cand, f"consulta_cand_{config.ANO}_BRASIL.csv"):
        gerado_em = gerado_em or f"{l['DT_GERACAO']} {l['HH_GERACAO']}"
        sq = l["SQ_CANDIDATO"]
        if sq in por_sq and int(por_sq[sq]["NR_TURNO"]) >= int(l["NR_TURNO"]):
            continue
        por_sq[sq] = l

    titulares, vinculados = [], []
    for l in por_sq.values():
        sq = l["SQ_CANDIDATO"]
        cargo = l["DS_CARGO"]
        uf = l["SG_UF"]
        federal = cargo in ("PRESIDENTE", "VICE-PRESIDENTE")
        cd = config.CD_ELEICAO_FEDERAL if federal else config.CD_ELEICAO_ESTADUAL
        sit_tse = l["DS_SIT_TOT_TURNO"]
        c = {
            "id": sq,
            "uf": uf,
            "cargo": cargo,
            "pilar": _pilar(cargo),
            "numero": l["NR_CANDIDATO"],
            "nome": _titulo(l["NM_CANDIDATO"]),
            "nome_urna": _titulo(l["NM_SOCIAL_CANDIDATO"] or l["NM_URNA_CANDIDATO"]),
            "partido": l["SG_PARTIDO"],
            "partido_nome": l["NM_PARTIDO"],
            "federacao": l["SG_FEDERACAO"],
            "coligacao": None if l["NM_COLIGACAO"] == "PARTIDO ISOLADO" else l["NM_COLIGACAO"],
            "composicao": l["DS_COMPOSICAO_COLIGACAO"],
            "idade": _idade(l["DT_NASCIMENTO"]),
            "genero": _titulo(l["DS_GENERO"]),
            "cor_raca": _titulo(l["DS_COR_RACA"]),
            "instrucao": _titulo(l["DS_GRAU_INSTRUCAO"]),
            "ocupacao": _titulo(l["DS_OCUPACAO"]),
            "situacao_candidatura": l["DS_SITUACAO_CANDIDATURA"],
            "resultado": config.RESULTADOS.get(sit_tse or "", "aguardando"),
            "resultado_tse": sit_tse,
            "turno": int(l["NR_TURNO"]),
            "bens_declarados": round(bens[sq], 2) if sq in bens else None,
            "foto": config.URL_FOTO.format(ano=config.ANO, cd=cd, uf=uf.lower(), sq=sq),
            "tse_url": config.URL_DIVULGACAND.format(
                ano=config.ANO, sqele=config.SQ_ELEICAO_DIVULGACAND, uf=uf, sq=sq),
        }
        r = totalizacao.get(sq)
        if r:
            c["votos"], c["percentual"] = r["votos"], r["percentual"]
            c["totalizacao"] = {k: r[k] for k in ("totalizacao", "atualizado", "fonte")}
            if c["resultado"] == "aguardando" and "resultado" in r:
                c["resultado"] = r["resultado"]
                c["resultado_tse"] = r["situacao_tse"] or ("2º turno (resultado matematicamente definido)"
                                                           if r["resultado"] == "segundo_turno" else None)
        (vinculados if cargo in config.CARGOS_VINCULADOS else titulares).append(c)

    titulares = _sem_substituidos(titulares, "titulares")
    vinculados = _sem_substituidos(vinculados, "vices e suplentes")

    # Vice e suplentes compartilham UF e número com o titular da chapa.
    chave = {(c["uf"], c["cargo"], c["numero"]): c for c in titulares}
    for v in vinculados:
        tit = chave.get((v["uf"], config.CARGOS_VINCULADOS[v["cargo"]], v["numero"]))
        if tit is not None:
            tit.setdefault("chapa", []).append(
                {"cargo": v["cargo"], "nome_urna": v["nome_urna"], "partido": v["partido"], "foto": v["foto"]})
    for t in titulares:
        t.get("chapa", []).sort(key=lambda v: v["cargo"])

    titulares = [c for c in titulares if c["pilar"]]
    print(f"  {len(titulares)} candidaturas titulares, dados TSE gerados em {gerado_em}")
    return {"gerado_em": gerado_em, "candidatos": titulares}
