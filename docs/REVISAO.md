# Fluxo de revisão (Etapa 1)

Guia para a coordenação do projeto. Nada vai ao site sem conferência humana; o que é automático é
a checagem de links e a publicação depois das aprovações.

## Critério de publicação

Publica-se o item com **fonte oficial ou decisão encerrada**, confirmado por **pelo menos duas fontes
independentes**. Processos em andamento sem documento oficial aguardam revisão jurídica.

| Onde fica | O que é | Vai ao site? | Está no GitHub? |
|---|---|---|---|
| `dados/dossies/` | itens `status: confirmado` (ou propostas/trajetória com fonte oficial) | sim | sim (público) |
| `dados/privado/` | itens `status: em_revisao` | **não** | **não** (fora do git) |

> A pasta `dados/privado/` existe apenas no computador da coordenação. Para mandar itens pendentes ao
> jurídico, use o PDF (`python MeuRepresentante.py relatorio`), que fica em `revisao/`, também fora do git.

## Passo a passo

1. **Sugestão chega** por *issue* (botão "Enviar" no site, modelo *Sugestão de informação*).
   O robô de triagem comenta em minutos: links que abrem, fonte oficial, duas fontes independentes.
2. **Triagem (coordenação):** recusar com motivo, pedir mais fontes ou transformar em rascunho.
   - Propostas, trajetória e fatos encerrados com fontes sólidas: abrir *pull request* em `dados/dossies/`.
   - Processos em andamento sem documento oficial: registrar em `dados/privado/` e incluir no próximo PDF.
3. **Revisão:** dois revisores credenciados aprovam o *pull request* usando o checklist. Para conduta,
   um deles é da área jurídica. O robô roda `validar` e `verificar-links`.
4. **Publicação automática:** com as aprovações, o *merge* dispara o site e a data de atualização.
5. **Parecer jurídico sobre pendentes:** quando aprovado, mover o item de `dados/privado/` para
   `dados/dossies/` com `status: confirmado` e a redação ajustada, num *pull request* normal.

## Configuração no GitHub (uma vez)

1. *Settings → Branches → Add rule* para `main`:
   - **Require a pull request before merging** → *Require approvals*: **2**.
   - **Require review from Code Owners** (ver `.github/CODEOWNERS`).
   - **Require status checks to pass** → marcar o job `gerar`.
   - **Do not allow bypassing the above settings**.
2. Criar uma organização (ex.: `meu-representante`) e a equipe **revisores**; trocar `@SEU_USUARIO`
   em `.github/CODEOWNERS` por `@meu-representante/revisores`.
3. Criar os rótulos `dossie`, `correcao`, `revisor` (os modelos de *issue* já os usam).
4. *Settings → Pages → Source: GitHub Actions* e preencher `REPO_URL` em `meurep/config.py`.

## Credenciamento de revisores

- Pedido pelo modelo *Quero ser revisor(a)*. A coordenação confere o vínculo informado
  (ex.: consulta pública ao Cadastro Nacional dos Advogados) e adiciona à equipe.
- Buscar equilíbrio: revisores de diferentes posições políticas; ninguém aprova o próprio texto.
- Remover da equipe quem violar a metodologia, registrando o motivo.

## Comandos úteis

```bash
python MeuRepresentante.py validar                 # regras editoriais (inclui itens privados)
python MeuRepresentante.py verificar-links --privados
python MeuRepresentante.py relatorio               # PDF para o jurídico em ./revisao
python MeuRepresentante.py triagem arquivo.txt     # testar a triagem de um texto com links
```
