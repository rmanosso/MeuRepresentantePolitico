"""Kit do Instagram: foto de perfil, capas de destaques e carrossel de lançamento."""
import math
from pathlib import Path

from PIL import Image, ImageDraw

from . import config
from .cards import A, FUNDO, LINHA, TINTA, TINTA_2, _hex, _quebrar, fonte

ROXO = _hex(config.PILARES["executivo"]["cor"])
CORES = [_hex(config.PILARES[p]["cor"]) for p in ("executivo", "senado", "camara")]
SAIDA = config.RAIZ / "instagram"
DY = (A - 1350) // 2  # desloca o miolo dos slides, desenhados para 1350, para centralizar em 3:4


def triangulo(d: ImageDraw.ImageDraw, cx: int, cy: int, raio: int, destaque: int | None = None,
              rotulos: list[str] | None = None, fundo=FUNDO, traco=TINTA):
    """Logo: triângulo com os três pilares nos vértices (Executivo no topo)."""
    pts = [(cx + raio * math.cos(a), cy + raio * math.sin(a))
           for a in (-math.pi / 2, math.pi * 5 / 6, math.pi / 6)]  # topo, base esq., base dir.
    d.line(pts + [pts[0]], fill=traco, width=max(4, raio // 22), joint="curve")
    r = raio // 3.2
    for i, ((x, y), cor) in enumerate(zip(pts, CORES)):
        c = cor if destaque in (None, i) else (200, 198, 192)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c, outline=fundo, width=max(3, raio // 40))
        if rotulos:
            f = fonte(int(r * 0.42), True)
            d.text((x, y), rotulos[i], font=f, fill="white", anchor="mm")
    return pts


def foto_perfil() -> Path:
    img = Image.new("RGB", (1080, 1080), FUNDO)
    triangulo(ImageDraw.Draw(img), 540, 590, 330)
    return _salvar(img, "perfil.png")


def destaques() -> list[Path]:
    capas = [("2turno", ROXO, "2º"), ("como-funciona", ROXO, "?"), ("colabore", ROXO, "+"),
             ("executivo", CORES[0], 0), ("senado", CORES[1], 1), ("camaras", CORES[2], 2)]
    saidas = []
    for nome, cor, simbolo in capas:
        img = Image.new("RGB", (1080, 1920), cor)
        d = ImageDraw.Draw(img)
        d.ellipse((240, 660, 840, 1260), fill=FUNDO)
        if isinstance(simbolo, int):
            triangulo(d, 540, 990, 190, destaque=simbolo)
        else:
            d.text((540, 960), simbolo, font=fonte(300, True), fill=cor, anchor="mm")
        saidas.append(_salvar(img, f"destaques/{nome}.png"))
    return saidas


def _slide(n: int, total: int, titulo: str, assinatura: str) -> tuple[Image.Image, ImageDraw.ImageDraw, int]:
    img = Image.new("RGB", (1080, A), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1080, 14), fill=ROXO)
    triangulo(d, 100, 92, 34)
    d.text((158, 70), "MEU REPRESENTANTE", font=fonte(30, True), fill=TINTA)
    d.text((1016, 72), f"{n}/{total}", font=fonte(28), fill=TINTA_2, anchor="ra")
    y = 190
    for ln in _quebrar(d, titulo, fonte(68, True), 952, 3):
        d.text((64, y), ln, font=fonte(68, True), fill=TINTA)
        y += 80
    d.line((64, A - 100, 1016, A - 100), fill=LINHA, width=3)
    d.text((64, A - 78), assinatura, font=fonte(28, True), fill=TINTA_2)
    d.text((1016, A - 78), "apartidário · com fontes", font=fonte(26), fill=TINTA_2, anchor="ra")
    return img, d, y + 40


def _texto(d, y: int, texto: str, tam=36, cor=TINTA, largura=952, x=64, negrito=False, max_linhas=8) -> int:
    for ln in _quebrar(d, texto, fonte(tam, negrito), largura, max_linhas):
        d.text((x, y), ln, font=fonte(tam, negrito), fill=cor)
        y += int(tam * 1.32)
    return y


def _itens(d, y: int, itens: list[tuple[str, str]], cor=ROXO, numerado=False) -> int:
    for i, (forte, resto) in enumerate(itens, 1):
        if numerado:
            d.ellipse((64, y, 116, y + 52), fill=cor)
            d.text((90, y + 26), str(i), font=fonte(30, True), fill="white", anchor="mm")
        else:
            d.ellipse((72, y + 14, 98, y + 40), fill=cor)
        y2 = _texto(d, y, forte, 36, TINTA, 860, 140, True, 2)
        y = _texto(d, y2 + 2, resto, 32, TINTA_2, 860, 140, False, 3) + 26
    return y


def carrossel_lancamento(assinatura: str, data_2t: str, disputas: list[str]) -> list[Path]:
    total, saidas = 6, []

    img, d, y = _slide(1, total, "Quem vai decidir o futuro do país?", assinatura)
    _texto(d, y, "Conheça o Meu Representante: um dossiê aberto e apartidário sobre candidatos e eleitos de 2026.", 40, TINTA_2)
    triangulo(d, 540, 900 + DY, 210)
    d.text((1016, 1200 + 2 * DY), "arraste →", font=fonte(32, True), fill=ROXO, anchor="ra")
    saidas.append(_salvar(img, "lancamento/01-capa.png"))

    img, d, y = _slide(2, total, "Tudo sobre quem nos representa, num só lugar", assinatura)
    _itens(d, y + 20, [
        ("Propostas", "Resumo fiel do plano de governo registrado no TSE, com a página de origem."),
        ("Trajetória", "Cargos ocupados, leis e realizações verificáveis."),
        ("Conduta", "Processos e controvérsias, sempre com a situação de cada caso."),
        ("Dados oficiais", "Votos, patrimônio declarado e chapa, direto do TSE."),
    ])
    saidas.append(_salvar(img, "lancamento/02-o-que-e.png"))

    img, d, y = _slide(3, total, "Três pilares decidem as leis e as políticas públicas", assinatura)
    triangulo(d, 540, 860 + DY, 220)
    d.text((540, 450 + DY), "Executivo", font=fonte(40, True), fill=TINTA, anchor="ma")
    d.text((540, 498 + DY), "Presidência e governos estaduais", font=fonte(28), fill=TINTA_2, anchor="ma")
    for x, nome, desc, anc in [(64, "Senado", "Senadores dos 27 estados", "la"),
                               (1016, "Câmaras", "Deputados federais e estaduais", "ra")]:
        d.text((x, 1068 + DY), nome, font=fonte(40, True), fill=TINTA, anchor=anc)
        d.text((x, 1116 + DY), desc, font=fonte(28), fill=TINTA_2, anchor=anc)
    _texto(d, 1180 + 2 * DY, "Navegue por pilar, por estado ou pelo nome do candidato.", 32, TINTA_2)
    saidas.append(_salvar(img, "lancamento/03-tres-pilares.png"))

    img, d, y = _slide(4, total, "Como garantimos a confiança", assinatura)
    _itens(d, y + 10, [
        ("Nenhuma informação sem fonte", "Cada afirmação tem link para conferir."),
        ("Fontes oficiais em primeiro lugar", "Sem elas, pelo menos duas fontes jornalísticas independentes."),
        ("Investigação não é condenação", "Informamos a situação de cada processo: investigado, réu, condenado, absolvido."),
        ("O mesmo critério para todos", "Qualquer partido, qualquer posição política."),
        ("Revisão humana antes de publicar", "Processos em andamento passam por revisão jurídica."),
    ], numerado=True)
    saidas.append(_salvar(img, "lancamento/04-confianca.png"))

    img, d, y = _slide(5, total, f"2º turno · {data_2t}", assinatura)
    y = _texto(d, y, "Compare os candidatos lado a lado: propostas por tema, trajetória, conduta e dados oficiais.", 38, TINTA_2)
    y += 40
    caixa = 300
    for i, nome in enumerate(disputas):
        col, lin = i % 3, i // 3
        x0, y0 = 64 + col * (caixa + 26), y + lin * 130
        d.rounded_rectangle((x0, y0, x0 + caixa, y0 + 104), 18, fill=(255, 255, 255), outline=LINHA, width=3)
        d.text((x0 + caixa // 2, y0 + 52), nome, font=fonte(34, True), fill=ROXO if i == 0 else TINTA, anchor="mm")
    saidas.append(_salvar(img, "lancamento/05-segundo-turno.png"))

    img, d, y = _slide(6, total, "Este projeto é aberto. Colabore!", assinatura)
    _itens(d, y + 10, [
        ("Tem uma informação com fonte?", "Envie pelo site: ela passa por checagem e revisão antes de publicar."),
        ("É da área jurídica ou do jornalismo?", "Seja revisor(a) e ajude a conferir os dossiês."),
        ("Viu algo errado?", "Peça correção: candidatos e assessorias também podem pedir."),
    ])
    d.rounded_rectangle((64, 1060 + 2 * DY, 1016, 1180 + 2 * DY), 24, fill=ROXO)
    d.text((540, 1120 + 2 * DY), "Link na bio · compartilhe", font=fonte(44, True), fill="white", anchor="mm")
    saidas.append(_salvar(img, "lancamento/06-colabore.png"))
    return saidas


COR_PODER = {"camara": CORES[2], "senado": CORES[1], "congresso": CORES[1], "executivo": CORES[0]}


def _clarear(cor, f=0.7):
    return tuple(int(c + (b - c) * f) for c, b in zip(cor, FUNDO))


def _percurso(d: ImageDraw.ImageDraw, y: int, etapas: list[dict]) -> int:
    """Linha de estações (mesma lógica do site): ✓ feita, anel na atual, tracejada a futura."""
    n = len(etapas)
    xs = [130 + i * (820 // (n - 1)) for i in range(n)]
    r = 36
    for i in range(n - 1):  # trilhos
        cor = COR_PODER.get(etapas[i + 1]["poder"], TINTA_2)
        if etapas[i + 1]["estado"] == "futura":
            for x in range(xs[i] + r, xs[i + 1] - r, 16):
                d.line((x, y, min(x + 8, xs[i + 1] - r), y), fill=LINHA, width=6)
        else:
            d.line((xs[i], y, xs[i + 1], y), fill=cor, width=6)
    for x, e in zip(xs, etapas):
        cor = COR_PODER.get(e["poder"], TINTA_2)
        if e["estado"] == "atual":
            d.ellipse((x - r - 14, y - r - 14, x + r + 14, y + r + 14), fill=_clarear(cor, 0.65))
        if e["estado"] == "futura":
            d.ellipse((x - r, y - r, x + r, y + r), fill=FUNDO)
            for a in range(0, 360, 30):
                d.arc((x - r, y - r, x + r, y + r), a, a + 16, fill=cor, width=5)
        else:
            d.ellipse((x - r, y - r, x + r, y + r), fill=cor)
        if e["estado"] == "feita":  # visto desenhado: a fonte do sistema pode não ter o glifo ✓
            d.line((x - 14, y + 1, x - 4, y + 12, x + 15, y - 11), fill="white", width=7, joint="curve")
        else:
            d.text((x, y), str(etapas.index(e) + 1), font=fonte(32, True),
                   fill="white" if e["estado"] != "futura" else cor, anchor="mm")
        nome = e["nome"].replace(" · ", "\n")
        d.multiline_text((x, y + r + 24), nome, font=fonte(25, True), fill=TINTA if e["estado"] != "futura" else TINTA_2,
                         anchor="ma", align="center", spacing=4)
        casa = e["casa_nome"] + (" · agora" if e["estado"] == "atual" else "")
        yc = y + r + 24 + (64 if "\n" in nome else 34)
        d.text((x, yc), casa, font=fonte(23, e["estado"] == "atual"), fill=cor if e["estado"] == "atual" else TINTA_2, anchor="ma")
        votos = sorted((v["placar"] for v in e["eventos"] if v.get("placar")), key=lambda v: v["turno"] != "primeiro")
        for k, v in enumerate(votos):
            d.text((x, yc + 34 + 28 * k), f"{v['sim']} a {v['nao']}", font=fonte(23, True), fill=(22, 101, 52), anchor="ma")
    return y + r + 160


def _data_br(iso: str) -> str:
    return "/".join(reversed(iso[:10].split("-"))) if iso else ""


def carrossel_pautas(assinatura: str, ids: list[str], data_ref: str) -> list[Path]:
    """Carrossel 'onde está cada proposta': capa, um slide por pauta (mesmo layout) e como uma PEC vira regra."""
    import json
    pautas = [json.loads((config.SAIDA / "dados" / "pauta" / f"{i}.json").read_text(encoding="utf-8")) for i in ids]
    total, saidas, pasta = len(pautas) + 2, [], f"pautas/{'_'.join(ids)}"

    img, d, y = _slide(1, total, "Jornada de trabalho: duas propostas no Senado", assinatura)
    y = _texto(d, y, f"O que cada uma muda e em que etapa está em {data_ref}, com dados oficiais da Câmara e do Senado.",
               40, TINTA_2)
    y += 50
    for p in pautas:
        d.rounded_rectangle((64, y, 1016, y + 190), 24, fill=(255, 255, 255), outline=LINHA, width=3)
        d.text((100, y + 32), p["identificacao"].upper(), font=fonte(28, True), fill=ROXO)
        _texto(d, y + 76, p["titulo"], 44, TINTA, 880, 100, True, 2)
        y += 220
    _texto(d, y + 20, "As duas tramitam ao mesmo tempo e são apresentadas por defensores e críticos como alternativas.",
           32, TINTA_2)
    d.text((1016, A - 160), "arraste →", font=fonte(32, True), fill=ROXO, anchor="ra")
    saidas.append(_salvar(img, f"{pasta}/01-capa.png"))

    for n, p in enumerate(pautas, 2):
        img, d, y = _slide(n, total, p["titulo"], assinatura)
        casa = p["casa_iniciadora"]
        d.text((64, y - 4), f"{p['identificacao']} · começou {'na' if casa == 'Câmara' else 'no'} {casa}".upper(),
               font=fonte(26, True), fill=TINTA_2)
        y += 60
        d.text((64, y), "O QUE MUDA", font=fonte(28, True), fill=ROXO)
        y += 46
        for ponto in p.get("pontos") or []:
            d.ellipse((70, y + 14, 88, y + 32), fill=ROXO)
            y = _texto(d, y, ponto, 34, TINTA, 900, 110, False, 2) + 10
        y += 26
        # caixa "onde está agora"
        d.rounded_rectangle((64, y, 1016, y + 170), 20, fill=(255, 237, 213))
        d.rectangle((64, y, 76, y + 170), fill=(154, 52, 18))
        d.text((104, y + 24), "ONDE ESTÁ AGORA", font=fonte(24, True), fill=(154, 52, 18))
        _texto(d, y + 60, p["situacao"], 38, TINTA, 880, 104, True, 1)
        _texto(d, y + 112, f"{p['local']} · desde {_data_br(p['desde'])}", 26, TINTA_2, 880, 104, False, 1)
        y += 214
        d.text((64, y), "O PERCURSO", font=fonte(28, True), fill=ROXO)
        _percurso(d, y + 100, p["etapas"])
        d.text((64, A - 140), f"Situação em {data_ref}. Fonte: dados abertos da Câmara e do Senado.",
               font=fonte(24), fill=TINTA_2)
        saidas.append(_salvar(img, f"{pasta}/{n:02d}-{p['id']}.png"))

    img, d, y = _slide(total, total, "Como uma PEC vira regra", assinatura)
    _itens(d, y + 10, [
        ("Dois turnos em cada Casa", "Câmara e Senado votam duas vezes cada."),
        ("3/5 dos votos em cada turno", "308 dos 513 deputados e 49 dos 81 senadores."),
        ("Texto mudou? Volta", "A parte alterada retorna à outra Casa."),
        ("Sem sanção nem veto", "O Congresso promulga; a Presidência não participa."),
        ("E os projetos de lei?", "Basta maioria simples, e a Presidência pode sancionar ou vetar."),
    ], numerado=True)
    d.rounded_rectangle((64, A - 330, 1016, A - 190), 24, fill=ROXO)
    d.text((540, A - 288), "Acompanhe no site, atualizado sozinho", font=fonte(36, True), fill="white", anchor="mm")
    d.text((540, A - 234), "Link na bio · seção Pautas", font=fonte(30), fill="white", anchor="mm")
    saidas.append(_salvar(img, f"{pasta}/{total:02d}-como-funciona.png"))
    return saidas


def _salvar(img: Image.Image, nome: str) -> Path:
    destino = SAIDA / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, optimize=True)
    return destino


def gerar(assinatura: str, disputas: list[str]) -> list[Path]:
    return [foto_perfil(), *destaques(),
            *carrossel_lancamento(assinatura, config.DATA_SEGUNDO_TURNO_TXT.replace(" de 2026", ""), disputas)]
