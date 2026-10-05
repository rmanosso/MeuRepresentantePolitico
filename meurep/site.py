"""Geração do site estático (HTML/CSS/JS + dados em JSON) a partir do TSE e dos dossiês."""
import json
import shutil
from collections import Counter
from datetime import datetime, timedelta, timezone

from . import config
from .dossies import CRITERIO_PUBLICACAO, publico

BRASILIA = timezone(timedelta(hours=-3))  # o GitHub Actions roda em UTC
DERIVADOS = ("foto", "tse_url")  # recalculados no navegador para deixar os JSON leves


def montar(base_tse: dict, dossies: dict, manuais: dict) -> list[dict]:
    """Junta dados do TSE, resultados manuais e dossiês em uma lista de candidatos."""
    candidatos = []
    for c in base_tse["candidatos"]:
        c = dict(c)
        m = manuais.get(c["id"])
        if m and c["resultado"] == "aguardando":
            c["resultado"] = m["resultado"]
            c["resultado_fontes"] = m["fontes"]
        if c["id"] in dossies:
            c["dossie"] = publico(dossies[c["id"]])
        candidatos.append(c)
    return candidatos


def _compacto(c: dict) -> dict:
    saida = {k: v for k, v in c.items() if v not in (None, [], "") and k not in DERIVADOS}
    if "chapa" in saida:
        saida["chapa"] = [{k: v for k, v in x.items() if k != "foto"} for x in saida["chapa"]]
    return saida


def _escrever(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def gerar(candidatos: list[dict], gerado_em_tse: str) -> None:
    if config.SAIDA.exists():
        shutil.rmtree(config.SAIDA)
    shutil.copytree(config.WEB, config.SAIDA)
    dados = config.SAIDA / "dados"

    nacional = [c for c in candidatos if c["pilar"] != "camara"]
    _escrever(dados / "nacional.json", [_compacto(c) for c in nacional])
    for uf in config.UFS:
        deps = [c for c in candidatos if c["pilar"] == "camara" and c["uf"] == uf]
        _escrever(dados / "uf" / f"{uf}.json", [_compacto(c) for c in deps])

    datas = [datetime.strptime(c["totalizacao"]["atualizado"], "%d/%m/%Y %H:%M:%S")
             for c in candidatos if c.get("totalizacao", {}).get("atualizado", "").count(":") == 2]
    contagem = Counter((c["uf"], c["cargo"], c["resultado"]) for c in candidatos)
    meta = {
        "ano": config.ANO,
        "repo_url": config.REPO_URL,
        "data_segundo_turno_txt": config.DATA_SEGUNDO_TURNO_TXT,
        "criterio_publicacao": CRITERIO_PUBLICACAO,
        "tse_gerado_em": gerado_em_tse,
        "totalizacao_atualizada": max(datas).strftime("%d/%m/%Y %H:%M") if datas else None,
        "site_gerado_em": datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M"),
        "pilares": config.PILARES,
        "ordem_cargos": config.ORDEM_CARGOS,
        "ufs": config.UFS,
        "url_foto": config.URL_FOTO,
        "url_divulgacand": config.URL_DIVULGACAND,
        "cd_eleicao_federal": config.CD_ELEICAO_FEDERAL,
        "cd_eleicao_estadual": config.CD_ELEICAO_ESTADUAL,
        "sq_eleicao": config.SQ_ELEICAO_DIVULGACAND,
        "total": len(candidatos),
        "com_dossie": sum(1 for c in candidatos if "dossie" in c),
        "resultados_disponiveis": any(c["resultado"] != "aguardando" for c in candidatos),
        "contagem": [[uf, cargo, res, n] for (uf, cargo, res), n in sorted(contagem.items())],
    }
    _escrever(dados / "meta.json", meta)
    (config.SAIDA / ".nojekyll").write_text("")
    print(f"Site gerado em {config.SAIDA} ({len(candidatos)} candidaturas, {meta['com_dossie']} com dossiê)")
