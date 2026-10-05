"""Resultados da totalização em tempo real do TSE (resultados.tse.jus.br).

Os dados abertos (consulta_cand) só recebem a situação final dias depois da
eleição. A totalização é publicada na hora pelo TSE em arquivos JSON, um por
eleição/UF/cargo (o mesmo que alimenta o app "Resultados").
"""
import json
from concurrent.futures import ThreadPoolExecutor

import requests

from . import config

BASE = "https://resultados.tse.jus.br/oficial/ele{ano}/{ele}/dados/{uf}/{uf}-c{cargo:04d}-e{ele:06d}-u.json"
URL_APP = "https://resultados.tse.jus.br/oficial/app/index.html"

# código do cargo na totalização -> nome no cadastro
CARGOS = {1: "PRESIDENTE", 3: "GOVERNADOR", 5: "SENADOR",
          6: "DEPUTADO FEDERAL", 7: "DEPUTADO ESTADUAL", 8: "DEPUTADO DISTRITAL"}
MAJORITARIOS_2T = {1, 3}  # cargos com possibilidade de 2º turno


def _arquivos():
    yield int(config.CD_ELEICAO_FEDERAL), "br", 1
    for uf in config.UFS:
        for cargo in (3, 5, 6, 8 if uf == "DF" else 7):
            yield int(config.CD_ELEICAO_ESTADUAL), uf.lower(), cargo


def _num(s: str | None) -> float | None:
    return float(s.replace(",", ".")) if s else None


def _baixar(ele: int, uf: str, cargo: int) -> tuple[int, str, dict | None]:
    url = BASE.format(ano=config.ANO, ele=ele, uf=uf, cargo=cargo)
    destino = config.CACHE / "totalizacao" / url.rsplit("/", 1)[-1]
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(r.content)
        return cargo, url, r.json()
    except (requests.RequestException, ValueError):
        if destino.exists():  # sem rede: usa a última cópia baixada
            return cargo, url, json.loads(destino.read_bytes())
        return cargo, url, None


def importar() -> dict[str, dict]:
    """Retorna {SQ_CANDIDATO: {resultado, votos, percentual, situacao_tse, fonte, ...}}."""
    print("Importando totalização do TSE…")
    with ThreadPoolExecutor(max_workers=8) as ex:
        arquivos = list(ex.map(lambda a: _baixar(*a), _arquivos()))

    saida: dict[str, dict] = {}
    falhas = 0
    for cargo, url, d in arquivos:
        if d is None:
            falhas += 1
            continue
        finalizada = d.get("tf") == "s"
        definida = d.get("md") == "s"
        atualizado = f"{d.get('dt') or d.get('dg')} {d.get('ht') or d.get('hg')}"
        cands = [c for cg in d.get("carg", []) for a in cg.get("agr", [])
                 for p in a.get("par", []) for c in p.get("cand", [])]
        validos = sorted((c for c in cands if c.get("dvt") == "Válido"),
                         key=lambda c: -int(c.get("vap") or 0))
        for c in cands:
            st = (c.get("st") or "").strip()
            r = {
                "votos": int(c["vap"]) if c.get("vap") else None,
                "percentual": _num(c.get("pvap")),
                "situacao_tse": st or None,
                "totalizacao": "finalizada" if finalizada else "em andamento",
                "atualizado": atualizado,
                "fonte": url,
            }
            if st:
                r["resultado"] = config.RESULTADOS.get(st.upper(), "aguardando")
            elif cargo in MAJORITARIOS_2T and definida and len(validos) >= 2 \
                    and (_num(validos[0].get("pvap")) or 0) < 50:
                # Sem situação oficial ainda, mas o TSE sinaliza resultado
                # matematicamente definido: os dois mais votados vão ao 2º turno.
                r["resultado"] = "segundo_turno" if c in validos[:2] else "nao_eleito"
                r["derivado"] = True
            saida[c["sqcand"]] = r
    com_sit = sum(1 for r in saida.values() if "resultado" in r)
    print(f"  {len(arquivos) - falhas}/{len(arquivos)} arquivos, {len(saida)} candidatos com votos, "
          f"{com_sit} com situação definida")
    return saida
