"""Leitura e validação dos dossiês curados (dados/dossies/<UF>/<id>.yaml).

Regras editoriais aplicadas automaticamente (ver docs/METODOLOGIA.md):
  * todo item precisa de pelo menos uma fonte com URL https;
  * itens de conduta precisam de uma situação processual explícita
    (presunção de inocência: investigado ≠ réu ≠ condenado);
  * conduta sem fonte oficial (tribunal, MP, órgão público) exige
    pelo menos duas fontes jornalísticas independentes;
  * todo item tem um status de verificação. Só itens "confirmado" são
    publicados; itens "em_revisao" ficam fora do site e dos cards e entram
    no relatório de revisão jurídica.
"""
from datetime import date
from urllib.parse import urlparse

import yaml

from . import config

SITUACOES_CONDUTA = {
    "investigado": "Investigado (inquérito ou apuração em andamento)",
    "denunciado": "Denunciado pelo Ministério Público (denúncia ainda não recebida)",
    "reu": "Réu (denúncia ou ação recebida pela Justiça, sem julgamento)",
    "condenado_1a_instancia": "Condenado em 1ª instância (cabe recurso)",
    "condenado_2a_instancia": "Condenado em 2ª instância / órgão colegiado (cabe recurso)",
    "condenado_definitivo": "Condenado com trânsito em julgado (decisão definitiva)",
    "absolvido": "Absolvido",
    "arquivado": "Arquivado",
    "prescrito": "Extinto por prescrição",
    "anulado": "Processo ou condenação anulados",
    "sancao_administrativa": "Sanção administrativa (TCU, TCE, CGU, órgão de classe)",
    "contas_rejeitadas": "Contas rejeitadas por Tribunal de Contas ou Justiça Eleitoral",
    "inelegivel": "Declarado inelegível pela Justiça Eleitoral",
    "registro_publico": "Fato público documentado (sem processo)",
}

TIPOS_CONDUTA = {
    "criminal": "Criminal",
    "improbidade": "Improbidade administrativa",
    "eleitoral": "Eleitoral",
    "contas": "Contas públicas",
    "civil": "Cível",
    "trabalhista": "Trabalhista",
    "etica": "Ética / decoro parlamentar",
    "declaracao": "Declarações públicas",
    "outro": "Outro",
}

STATUS = {
    "confirmado": "Confirmado: fato verificável, publicado",
    "em_revisao": "Em revisão: fora do site até a conferência",
}

CRITERIO_PUBLICACAO = (
    "Publica-se o item com fonte oficial ou decisão encerrada, confirmado por pelo menos duas "
    "fontes independentes. Processos em andamento sem documento oficial aguardam revisão jurídica."
)

DOMINIOS_OFICIAIS = (".jus.br", ".mp.br", ".gov.br", ".leg.br", ".def.br")


class ErroDossie(Exception):
    pass


def _oficial(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host.endswith(DOMINIOS_OFICIAIS)


def _fontes(item: dict, onde: str, erros: list[str]) -> list[dict]:
    fontes = item.get("fontes") or ([item["fonte"]] if item.get("fonte") else [])
    normalizadas = []
    for f in fontes:
        if isinstance(f, str):
            f = {"url": f}
        url = (f or {}).get("url", "")
        if not url.startswith("https://"):
            erros.append(f"{onde}: fonte sem URL https ({url!r})")
            continue
        normalizadas.append({
            "titulo": f.get("titulo") or urlparse(url).hostname,
            "url": url,
            "veiculo": f.get("veiculo"),
            "data": str(f["data"]) if f.get("data") else None,
            "oficial": _oficial(url),
        })
    if not normalizadas:
        erros.append(f"{onde}: nenhuma fonte válida")
    return normalizadas


def _status(item: dict, fontes: list[dict], padrao_conduta: bool, onde: str, erros: list[str]) -> str:
    """Status explícito no YAML; sem ele, conduta nasce 'em_revisao' e os demais itens são
    confirmados automaticamente quando têm fonte oficial ou duas fontes distintas."""
    st = item.get("status")
    if st is not None:
        if st not in STATUS:
            erros.append(f"{onde}: 'status' deve ser um de {sorted(STATUS)}")
        return st
    if padrao_conduta:
        return "em_revisao"
    distintas = len({f["url"] for f in fontes})
    return "confirmado" if any(f["oficial"] for f in fontes) or distintas >= 2 else "em_revisao"


def validar(d: dict, origem: str) -> tuple[dict, list[str]]:
    erros: list[str] = []
    if not d.get("id"):
        erros.append(f"{origem}: campo 'id' (SQ_CANDIDATO do TSE) é obrigatório")

    propostas = []
    for i, p in enumerate(d.get("propostas") or []):
        onde = f"{origem} propostas[{i}]"
        if not p.get("resumo"):
            erros.append(f"{onde}: 'resumo' obrigatório")
        fontes = _fontes(p, onde, erros)
        propostas.append({"tema": p.get("tema", "Geral"), "resumo": p.get("resumo", ""),
                          "fontes": fontes, "status": _status(p, fontes, False, onde, erros)})

    trajetoria = []
    for i, t in enumerate(d.get("trajetoria") or []):
        onde = f"{origem} trajetoria[{i}]"
        if not t.get("titulo"):
            erros.append(f"{onde}: 'titulo' obrigatório")
        fontes = _fontes(t, onde, erros)
        trajetoria.append({"ano": t.get("ano"), "titulo": t.get("titulo", ""),
                           "resumo": t.get("resumo", ""), "fontes": fontes,
                           "status": _status(t, fontes, False, onde, erros)})

    conduta = []
    for i, c in enumerate(d.get("conduta") or []):
        onde = f"{origem} conduta[{i}]"
        sit = c.get("situacao")
        if sit not in SITUACOES_CONDUTA:
            erros.append(f"{onde}: 'situacao' deve ser uma de {sorted(SITUACOES_CONDUTA)}")
        tipo = c.get("tipo", "outro")
        if tipo not in TIPOS_CONDUTA:
            erros.append(f"{onde}: 'tipo' deve ser um de {sorted(TIPOS_CONDUTA)}")
        fontes = _fontes(c, onde, erros)
        if fontes and not any(f["oficial"] for f in fontes) and len({f["url"] for f in fontes}) < 2:
            erros.append(f"{onde}: sem fonte oficial, são exigidas ao menos 2 fontes independentes")
        conduta.append({
            "tipo": tipo, "tipo_texto": TIPOS_CONDUTA.get(tipo, tipo),
            "situacao": sit, "situacao_texto": SITUACOES_CONDUTA.get(sit, sit),
            "titulo": c.get("titulo", ""), "resumo": c.get("resumo", ""),
            "processo": c.get("processo"), "data": str(c["data"]) if c.get("data") else None,
            "resposta": c.get("resposta"),  # posicionamento do candidato, se houver
            "fontes": fontes,
            "status": _status(c, fontes, True, onde, erros),
            "nota_revisao": c.get("nota_revisao"),  # pergunta/observação para o revisor
        })

    limpo = {
        "id": str(d.get("id", "")),
        "atualizado_em": str(d.get("atualizado_em") or date.today()),
        "resumo": d.get("resumo"),
        "propostas": propostas,
        "trajetoria": sorted(trajetoria, key=lambda t: str(t["ano"] or ""), reverse=True),
        "conduta": conduta,
        "links": d.get("links") or [],
    }
    return limpo, erros


def publico(dossie: dict) -> dict:
    """Versão do dossiê que pode ir ao ar: só itens confirmados, sem notas internas."""
    saida = dict(dossie)
    for secao in ("propostas", "trajetoria", "conduta"):
        saida[secao] = [{k: v for k, v in item.items() if k not in ("status", "nota_revisao")}
                        for item in dossie[secao] if item["status"] == "confirmado"]
    return saida


def _ler_pasta(pasta, erros: list[str]) -> dict[str, dict]:
    saida = {}
    for arq in sorted(pasta.rglob("*.y*ml")) if pasta.exists() else []:
        if arq.name.startswith("_"):
            continue
        origem = str(arq.relative_to(config.RAIZ))
        try:
            bruto = yaml.safe_load(arq.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            erros.append(f"{origem}: YAML inválido: {e}")
            continue
        limpo, errs = validar(bruto, origem)
        erros += errs
        if limpo["id"] in saida:
            erros.append(f"{origem}: id {limpo['id']} duplicado")
        saida[limpo["id"]] = limpo
    return saida


def carregar(incluir_privados: bool = False) -> tuple[dict[str, dict], list[str]]:
    """Carrega os dossiês. Arquivos iniciados por '_' são modelos e são ignorados.

    dados/privado/ (fora do git) guarda itens ainda em conferência; eles só são somados
    quando incluir_privados=True (relatório de revisão), nunca na geração do site.
    """
    erros: list[str] = []
    dossies = _ler_pasta(config.DOSSIES, erros)
    if incluir_privados:
        for i, priv in _ler_pasta(config.PRIVADO, erros).items():
            base = dossies.setdefault(i, {**priv, "propostas": [], "trajetoria": [], "conduta": []})
            for secao in ("propostas", "trajetoria", "conduta"):
                for item in priv[secao]:
                    base[secao].append({**item, "privado": True})
    return dossies, erros


def carregar_resultados_manuais() -> tuple[dict[str, dict], list[str]]:
    """Resultados informados manualmente (com fonte) enquanto o TSE não atualiza os dados abertos."""
    arq = config.DADOS / "resultados.yaml"
    if not arq.exists():
        return {}, []
    bruto = yaml.safe_load(arq.read_text(encoding="utf-8")) or {}
    saida, erros = {}, []
    for i, r in enumerate(bruto.get("resultados") or []):
        onde = f"dados/resultados.yaml[{i}]"
        if r.get("resultado") not in ("eleito", "segundo_turno", "nao_eleito", "suplente"):
            erros.append(f"{onde}: resultado inválido")
        fontes = _fontes(r, onde, erros)
        saida[str(r.get("id"))] = {"resultado": r.get("resultado"), "fontes": fontes}
    return saida, erros
