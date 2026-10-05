# Meu Representante · Eleições 2026

Dossiê aberto, apartidário e com fontes sobre **quem disputa e quem foi eleito** em 2026:
Presidência, Governos estaduais, Senado, Câmara dos Deputados e Assembleias Legislativas.

> Quem decide o futuro do país precisa ser conhecido por quem o escolhe.

## O que o site mostra

Navegação pelos **três pilares**: **Executivo**, **Senado** e **Câmaras**. Também dá para navegar por **estado**
ou por **busca**. Cada candidatura tem:

| Seção | Origem | Atualização |
|---|---|---|
| Nome, partido, número, foto, chapa | [Dados Abertos do TSE](https://dadosabertos.tse.jus.br/) | automática |
| Votos, percentual e resultado (eleito / 2º turno) | [Totalização do TSE](https://resultados.tse.jus.br/) | automática |
| Patrimônio declarado, ocupação, instrução, idade | Dados Abertos do TSE | automática |
| **Propostas** (resumo + link do documento) | dossiê colaborativo | via pull request |
| **Trajetória e realizações** | dossiê colaborativo | via pull request |
| **Conduta, processos e controvérsias** (com situação processual) | dossiê colaborativo | via pull request |

**2º turno:** a página `#/2turno` lista as disputas e compara os dois candidatos lado a lado
(propostas por tema, trajetória, conduta e dados oficiais).

**Revisão:** só vai ao ar o que tem fonte oficial ou decisão encerrada, confirmado por duas fontes.
Processos em andamento aguardam revisão jurídica ([docs/REVISAO.md](docs/REVISAO.md)).

Toda afirmação dos dossiês tem fonte. As regras estão em [docs/METODOLOGIA.md](docs/METODOLOGIA.md) e são
**verificadas automaticamente** (`python MeuRepresentante.py validar`).

## Rodando no seu computador

Requisitos: Python 3.10+.

```bash
pip install -r requirements.txt
python MeuRepresentante.py tudo      # baixa os dados do TSE, valida os dossiês e gera ./site
python MeuRepresentante.py servir    # abre em http://localhost:8000
```

Outros comandos:

```bash
python MeuRepresentante.py buscar "nome"            # descobre o id (SQ_CANDIDATO) de um candidato
python MeuRepresentante.py novo-dossie 250002544912 # cria dados/dossies/SP/250002544912.yaml
python MeuRepresentante.py validar                  # confere as regras editoriais
python MeuRepresentante.py verificar-links          # confere se as fontes respondem
python MeuRepresentante.py relatorio                # PDF para revisão jurídica (não publicar)
python MeuRepresentante.py cards --uf SP            # gera imagens 1080x1350 para Instagram em ./cards
python MeuRepresentante.py cards --cargo PRESIDENTE --todos
python MeuRepresentante.py cards --segundo-turno         # um card "A x B" por disputa de 2º turno
python MeuRepresentante.py cards --resultado segundo_turno --todos --site-url meurepresentante.org
```

O comando `importar` só baixa de novo se o TSE tiver atualizado os arquivos. Rode `tudo` periodicamente
para pegar os resultados oficiais assim que forem publicados.

## Estrutura

```
MeuRepresentante.py      linha de comando
meurep/
  config.py              URLs do TSE, pilares, cores, cargos
  tse.py                 importação dos dados abertos (descarta CPF, e-mail, título etc.)
  resultados.py          votos e situação a partir da totalização em tempo real do TSE
  dossies.py             leitura e validação dos dossiês (regras editoriais)
  site.py                gera o site estático (HTML + JSON)
  cards.py               gera imagens para redes sociais
web/                     HTML, CSS e JavaScript do site (sem dependências externas)
dados/
  dossies/<UF>/<id>.yaml um arquivo por candidato (conteúdo curado)
  dossies/_modelo.yaml   modelo comentado
  resultados.yaml        resultados manuais (com fonte) enquanto o TSE não publica
docs/METODOLOGIA.md      regras editoriais e jurídicas
```

## Publicação

O workflow [.github/workflows/site.yml](.github/workflows/site.yml) gera e publica o site no **GitHub Pages**
a cada push na `main` e a cada 3 horas, já com os dados mais recentes do TSE. No GitHub, ative em
*Settings → Pages → Source: GitHub Actions*. Depois preencha `REPO_URL` em [meurep/config.py](meurep/config.py)
para habilitar os links de correção e contribuição.

## Como contribuir

Leia o [CONTRIBUTING.md](CONTRIBUTING.md). Há trabalho para todos os perfis: pesquisa e checagem de
dossiês, revisão jurídica, design, programação e divulgação.

## Licenças

- Código: [MIT](LICENSE).
- Conteúdo dos dossiês (`dados/dossies`): [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.pt_BR).
- Dados do TSE: dados abertos públicos, com atribuição ao Tribunal Superior Eleitoral.
