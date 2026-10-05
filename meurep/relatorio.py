"""Relatório em PDF para revisão jurídica dos dossiês (inclui itens ainda não publicados)."""
import shutil
import subprocess
from datetime import datetime
from html import escape
from pathlib import Path

from . import config
from .dossies import CRITERIO_PUBLICACAO, SITUACOES_CONDUTA

NAVEGADORES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google-chrome", "chromium", "chromium-browser", "msedge",
]

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body { font: 10.5pt/1.45 "Segoe UI", Arial, sans-serif; color: #1c1b22; }
h1 { font-size: 20pt; margin: 0 0 4mm; }
h2 { font-size: 14pt; margin: 9mm 0 3mm; border-bottom: 1.5px solid #6D28D9; padding-bottom: 1mm; }
h3 { font-size: 12pt; margin: 6mm 0 2mm; }
.capa { border-left: 6px solid #6D28D9; padding: 2mm 0 2mm 6mm; margin-bottom: 8mm; }
.capa p { margin: 1mm 0; color: #55525e; }
.aviso { border: 1.5px solid #991b1b; background: #fef2f2; padding: 3mm 4mm; margin: 4mm 0; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0; font-size: 9.5pt; }
th, td { border: 1px solid #d6d3cd; padding: 1.6mm 2mm; text-align: left; vertical-align: top; }
th { background: #f1efe9; }
.item { border: 1px solid #d6d3cd; border-radius: 3mm; padding: 4mm 5mm; margin: 5mm 0; }
h2, h3, .meta { break-after: avoid; }
.parecer, .pergunta, .texto { break-inside: avoid; }
.item.pendente { border-left: 5px solid #b45309; }
.item.publicado { border-left: 5px solid #166534; }
.rotulo { display: inline-block; font-size: 8.5pt; font-weight: 700; padding: .5mm 2mm; border-radius: 2mm; margin-right: 2mm; }
.r-pendente { background: #ffedd5; color: #9a3412; }
.r-publicado { background: #dcfce7; color: #166534; }
.r-sit { background: #ecebe8; color: #33313a; }
.texto { background: #faf9f6; border: 1px dashed #d6d3cd; padding: 2.5mm 3mm; margin: 2mm 0; }
.pergunta { background: #f5f3ff; padding: 2.5mm 3mm; margin: 2mm 0; }
.fontes { font-size: 9pt; word-break: break-all; }
.parecer { margin-top: 3mm; font-size: 9.5pt; }
.parecer .linha { border-bottom: 1px solid #9a97a3; height: 7mm; }
.quebra { page-break-before: always; }
small, .meta { color: #55525e; }
"""


def _fontes(lista: list[dict]) -> str:
    return "<ol class='fontes'>" + "".join(
        f"<li>{'<b>[oficial]</b> ' if f['oficial'] else ''}{escape(f.get('veiculo') or '')}"
        f"{' — ' if f.get('veiculo') else ''}{escape(f['titulo'])}<br>{escape(f['url'])}</li>" for f in lista) + "</ol>"


def _item_conduta(n: str, k: dict) -> str:
    pend = k["status"] != "confirmado"
    rot = ("<span class='rotulo r-pendente'>PENDENTE — NÃO PUBLICADO</span>" if pend
           else "<span class='rotulo r-publicado'>PUBLICADO</span>")
    meta = " · ".join(x for x in [k["tipo_texto"], f"data: {k['data']}" if k.get("data") else "",
                                  f"processo: {k['processo']}" if k.get("processo") else ""] if x)
    return f"""
    <div class="item {'pendente' if pend else 'publicado'}">
      <div>{rot}<span class="rotulo r-sit">{escape(k['situacao_texto'])}</span> <b>Item {n}</b></div>
      <h3>{escape(k['titulo'])}</h3>
      <p class="meta">{escape(meta)}</p>
      <p><b>Texto {'proposto' if pend else 'publicado'} no site:</b></p>
      <div class="texto">{escape(k['resumo'])}</div>
      {f"<p><b>Posição do(a) candidato(a):</b> {escape(k['resposta'])}</p>" if k.get('resposta') else ""}
      {f"<div class='pergunta'><b>Pergunta para a revisão:</b> {escape(k['nota_revisao'])}</div>" if k.get('nota_revisao') else ""}
      <p><b>Fontes:</b></p>{_fontes(k['fontes'])}
      <div class="parecer"><b>Parecer:</b> ☐ Publicar como está &nbsp; ☐ Publicar com ajustes &nbsp; ☐ Não publicar &nbsp; ☐ Retirar do site
        <p>Observações / redação sugerida:</p><div class="linha"></div><div class="linha"></div><div class="linha"></div>
        <p>Revisor(a): ______________________________ &nbsp; Data: ____/____/2026</p></div>
    </div>"""


def html(candidatos: list[dict], dossies: dict) -> str:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    alvo = [c for c in candidatos if c["id"] in dossies]
    alvo.sort(key=lambda c: (config.ORDEM_CARGOS.index(c["cargo"]), c["uf"], -(c.get("votos") or 0)))

    linhas, fichas, anexos = [], [], []
    for ci, c in enumerate(alvo, 1):
        d = dossies[c["id"]]
        local = "Brasil" if c["uf"] == "BR" else config.UFS.get(c["uf"], c["uf"])
        cab = f"{escape(c['nome_urna'])} ({escape(c['partido'])}) — {escape(c['cargo'].title())}, {escape(local)}"
        fichas.append(f"<h2 class='quebra'>{ci}. {cab}</h2><p class='meta'>Nome completo: {escape(c['nome'])} · "
                      f"situação: {escape(c.get('resultado_tse') or c['resultado'])} · id TSE {c['id']}</p>")
        if not d["conduta"]:
            fichas.append("<p>Sem registros de conduta no dossiê.</p>")
        for j, k in enumerate(d["conduta"], 1):
            n = f"{ci}.{j}"
            linhas.append(f"<tr><td>{n}</td><td>{escape(c['nome_urna'])}</td><td>{escape(k['titulo'])}</td>"
                          f"<td>{escape(k['situacao_texto'])}</td><td>{'Pendente' if k['status'] != 'confirmado' else 'Publicado'}</td></tr>")
            fichas.append(_item_conduta(n, k))
        traj = "".join(f"<li><b>{escape(str(t['ano'] or ''))}</b> — {escape(t['titulo'])}"
                       f"{' <i>(pendente)</i>' if t['status'] != 'confirmado' else ''}"
                       f"<div class='fontes'>{'; '.join(escape(f['url']) for f in t['fontes'])}</div></li>"
                       for t in d["trajetoria"])
        anexos.append(f"<h3>{cab}</h3><ul>{traj}</ul>"
                      f"<p class='meta'>{len(d['propostas'])} propostas resumidas a partir do plano de governo registrado no TSE "
                      f"(com indicação de página; visíveis no site).</p>")

    situacoes = "".join(f"<tr><td>{escape(k)}</td><td>{escape(v)}</td></tr>" for k, v in SITUACOES_CONDUTA.items())
    pend = sum(1 for d in dossies.values() for k in d["conduta"] if k["status"] != "confirmado")
    publ = sum(1 for d in dossies.values() for k in d["conduta"] if k["status"] == "confirmado")
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Revisão jurídica — Meu Representante</title><style>{CSS}</style></head><body>
<div class="capa">
  <h1>Relatório para revisão jurídica</h1>
  <p><b>Meu Representante</b> — dossiê aberto sobre candidatos das Eleições 2026</p>
  <p>Escopo: candidatos do 2º turno, Presidência e governos estaduais ({escape(config.DATA_SEGUNDO_TURNO_TXT)})</p>
  <p>Gerado em {agora}</p>
</div>
<div class="aviso"><b>Documento interno e confidencial.</b> Contém {pend} registro(s) ainda não publicado(s), que não devem ser
divulgados antes da conclusão da revisão. Os demais {publ} registro(s) já estão no site.</div>

<h2>1. O que pedimos</h2>
<p>O projeto é cidadão, apartidário e de código aberto. Ele reúne informação pública sobre candidatos: propostas, trajetória
e registros de conduta (processos e controvérsias). Antes de divulgar amplamente, pedimos a avaliação jurídica de cada registro
de conduta, em especial:</p>
<ol>
  <li>se a <b>situação processual</b> descrita está correta e atualizada;</li>
  <li>se a <b>redação</b> é factual, neutra e atribui corretamente as afirmações às fontes;</li>
  <li>se há <b>risco</b> na publicação (honra, sigilo processual, legislação eleitoral, LGPD) e qual ajuste o reduziria;</li>
  <li>se o <b>critério de publicação</b> abaixo é adequado e está sendo aplicado de forma igual aos candidatos.</li>
</ol>
<p>Cada ficha tem um campo de parecer. Comentários livres também são bem-vindos.</p>

<h2>2. Critérios editoriais</h2>
<p><b>Critério de publicação:</b> {escape(CRITERIO_PUBLICACAO)}</p>
<ul>
  <li>Toda afirmação precisa de fonte com link. Fontes oficiais (tribunais, MP, órgãos públicos) são preferidas.</li>
  <li>Registros sem fonte oficial exigem pelo menos duas fontes jornalísticas independentes.</li>
  <li>A situação processual é sempre informada (tabela abaixo); investigação ou denúncia não significa culpa.</li>
  <li>O posicionamento público do candidato é registrado junto ao fato.</li>
  <li>Não são publicados CPF, endereço, contatos ou dados de familiares.</li>
  <li>Qualquer pessoa, incluindo candidatos e assessorias, pode pedir correção; conteúdo contestado sem fonte suficiente é retirado
      até a verificação.</li>
</ul>
<table><tr><th>Situação</th><th>Significado no site</th></tr>{situacoes}</table>

<h2>3. Resumo dos registros de conduta</h2>
<table><tr><th>Item</th><th>Candidato(a)</th><th>Registro</th><th>Situação processual</th><th>Status</th></tr>{''.join(linhas)}</table>

{''.join(fichas)}

<h2 class="quebra">Anexo — trajetória publicada</h2>
<p>Itens de menor risco, com fontes oficiais em sua maioria. Incluídos para conferência geral.</p>
{''.join(anexos)}
</body></html>"""


def gerar(candidatos: list[dict], dossies: dict) -> Path:
    pasta = config.RAIZ / "revisao"
    pasta.mkdir(exist_ok=True)
    # Horário no nome: cada versão é um arquivo novo (o anterior pode estar aberto num leitor de PDF).
    dia = datetime.now().strftime("%Y-%m-%d_%Hh%M")
    arq_html = pasta / f"relatorio_revisao_juridica_{dia}.html"
    arq_pdf = arq_html.with_suffix(".pdf")
    arq_html.write_text(html(candidatos, dossies), encoding="utf-8")
    nav = next((n for n in NAVEGADORES if Path(n).exists() or shutil.which(n)), None)
    if not nav:
        print(f"Navegador não encontrado; abra {arq_html} e imprima como PDF.")
        return arq_html
    subprocess.run([nav, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={arq_pdf}", arq_html.as_uri()], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    if not arq_pdf.exists():
        print(f"Não foi possível gerar o PDF; abra {arq_html} no navegador e imprima como PDF.")
        return arq_html
    return arq_pdf
