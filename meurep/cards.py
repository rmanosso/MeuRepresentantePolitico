"""Gera cards (PNG 1080x1350, formato retrato do Instagram) a partir dos dados do site."""
import io
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

from . import config

L, A = 1080, 1350
MARGEM = 64
FUNDO = (250, 249, 246)
TINTA = (28, 27, 34)
TINTA_2 = (85, 82, 94)
LINHA = (227, 224, 218)

ROTULO_RESULTADO = {
    "eleito": ("ELEITO(A)", (22, 101, 52), (220, 252, 231)),
    "segundo_turno": ("2º TURNO", (154, 52, 18), (255, 237, 213)),
    "suplente": ("SUPLENTE", TINTA_2, (236, 235, 232)),
    "nao_eleito": ("NÃO ELEITO(A)", TINTA_2, (236, 235, 232)),
    "aguardando": ("AGUARDANDO RESULTADO", TINTA_2, (236, 235, 232)),
}
SITUACAO_CURTA = {
    "investigado": "investigação em andamento", "denunciado": "denunciado, sem julgamento",
    "reu": "réu, sem julgamento", "condenado_1a_instancia": "condenado em 1ª instância, cabe recurso",
    "condenado_2a_instancia": "condenado em 2ª instância, cabe recurso",
    "condenado_definitivo": "condenação definitiva", "absolvido": "absolvido", "arquivado": "arquivado",
    "prescrito": "prescrito", "anulado": "condenação anulada", "inelegivel": "inelegível",
}
CARGO_TXT = {
    "PRESIDENTE": "Presidente", "GOVERNADOR": "Governador(a)", "SENADOR": "Senador(a)",
    "DEPUTADO FEDERAL": "Deputado(a) Federal", "DEPUTADO ESTADUAL": "Deputado(a) Estadual",
    "DEPUTADO DISTRITAL": "Deputado(a) Distrital",
}

_FONTES = {
    False: ["segoeui.ttf", "DejaVuSans.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"],
    True: ["segoeuib.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf"],
}
_PASTAS = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu"),
           Path("/usr/share/fonts/truetype/liberation"), Path("/Library/Fonts"), Path("/System/Library/Fonts/Supplemental")]


def fonte(tamanho: int, negrito: bool = False):
    for nome in _FONTES[negrito]:
        for pasta in _PASTAS:
            if (pasta / nome).exists():
                return ImageFont.truetype(str(pasta / nome), tamanho)
    return ImageFont.load_default(tamanho)


def _hex(cor: str) -> tuple[int, int, int]:
    cor = cor.lstrip("#")
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))


def _foto(c: dict) -> Image.Image | None:
    pasta = config.CACHE / "fotos"
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / f"{c['id']}.jpeg"
    if not arq.exists():
        try:
            r = requests.get(c["foto"], timeout=30)
            r.raise_for_status()
            arq.write_bytes(r.content)
        except requests.RequestException:
            return None
    try:
        return Image.open(io.BytesIO(arq.read_bytes())).convert("RGB")
    except OSError:
        return None


def _quebrar(draw, texto: str, f, largura: int, max_linhas: int) -> list[str]:
    """Quebra o texto em linhas que cabem na largura, com reticências se exceder."""
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = f"{atual} {p}".strip()
        if draw.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    if len(linhas) > max_linhas:
        linhas = linhas[:max_linhas]
        while draw.textlength(linhas[-1] + "…", font=f) > largura:
            linhas[-1] = linhas[-1].rsplit(" ", 1)[0]
        linhas[-1] += "…"
    return linhas


def _bloco(draw, y: int, titulo: str, itens: list[str], cor, max_itens=3, linhas_item=2) -> int:
    draw.text((MARGEM, y), titulo, font=fonte(30, True), fill=cor)
    y += 46
    f = fonte(30)
    for item in itens[:max_itens]:
        linhas = _quebrar(draw, item, f, L - 2 * MARGEM - 34, linhas_item)
        draw.ellipse((MARGEM + 2, y + 13, MARGEM + 14, y + 25), fill=cor)
        for ln in linhas:
            draw.text((MARGEM + 34, y), ln, font=f, fill=TINTA)
            y += 40
        y += 10
    return y + 14


def card(c: dict, destino: Path, site_url: str = "") -> Path:
    pilar = config.PILARES[c["pilar"]]
    cor = _hex(pilar["cor"])
    img = Image.new("RGB", (L, A), FUNDO)
    d = ImageDraw.Draw(img)

    # faixa superior
    d.rectangle((0, 0, L, 120), fill=cor)
    d.text((MARGEM, 34), "MEU REPRESENTANTE", font=fonte(38, True), fill="white")
    d.text((L - MARGEM, 40), f"ELEIÇÕES {config.ANO}", font=fonte(32), fill="white", anchor="ra")

    # foto + identificação
    y0 = 170
    foto = _foto(c)
    fw, fh = 300, 400
    if foto:
        foto = ImageOps.fit(foto, (fw, fh), Image.LANCZOS, centering=(0.5, 0.3))
        mascara = Image.new("L", (fw, fh), 0)
        ImageDraw.Draw(mascara).rounded_rectangle((0, 0, fw, fh), 24, fill=255)
        img.paste(foto, (MARGEM, y0), mascara)
    else:
        d.rounded_rectangle((MARGEM, y0, MARGEM + fw, y0 + fh), 24, fill=LINHA)

    x = MARGEM + fw + 40
    larg = L - x - MARGEM
    local = config.UFS.get(c["uf"], "Brasil")
    d.text((x, y0), f"{CARGO_TXT.get(c['cargo'], c['cargo']).upper()}", font=fonte(28, True), fill=cor)
    d.text((x, y0 + 38), local, font=fonte(28), fill=TINTA_2)
    y = y0 + 100
    for ln in _quebrar(d, c["nome_urna"], fonte(60, True), larg, 3):
        d.text((x, y), ln, font=fonte(60, True), fill=TINTA)
        y += 70
    d.text((x, y + 6), f"{c['partido']} · nº {c['numero']}", font=fonte(34), fill=TINTA_2)
    rot, cor_txt, cor_fundo = ROTULO_RESULTADO.get(c["resultado"], ROTULO_RESULTADO["aguardando"])
    fb = fonte(28, True)
    w = d.textlength(rot, font=fb)
    d.rounded_rectangle((x, y + 66, x + w + 36, y + 114), 24, fill=cor_fundo)
    d.text((x + 18, y + 74), rot, font=fb, fill=cor_txt)

    # conteúdo do dossiê
    y = y0 + fh + 50
    d.line((MARGEM, y - 20, L - MARGEM, y - 20), fill=LINHA, width=3)
    dossie = c.get("dossie")
    if dossie:
        # A conduta sempre aparece: o espaço das outras seções é limitado para garantir isso.
        if dossie["propostas"]:
            y = _bloco(d, y, "PROPOSTAS", [p["resumo"] for p in dossie["propostas"]], cor, max_itens=2)
        if dossie["trajetoria"]:
            y = _bloco(d, y, "TRAJETÓRIA",
                       [f"{t['ano']}: {t['titulo']}" if t.get("ano") else t["titulo"] for t in dossie["trajetoria"]],
                       cor, max_itens=1, linhas_item=1)
        conduta = dossie["conduta"]
        itens = ([f"{k['titulo']} ({SITUACAO_CURTA.get(k['situacao'], k['situacao_texto'])})" for k in conduta]
                 or [f"Nenhum registro publicado até {dossie['atualizado_em']}"])
        if len(conduta) > 2:
            itens[1] = f"{itens[1]} · e mais {len(conduta) - 2} no site"
        _bloco(d, y, f"CONDUTA E PROCESSOS ({len(conduta)})", itens, cor, max_itens=2, linhas_item=2)
    else:
        f = fonte(32)
        texto = ("Dossiê em construção. Ficha oficial, patrimônio declarado e, em breve, "
                 "propostas, trajetória e conduta com fontes verificáveis.")
        for ln in _quebrar(d, texto, f, L - 2 * MARGEM, 4):
            d.text((MARGEM, y), ln, font=f, fill=TINTA_2)
            y += 46
        if c.get("bens_declarados") is not None:
            v = f"R$ {c['bens_declarados']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            d.text((MARGEM, y + 20), "PATRIMÔNIO DECLARADO AO TSE", font=fonte(28, True), fill=cor)
            d.text((MARGEM, y + 60), v, font=fonte(48, True), fill=TINTA)

    # rodapé
    d.rectangle((0, A - 110, L, A), fill=(236, 235, 232))
    d.text((MARGEM, A - 88), "Fontes: TSE e referências citadas no site. Investigação não é condenação.",
           font=fonte(24), fill=TINTA_2)
    d.text((MARGEM, A - 52), site_url or "Projeto cidadão e apartidário", font=fonte(28, True), fill=TINTA)

    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, optimize=True)
    return destino


def gerar(candidatos: list[dict], site_url: str = "") -> list[Path]:
    saidas = []
    for c in candidatos:
        nome = f"{c['uf']}_{c['cargo'].replace(' ', '-').lower()}_{c['partido']}_{c['id']}.png"
        saidas.append(card(c, config.CARDS / c["uf"] / nome, site_url))
    return saidas


TEMAS_PRIORITARIOS = ["Segurança pública", "Economia e impostos", "Saúde", "Educação",
                      "Trabalho e emprego", "Assistência social", "Meio ambiente", "Moradia"]


def _foto_colada(img, c, x, y, w, h):
    foto = _foto(c)
    if foto:
        foto = ImageOps.fit(foto, (w, h), Image.LANCZOS, centering=(0.5, 0.3))
        mascara = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mascara).rounded_rectangle((0, 0, w, h), 22, fill=255)
        img.paste(foto, (x, y), mascara)
    else:
        ImageDraw.Draw(img).rounded_rectangle((x, y, x + w, y + h), 22, fill=LINHA)


def card_comparacao(a: dict, b: dict, destino: Path, site_url: str = "", data_2t: str = "") -> Path:
    """Card 'A x B' do 2º turno: votação do 1º turno e propostas lado a lado nos temas em comum."""
    cor = _hex(config.PILARES[a["pilar"]]["cor"])
    img = Image.new("RGB", (L, A), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, L, 110), fill=cor)
    d.text((MARGEM, 32), "MEU REPRESENTANTE", font=fonte(36, True), fill="white")
    d.text((L - MARGEM, 38), f"2º TURNO · {data_2t}".upper(), font=fonte(28), fill="white", anchor="ra")
    local = "BRASIL" if a["uf"] == "BR" else config.UFS.get(a["uf"], a["uf"]).upper()
    d.text((L // 2, 140), f"{CARGO_TXT.get(a['cargo'], a['cargo']).upper()} · {local}",
           font=fonte(30, True), fill=cor, anchor="ma")

    col = (L - 2 * MARGEM - 40) // 2
    xs = [MARGEM, MARGEM + col + 40]
    fw, fh = 220, 290
    for c, x in zip((a, b), xs):
        cx = x + col // 2
        _foto_colada(img, c, cx - fw // 2, 195, fw, fh)
        y = 500
        for ln in _quebrar(d, c["nome_urna"], fonte(42, True), col, 2):
            d.text((cx, y), ln, font=fonte(42, True), fill=TINTA, anchor="ma")
            y += 50
        d.text((cx, y + 2), f"{c['partido']} · nº {c['numero']}", font=fonte(28), fill=TINTA_2, anchor="ma")
        if c.get("percentual") is not None:
            pct = f"{c['percentual']:.2f}%".replace(".", ",")
            d.text((cx, y + 44), pct, font=fonte(48, True), fill=TINTA, anchor="ma")
            d.text((cx, y + 102), "no 1º turno", font=fonte(22), fill=TINTA_2, anchor="ma")
    d.text((L // 2, 330), "x", font=fonte(54, True), fill=TINTA_2, anchor="mm")

    y = 735
    d.line((MARGEM, y, L - MARGEM, y), fill=LINHA, width=3)
    y += 22
    props = [{p["tema"]: [] for p in (c.get("dossie") or {}).get("propostas", [])} for c in (a, b)]
    for i, c in enumerate((a, b)):
        for p in (c.get("dossie") or {}).get("propostas", []):
            props[i][p["tema"]].append(p["resumo"])
    comuns = [t for t in TEMAS_PRIORITARIOS if t in props[0] and t in props[1]]
    if comuns:
        f = fonte(24)
        for tema in comuns:
            if y > A - 260:
                break
            d.text((L // 2, y), tema.upper(), font=fonte(24, True), fill=cor, anchor="ma")
            y += 36
            alturas = []
            for i, x in enumerate(xs):
                yy = y
                for ln in _quebrar(d, props[i][tema][0], f, col, 5):
                    d.text((x, yy), ln, font=f, fill=TINTA)
                    yy += 31
                alturas.append(yy)
            y = max(alturas) + 22
    else:
        texto = "Dossiês em construção. Veja no site a ficha oficial, o patrimônio declarado e as fontes."
        for ln in _quebrar(d, texto, fonte(30), L - 2 * MARGEM, 3):
            d.text((MARGEM, y), ln, font=fonte(30), fill=TINTA_2)
            y += 42

    d.rectangle((0, A - 120, L, A), fill=(236, 235, 232))
    d.text((MARGEM, A - 100), "Resumo dos planos de governo registrados no TSE. Trajetória, conduta",
           font=fonte(23), fill=TINTA_2)
    d.text((MARGEM, A - 72), "e todas as fontes no site. Investigação não é condenação.", font=fonte(23), fill=TINTA_2)
    d.text((L - MARGEM, A - 72), site_url, font=fonte(26, True), fill=TINTA, anchor="ra")
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, optimize=True)
    return destino


def gerar_segundo_turno(candidatos: list[dict], site_url: str = "") -> list[Path]:
    grupos: dict[tuple, list[dict]] = {}
    for c in candidatos:
        if c["resultado"] == "segundo_turno":
            grupos.setdefault((c["uf"], c["cargo"]), []).append(c)
    saidas = []
    for (uf, cargo), g in sorted(grupos.items(), key=lambda kv: (config.ORDEM_CARGOS.index(kv[0][1]), kv[0][0])):
        if len(g) < 2:
            continue
        a, b = sorted(g, key=lambda c: -(c.get("votos") or 0))[:2]
        nome = f"2turno_{uf}_{cargo.replace(' ', '-').lower()}.png"
        saidas.append(card_comparacao(a, b, config.CARDS / "2turno" / nome, site_url, config.DATA_SEGUNDO_TURNO_TXT))
    return saidas
