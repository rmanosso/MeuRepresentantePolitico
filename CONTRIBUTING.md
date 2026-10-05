# Como contribuir

Obrigado por ajudar! Antes de tudo, leia a [metodologia editorial](docs/METODOLOGIA.md):
**toda informação precisa de fonte, e a situação processual é sempre informada.**

## Montar ou melhorar um dossiê

1. Faça um *fork* do repositório e clone no seu computador.
2. Instale as dependências: `pip install -r requirements.txt`.
3. Encontre o id do candidato:
   ```bash
   python MeuRepresentante.py buscar "nome do candidato" --uf SP
   ```
4. Crie o arquivo do dossiê (já vem com o modelo comentado):
   ```bash
   python MeuRepresentante.py novo-dossie 250002544912
   ```
5. Preencha `dados/dossies/<UF>/<id>.yaml`: propostas, trajetória, conduta, cada item com `fontes`.
6. Valide e confira no navegador:
   ```bash
   python MeuRepresentante.py validar
   python MeuRepresentante.py site && python MeuRepresentante.py servir
   ```
7. Abra um *pull request* com o título `Dossiê: Nome (PARTIDO/UF)`. Na descrição, conte quais fontes
   consultou. Um segundo colaborador revisa antes do *merge*. Para itens de **conduta**, a revisão confere
   cada link.

Não tem familiaridade com git? Abra uma *issue* com o modelo **Sugestão de informação**, com os links,
e alguém transforma em dossiê.

## Revisar dossiês

Revisores credenciados conferem cada alteração antes de ela ir ao ar (duas aprovações por item;
para registros de conduta, uma delas da área jurídica). Peça credenciamento pela *issue*
**Quero ser revisor(a)**. O fluxo completo está em [docs/REVISAO.md](docs/REVISAO.md).

> Processos em andamento sem documento oficial não são publicados direto: passam antes pela
> revisão jurídica da coordenação.

## Pedir correção

Use a *issue* modelo **Correção** (há um link em cada página de candidato). Informe o que está errado e a
fonte correta.

## Código

- Python sem frameworks; o site é HTML/CSS/JS puro, sem *build*.
- Mantenha o site leve: ele precisa abrir bem em celulares simples e em conexão móvel.
- Ideias de evolução: integração com as APIs da [Câmara](https://dadosabertos.camara.leg.br/) e do
  [Senado](https://legis.senado.leg.br/dadosabertos/) (votações, presença, proposições), histórico de
  patrimônio entre eleições, comparação lado a lado de candidatos do 2º turno, carrosséis para Instagram,
  acessibilidade (leitores de tela, alto contraste), PWA para uso offline.
