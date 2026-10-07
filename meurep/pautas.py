"""Pautas acompanhadas: tramitação oficial (APIs da Câmara e do Senado) desenhada como percurso.

Cada pauta é um YAML curto em dados/pautas/ com o que exige curadoria (resumo neutro, contexto e
debate com fontes). Etapa atual, eventos e autores vêm das APIs a cada geração do site; se a API
falhar, usa-se a última resposta guardada em cache/pautas/.
"""
import json
import re

import requests
import yaml

from . import config

PASTA = config.DADOS / "pautas"
CACHE = config.CACHE / "pautas"
API_SENADO = "https://legis.senado.leg.br/dadosabertos/processo/{id}"
API_CAMARA = "https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}"
PAGINA_SENADO = "https://www25.senado.leg.br/web/atividade/materias/-/materia/{codigo}"
PAGINA_CAMARA = "https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={id}"

CASAS = {"SF": "Senado", "CD": "Câmara"}
PODER_DA_CASA = {"SF": "senado", "CD": "camara"}

# Percursos por tipo. "casa": ini = Casa iniciadora, rev = revisora. Explicações seguem a Constituição.
PERCURSOS = {
    "PEC": [
        {"id": "apresentacao", "nome": "Apresentação", "casa": "ini",
         "explica": "Precisa da assinatura de ao menos 1/3 dos senadores (27) ou dos deputados (171), ou ser "
                    "enviada pela Presidência ou por mais da metade das Assembleias Legislativas (CF, art. 60)."},
        {"id": "comissoes_ini", "nome": "Comissões", "casa": "ini",
         "explica": "No Senado, a CCJ analisa a constitucionalidade e o mérito. Na Câmara, a CCJ vê se a proposta "
                    "pode tramitar e uma comissão especial analisa o conteúdo. Um relator é designado e apresenta parecer."},
        {"id": "plenario_ini", "nome": "Plenário · 2 turnos", "casa": "ini",
         "explica": "Votação em dois turnos. Em cada um, precisa de 3/5 dos votos: 49 dos 81 senadores ou 308 dos 513 deputados."},
        {"id": "comissoes_rev", "nome": "Comissões", "casa": "rev",
         "explica": "A outra Casa repete a análise nas suas comissões."},
        {"id": "plenario_rev", "nome": "Plenário · 2 turnos", "casa": "rev",
         "explica": "De novo dois turnos com 3/5 dos votos. Se o texto for alterado, a parte modificada volta à Casa anterior."},
        {"id": "promulgacao", "nome": "Promulgação", "casa": "congresso",
         "explica": "As Mesas da Câmara e do Senado promulgam a emenda, que passa a fazer parte da Constituição. "
                    "PEC não vai à sanção: a Presidência não pode vetar."},
    ],
    "PL": [
        {"id": "apresentacao", "nome": "Apresentação", "casa": "ini",
         "explica": "Pode ser apresentado por parlamentares, comissões, pela Presidência, pelos tribunais superiores, "
                    "pela PGR ou por iniciativa popular (CF, art. 61)."},
        {"id": "comissoes_ini", "nome": "Comissões", "casa": "ini",
         "explica": "As comissões temáticas analisam o mérito e a CCJ, a constitucionalidade. Alguns projetos são "
                    "decididos nas próprias comissões, sem passar pelo Plenário (caráter conclusivo ou terminativo)."},
        {"id": "plenario_ini", "nome": "Plenário", "casa": "ini",
         "explica": "Aprovação por maioria simples dos presentes (lei ordinária) ou maioria absoluta (lei complementar)."},
        {"id": "comissoes_rev", "nome": "Comissões", "casa": "rev",
         "explica": "A outra Casa revisa o texto nas suas comissões."},
        {"id": "plenario_rev", "nome": "Plenário", "casa": "rev",
         "explica": "Se a Casa revisora alterar o texto, ele volta à Casa iniciadora, que decide sobre as mudanças."},
        {"id": "sancao", "nome": "Sanção ou veto", "casa": "executivo",
         "explica": "A Presidência tem 15 dias úteis para sancionar (aprovar) ou vetar, no todo ou em parte (CF, art. 66)."},
        {"id": "vetos", "nome": "Análise dos vetos", "casa": "congresso",
         "explica": "Em sessão conjunta, o Congresso pode derrubar o veto com maioria absoluta: 257 deputados e 41 senadores."},
        {"id": "lei", "nome": "Lei publicada", "casa": "executivo",
         "explica": "Promulgada e publicada no Diário Oficial, a lei entra em vigor na data que ela mesma definir."},
    ],
}
PERCURSOS["PLP"] = PERCURSOS["PL"]

JUDICIARIO = {"id": "stf", "nome": "STF (se questionada)", "casa": "judiciario",
              "explica": "Depois de valer, a norma pode ser contestada no Supremo por meio de ação direta "
                         "(ADI). O STF pode declará-la inconstitucional, no todo ou em parte. Não é etapa obrigatória."}

ENCERRADA = re.compile(r"arquiv|retirad|rejeitad|prejudicad|devolvid", re.I)


def _get(url: str, nome: str) -> dict | None:
    """Busca JSON na API; guarda a resposta e, se a API falhar, devolve a última guardada."""
    arq = CACHE / f"{nome}.json"
    try:
        r = requests.get(url, headers={"Accept": "application/json"}, timeout=40)
        r.raise_for_status()
        dados = r.json()
        CACHE.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        return dados
    except (requests.RequestException, ValueError) as e:
        print(f"  aviso: {url} indisponível ({e.__class__.__name__}); usando cache")
        return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None


def _senado(pid: int) -> dict | None:
    p = _get(API_SENADO.format(id=pid), f"senado_{pid}")
    if not p:
        return None
    eventos = []
    for aut in p.get("autuacoes") or []:
        for inf in aut.get("informesLegislativos") or []:
            col = inf.get("colegiado") or {}
            eventos.append({"data": inf["data"][:10], "casa": "SF", "orgao": col.get("sigla"),
                            "orgao_nome": col.get("nome"), "texto": inf.get("descricao", "")})
    abertas = [s for a in p.get("autuacoes") or [] for s in a.get("situacoes") or [] if not s.get("fim")]
    atual = abertas[-1] if abertas else {}
    doc = p.get("documento") or {}
    return {
        "eventos": eventos,
        "situacao": (atual.get("descricao") or p.get("situacaoAtual") or "").capitalize(),
        "desde": atual.get("inicio") or p.get("dataSituacaoAtual"),
        "local": (atual.get("colegiado") or {}).get("nome"),
        "local_sigla": (atual.get("colegiado") or {}).get("sigla"),
        "tramitando": p.get("tramitando") == "Sim",
        "norma": p.get("normaGerada") or None,
        "ementa": (p.get("conteudo") or {}).get("ementa") or doc.get("ementa"),
        "apresentacao": doc.get("dataApresentacao"),
        "autores": [{"nome": a["autor"], "partido": a.get("siglaPartido"), "uf": a.get("uf"),
                     "cargo": a.get("cargo")} for a in doc.get("autoria") or []],
        "texto_url": doc.get("url"),
        "pagina": PAGINA_SENADO.format(codigo=p.get("codigoMateria")),
        "identificacao": p.get("identificacao"),
    }


def _camara(pid: int) -> dict | None:
    p = _get(API_CAMARA.format(id=pid), f"camara_{pid}")
    t = _get(API_CAMARA.format(id=pid) + "/tramitacoes", f"camara_{pid}_tram")
    au = _get(API_CAMARA.format(id=pid) + "/autores", f"camara_{pid}_autores") or {"dados": []}
    if not p or not t:
        return None
    d = p["dados"]
    st = d.get("statusProposicao") or {}
    eventos = [{"data": e["dataHora"][:10], "casa": "CD", "orgao": e.get("siglaOrgao"), "orgao_nome": e.get("siglaOrgao"),
                "texto": " ".join(x for x in (e.get("descricaoTramitacao"), e.get("despacho")) if x)}
               for e in t["dados"]]
    return {
        "eventos": eventos,
        "situacao": st.get("descricaoSituacao") or "",
        "desde": (st.get("dataHora") or "")[:10],
        "local": st.get("siglaOrgao"),
        "local_sigla": st.get("siglaOrgao"),
        "tramitando": not ENCERRADA.search(st.get("descricaoSituacao") or ""),
        "norma": None,
        "ementa": d.get("ementa"),
        "apresentacao": (d.get("dataApresentacao") or "")[:10],
        "autores": [{"nome": a["nome"], "partido": None, "uf": None, "cargo": a.get("tipo")}
                    for a in au["dados"] if a.get("proponente")],
        "texto_url": d.get("urlInteiroTeor"),
        "pagina": PAGINA_CAMARA.format(id=pid),
        "identificacao": f"{d.get('siglaTipo')} {d.get('numero')}/{d.get('ano')}",
    }


# Órgãos de plenário/mesa: atos administrativos deles herdam a etapa em que a proposta já estava.
ORGAOS_PLENARIO = {"PLEN", "MESA", "SGM", "CCP", "SLSF", "SEADI"}
PLACAR = re.compile(r"sim:?\s*(\d+)\s*;?\s*não:?\s*(\d+)", re.I)


def _etapa_do_evento(ev: dict, ini: str, tipo: str) -> str | None:
    """Classifica um evento oficial numa etapa do percurso (regras simples e auditáveis).
    Devolve None quando o evento é administrativo e deve herdar a etapa anterior."""
    txt = ev["texto"].lower()
    if tipo != "PEC" and re.search(r"sanção|sancionad|vetad|veto", txt):
        return "vetos" if "derrub" in txt or "manuten" in txt else "sancao"
    if re.search(r"promulgad", txt):
        return "promulgacao" if tipo == "PEC" else "lei"
    lado = "ini" if ev["casa"] == ini else "rev"
    if ev["orgao"] in ORGAOS_PLENARIO:
        if re.search(r"turno|votaç|ordem do dia|discussão", txt) or (
                re.search(r"aprovad|rejeitad", txt) and "requerimento" not in txt):
            return f"plenario_{lado}"
        if lado == "ini" and re.search(r"remetid|remessa|vai à câmara|vai ao senado", txt):
            return "plenario_ini"
        return None
    return f"comissoes_{lado}"


def _classificar(eventos: list[dict], ini: str, tipo: str) -> None:
    """Etapa de cada evento (em ordem cronológica); administrativos herdam a anterior."""
    anterior, casa_ant = "apresentacao", ini
    for ev in eventos:
        etapa = _etapa_do_evento(ev, ini, tipo)
        if etapa is None:
            # primeiro ato na outra Casa abre a fase de comissões dela; senão, segue onde estava
            etapa = f"comissoes_{'ini' if ev['casa'] == ini else 'rev'}" if ev["casa"] != casa_ant else anterior
        ev["etapa"], anterior, casa_ant = etapa, etapa, ev["casa"]
        m = PLACAR.search(ev["texto"])
        turno = re.search(r"(primeiro|segundo|1º|2º) turno", ev["texto"], re.I)
        if m and turno and "requerimento" not in ev["texto"].lower():  # só votações da proposta, não de requerimentos
            ev["placar"] = {"sim": int(m[1]), "nao": int(m[2]), "turno": turno[1].lower().replace("º", "")}


def montar(cfg: dict) -> dict:
    tipo, ini = cfg["tipo"], cfg["casa_iniciadora"]
    fontes = {"SF": _senado(cfg["senado_id"]) if cfg.get("senado_id") else None,
              "CD": _camara(cfg["camara_id"]) if cfg.get("camara_id") else None}
    base = fontes[ini]
    if base is None:
        raise RuntimeError(f"pauta {cfg['id']}: sem dados da Casa iniciadora")
    rev = "CD" if ini == "SF" else "SF"
    eventos = sorted(base["eventos"] + (fontes[rev]["eventos"] if fontes[rev] else []), key=lambda e: e["data"])
    percurso = PERCURSOS[tipo]
    ordem = [e["id"] for e in percurso]
    _classificar(eventos, ini, tipo)
    atual_doc = fontes[rev] if fontes[rev] else base  # a Casa onde a proposta está agora
    feitas = [ordem.index(ev["etapa"]) for ev in eventos if ev["etapa"] in ordem]
    i_atual = max(feitas, default=0)
    encerrada = not atual_doc["tramitando"] or bool(ENCERRADA.search(atual_doc["situacao"]))
    if base.get("norma"):
        i_atual, encerrada = len(ordem) - 1, False

    etapas = []
    for i, e in enumerate(percurso):
        casa = {"ini": ini, "rev": rev}.get(e["casa"], e["casa"])
        etapas.append({
            "id": e["id"], "nome": e["nome"], "explica": e["explica"],
            "poder": PODER_DA_CASA.get(casa, casa),
            "casa_nome": CASAS.get(casa, {"congresso": "Congresso", "executivo": "Presidência"}.get(casa, casa)),
            "estado": "feita" if i < i_atual else ("atual" if i == i_atual else "futura"),
            "eventos": [ev for ev in eventos if ev["etapa"] == e["id"]][::-1],
        })
    if not encerrada and i_atual == len(ordem) - 1:
        etapas[-1]["estado"] = "feita"

    return {
        **{k: cfg.get(k) for k in ("id", "tipo", "titulo", "tema", "resumo", "resumo_fontes", "contexto",
                                   "contexto_fontes", "debate", "atualizado_em", "relacionadas")},
        "identificacao": base["identificacao"],
        "casa_iniciadora": CASAS[ini],
        "ementa": base["ementa"],
        "apresentacao": base["apresentacao"],
        "autores": base["autores"],
        "situacao": atual_doc["situacao"],
        "desde": atual_doc["desde"],
        "local": atual_doc["local"],
        "tramitando": not encerrada,
        "sem_sancao": tipo == "PEC",
        "etapa_atual": ordem[i_atual],
        "etapas": etapas,
        "judiciario": JUDICIARIO,
        "eventos": eventos[::-1],
        "links": [x for x in (
            {"titulo": f"Ficha no {CASAS[ini]}", "url": base["pagina"]},
            {"titulo": f"Ficha no {CASAS[rev]}", "url": fontes[rev]["pagina"]} if fontes[rev] else None,
            {"titulo": "Texto original", "url": base["texto_url"]} if base["texto_url"] else None) if x],
    }


def carregar() -> list[dict]:
    return [yaml.safe_load(a.read_text(encoding="utf-8")) for a in sorted(PASTA.glob("*.yaml"))]


def gerar(destino) -> list[dict]:
    """Escreve <destino>/pautas.json (lista resumida) e <destino>/pauta/<id>.json (percurso completo)."""
    pautas = []
    for cfg in carregar():
        try:
            p = montar(cfg)
        except RuntimeError as e:  # API fora do ar e sem cache: pula a pauta, não derruba o site
            print(f"  aviso: {e}")
            continue
        (destino / "pauta").mkdir(parents=True, exist_ok=True)
        (destino / "pauta" / f"{p['id']}.json").write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
        pautas.append({k: p[k] for k in ("id", "tipo", "identificacao", "titulo", "tema", "resumo", "situacao",
                                         "desde", "local", "tramitando", "etapa_atual", "casa_iniciadora")}
                      | {"progresso": [e["estado"] for e in p["etapas"]]})
    (destino / "pautas.json").write_text(json.dumps(pautas, ensure_ascii=False), encoding="utf-8")
    print(f"Pautas: {len(pautas)} acompanhada(s)")
    return pautas
