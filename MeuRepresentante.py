"""Meu Representante — dossiê aberto sobre candidatos e eleitos (Eleições 2026).

Uso:
    python MeuRepresentante.py tudo              # importa TSE, valida dossiês e gera o site
    python MeuRepresentante.py importar          # baixa/atualiza os dados abertos do TSE
    python MeuRepresentante.py validar           # confere as regras editoriais dos dossiês
    python MeuRepresentante.py site              # gera o site em ./site (inclui as pautas de dados/pautas)
    python MeuRepresentante.py servir            # abre o site em http://localhost:8000
    python MeuRepresentante.py buscar "nome"     # encontra o id de um candidato
    python MeuRepresentante.py novo-dossie ID    # cria o arquivo de dossiê de um candidato
    python MeuRepresentante.py cards [filtros]   # gera imagens para Instagram em ./cards
    python MeuRepresentante.py relatorio         # PDF para revisão jurídica em ./revisao (não publicar)
    python MeuRepresentante.py cards --segundo-turno  # cards comparativos "A x B" do 2º turno
"""
import argparse
import functools
import http.server
import json
import sys
import unicodedata

from meurep import cards, config, dossies, instagram, links, pautas, relatorio, site, tse

BASE = config.CACHE / "base_tse.json"


def carregar_base(forcar_importacao=False) -> dict:
    if forcar_importacao or not BASE.exists():
        base = tse.importar(forcar=False)
        BASE.write_text(json.dumps(base, ensure_ascii=False), encoding="utf-8")
        return base
    return json.loads(BASE.read_text(encoding="utf-8"))


def validar() -> tuple[dict, dict]:
    dos, erros = dossies.carregar()
    _, erros_priv = dossies.carregar(incluir_privados=True)  # confere também os itens em conferência
    erros += [e for e in erros_priv if e not in erros]
    man, erros_man = dossies.carregar_resultados_manuais()
    erros += erros_man
    if erros:
        print("Problemas encontrados:")
        for e in erros:
            print("  ✗", e)
        sys.exit(1)
    print(f"Dossiês OK: {len(dos)} arquivo(s), {len(man)} resultado(s) manual(is).")
    return dos, man


def montar() -> tuple[list[dict], dict]:
    base = carregar_base()
    dos, man = validar()
    ids = {c["id"] for c in base["candidatos"]}
    for i in set(dos) - ids:
        print(f"  ! dossiê com id {i} não corresponde a nenhuma candidatura titular do TSE")
    return site.montar(base, dos, man), base


def _norm(s: str) -> str:
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()


def cmd_buscar(args):
    termo = _norm(args.termo)
    achados = [c for c in carregar_base()["candidatos"]
               if termo in _norm(f"{c['nome_urna']} {c['nome']}") and (not args.uf or c["uf"] == args.uf.upper())]
    for c in achados[:50]:
        print(f"{c['id']}  {c['uf']}  {c['cargo']:<18} {c['partido']:<14} {c['nome_urna']} ({c['nome']})")
    print(f"{len(achados)} resultado(s)")


def cmd_novo_dossie(args):
    base = carregar_base()
    c = next((x for x in base["candidatos"] if x["id"] == args.id), None)
    if not c:
        sys.exit(f"Candidato {args.id} não encontrado. Use: python MeuRepresentante.py buscar \"nome\"")
    destino = config.DOSSIES / c["uf"] / f"{c['id']}.yaml"
    if destino.exists():
        sys.exit(f"Já existe: {destino}")
    modelo = (config.DOSSIES / "_modelo.yaml").read_text(encoding="utf-8")
    cabecalho = (f"# {c['nome_urna']} ({c['nome']}) — {c['cargo']} / {c['uf']} — {c['partido']} nº {c['numero']}\n"
                 f"# Ficha oficial: {c['tse_url']}\n")
    corpo = modelo.split("# --- início ---\n", 1)[1].replace("ID_DO_TSE", c["id"])
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(cabecalho + corpo, encoding="utf-8")
    print(f"Criado: {destino.relative_to(config.RAIZ)}")


def cmd_cards(args):
    candidatos, _ = montar()
    if args.segundo_turno:
        for p in cards.gerar_segundo_turno(candidatos, args.site_url):
            print(" ", p.relative_to(config.RAIZ))
        return
    sel = [c for c in candidatos
           if (not args.uf or c["uf"] == args.uf.upper())
           and (not args.cargo or c["cargo"] == args.cargo.upper())
           and (not args.resultado or c["resultado"] == args.resultado)
           and (not args.id or c["id"] in args.id)
           and (args.todos or args.id or "dossie" in c)]
    if not sel:
        sys.exit("Nenhum candidato selecionado. Por padrão só entram candidatos com dossiê; use --todos ou --id.")
    if len(sel) > 300 and not args.sim:
        sys.exit(f"{len(sel)} cards seriam gerados (baixando as fotos). Refine os filtros ou use --sim.")
    for p in cards.gerar(sel, args.site_url):
        print(" ", p.relative_to(config.RAIZ))


def cmd_relatorio(args):
    base = carregar_base()
    validar()
    dos, _ = dossies.carregar(incluir_privados=True)
    man, _ = dossies.carregar_resultados_manuais()
    candidatos = [c for c in site.montar(base, {}, man) if c["id"] in dos]
    print("Relatório gerado:", relatorio.gerar(candidatos, dos).relative_to(config.RAIZ))


def cmd_verificar_links(args):
    dos, _ = dossies.carregar(incluir_privados=args.privados)
    urls = [f["url"] for d in dos.values() for sec in ("propostas", "trajetoria", "conduta")
            for item in d[sec] for f in item["fontes"]]
    res = links.verificar_varios(urls)
    erros = {u: r for u, r in res.items() if r[0] == "erro"}
    for u, (sit, det) in sorted(res.items(), key=lambda kv: kv[1][0]):
        if sit != "ok":
            print(f"  {'✗' if sit == 'erro' else '?'} {det}: {u}")
    print(f"{len(res)} link(s): {len(res) - len(erros)} ok ou conferência manual, {len(erros)} com erro.")
    if erros:
        sys.exit(1)


def cmd_triagem(args):
    texto = sys.stdin.read() if args.arquivo == "-" else open(args.arquivo, encoding="utf-8").read()
    print(links.triagem(texto))


def cmd_instagram(args):
    candidatos, _ = montar()
    disputas = sorted({(c["uf"], c["cargo"]) for c in candidatos if c["resultado"] == "segundo_turno"},
                      key=lambda d: (config.ORDEM_CARGOS.index(d[1]), d[0]))
    rotulos = ["Presidência" if uf == "BR" else f"Governo {uf}" for uf, _ in disputas]
    for p in instagram.gerar(args.assinatura, rotulos):
        print(" ", p.relative_to(config.RAIZ))


def cmd_servir(args):
    if not config.SAIDA.exists():
        sys.exit("Gere o site antes: python MeuRepresentante.py site")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(config.SAIDA))
    print(f"Servindo em http://localhost:{args.porta} (Ctrl+C para parar)")
    http.server.ThreadingHTTPServer(("localhost", args.porta), handler).serve_forever()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Meu Representante — Eleições 2026")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("importar", help="baixa/atualiza os dados do TSE")
    sub.add_parser("validar", help="valida os dossiês")
    sub.add_parser("site", help="gera o site estático")
    sub.add_parser("tudo", help="importar + validar + site")
    sub.add_parser("relatorio", help="PDF para revisão jurídica (inclui itens não publicados)")
    p = sub.add_parser("instagram", help="kit do Instagram: foto de perfil, destaques e carrossel de lançamento")
    p.add_argument("--assinatura", default=config.INSTAGRAM, help="arroba ou site exibido no rodapé")
    p = sub.add_parser("verificar-links", help="confere se as fontes dos dossiês respondem")
    p.add_argument("--privados", action="store_true", help="inclui os itens em conferência")
    p = sub.add_parser("triagem", help="checagem automática de uma sugestão (texto com links)")
    p.add_argument("arquivo", help="arquivo de texto, ou - para ler da entrada padrão")
    p = sub.add_parser("servir", help="servidor local para ver o site")
    p.add_argument("--porta", type=int, default=8000)
    p = sub.add_parser("buscar", help="procura candidatos pelo nome")
    p.add_argument("termo")
    p.add_argument("--uf")
    p = sub.add_parser("novo-dossie", help="cria o YAML de dossiê para um candidato")
    p.add_argument("id", help="SQ_CANDIDATO do TSE (veja o comando buscar)")
    p = sub.add_parser("cards", help="gera imagens para redes sociais")
    p.add_argument("--uf")
    p.add_argument("--cargo", help='ex.: "SENADOR"')
    p.add_argument("--resultado", choices=["eleito", "segundo_turno", "aguardando", "nao_eleito", "suplente"])
    p.add_argument("--id", nargs="*")
    p.add_argument("--todos", action="store_true", help="inclui candidatos sem dossiê")
    p.add_argument("--segundo-turno", action="store_true", help="um card comparativo por disputa de 2º turno")
    p.add_argument("--sim", action="store_true", help="confirma geração de muitos cards")
    p.add_argument("--site-url", default=config.INSTAGRAM, help="endereço exibido no rodapé do card")
    args = ap.parse_args()

    if args.cmd == "importar":
        carregar_base(forcar_importacao=True)
    elif args.cmd == "validar":
        validar()
    elif args.cmd in ("site", "tudo"):
        if args.cmd == "tudo":
            carregar_base(forcar_importacao=True)
        candidatos, base = montar()
        site.gerar(candidatos, base["gerado_em"])
        pautas.gerar(config.SAIDA / "dados")
    elif args.cmd == "servir":
        cmd_servir(args)
    elif args.cmd == "buscar":
        cmd_buscar(args)
    elif args.cmd == "novo-dossie":
        cmd_novo_dossie(args)
    elif args.cmd == "cards":
        cmd_cards(args)
    elif args.cmd == "relatorio":
        cmd_relatorio(args)
    elif args.cmd == "verificar-links":
        cmd_verificar_links(args)
    elif args.cmd == "instagram":
        cmd_instagram(args)
    elif args.cmd == "triagem":
        cmd_triagem(args)


if __name__ == "__main__":
    main()
