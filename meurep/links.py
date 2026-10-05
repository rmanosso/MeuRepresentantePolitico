"""Conferência automática de links: usada na validação dos dossiês e na triagem de sugestões."""
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests

from .dossies import DOMINIOS_OFICIAIS

UA = {"User-Agent": "Mozilla/5.0 (MeuRepresentante; verificador de fontes)"}
BLOQUEIO = {401, 403, 405, 429, 503}  # sites que barram robôs: exigem conferência manual


def verificar(url: str) -> tuple[str, str]:
    """Retorna (situação, detalhe): 'ok', 'manual' (bloqueado para robôs) ou 'erro'."""
    try:
        r = requests.head(url, headers=UA, timeout=20, allow_redirects=True)
        if r.status_code >= 400:
            r = requests.get(url, headers=UA, timeout=25, allow_redirects=True, stream=True)
        if r.status_code < 400:
            return "ok", str(r.status_code)
        if r.status_code in BLOQUEIO:
            return "manual", f"HTTP {r.status_code} (site bloqueia verificação automática)"
        return "erro", f"HTTP {r.status_code}"
    except requests.Timeout:
        return "manual", "sem resposta no prazo (conferir manualmente)"
    except requests.RequestException as e:
        return "erro", type(e).__name__


def verificar_varios(urls: list[str]) -> dict[str, tuple[str, str]]:
    unicos = list(dict.fromkeys(urls))
    with ThreadPoolExecutor(max_workers=8) as ex:
        return dict(zip(unicos, ex.map(verificar, unicos)))


def oficial(url: str) -> bool:
    return (urlparse(url).hostname or "").endswith(DOMINIOS_OFICIAIS)


def triagem(texto: str) -> str:
    """Relatório em Markdown para uma sugestão enviada pelo público (comentado na issue)."""
    urls = list(dict.fromkeys(re.findall(r"https?://[^\s)>\]\"']+", texto)))
    if not urls:
        return ("### Triagem automática\n\nNenhum link encontrado. Toda informação precisa de fonte: "
                "edite a sugestão e inclua os links.")
    res = verificar_varios(urls)
    validos = [u for u in urls if res[u][0] != "erro"]  # link quebrado não conta como fonte
    dominios = {urlparse(u).hostname for u in validos}
    tem_oficial = any(oficial(u) for u in validos)
    icone = {"ok": "✅", "manual": "⚠️", "erro": "❌"}
    linhas = [f"| {icone[res[u][0]]} | {'oficial' if oficial(u) else ''} | {u} | {res[u][1]} |" for u in urls]
    criterio = ("✅ Há fonte oficial." if tem_oficial else
                "✅ Há duas ou mais fontes de domínios diferentes." if len(dominios) >= 2 else
                "❌ Sem fonte oficial e com menos de duas fontes independentes: para registros de conduta, "
                "inclua mais uma fonte de outro veículo ou um documento oficial.")
    return "\n".join([
        "### Triagem automática", "",
        "| | Tipo | Link | Resultado |", "|---|---|---|---|", *linhas, "",
        f"**Critério de fontes:** {criterio}", "",
        "⚠️ = o site bloqueia robôs; a coordenação confere manualmente. "
        "Esta checagem não avalia o conteúdo: a sugestão segue para triagem humana.",
    ])
