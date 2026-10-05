# Metodologia editorial

O projeto só tem valor se for **confiável para qualquer eleitor, de qualquer posição política**.
Por isso as regras abaixo valem igualmente para todos os candidatos e são, sempre que possível,
verificadas por código (`meurep/dossies.py`).

## 1. Fontes

1. **Nenhuma afirmação sem fonte.** Cada proposta, item de trajetória ou registro de conduta precisa de
   pelo menos um link `https://`. *(verificado automaticamente)*
2. **Hierarquia de fontes**, da mais para a menos preferida:
   1. Documentos oficiais: TSE (DivulgaCandContas, planos de governo), tribunais (`.jus.br`),
      Ministério Público (`.mp.br`), Câmara, Senado e Assembleias (`.leg.br`), órgãos públicos (`.gov.br`),
      Tribunais de Contas, Diário Oficial.
   2. Veículos jornalísticos com política de correção pública.
   3. Canais oficiais do próprio candidato (site, redes): apenas para **propostas** e **posicionamentos**.
3. **Conduta sem fonte oficial exige ao menos duas fontes jornalísticas independentes.** *(verificado)*
4. Não são aceitos: blogs anônimos, correntes de WhatsApp, vídeos cortados, perfis sem identificação,
   sites de checagem como única fonte para o fato em si (use-os para chegar à fonte primária).
5. Arquive links importantes no [Wayback Machine](https://web.archive.org/) e, se possível, use o link arquivado
   como segunda fonte.

## 2. Presunção de inocência e situação processual

Todo registro de conduta precisa declarar sua **situação** *(verificado)*:

| Código | Significado |
|---|---|
| `investigado` | inquérito ou apuração em andamento |
| `denunciado` | denúncia oferecida pelo MP, ainda não recebida |
| `reu` | denúncia/ação recebida pela Justiça, sem julgamento |
| `condenado_1a_instancia` | condenação em 1º grau (cabe recurso) |
| `condenado_2a_instancia` | condenação por órgão colegiado (cabe recurso) |
| `condenado_definitivo` | trânsito em julgado |
| `absolvido` / `arquivado` / `prescrito` / `anulado` | encerrado sem condenação |
| `sancao_administrativa` / `contas_rejeitadas` | TCU, TCE, CGU, órgão de classe, Justiça Eleitoral |
| `inelegivel` | declarado inelegível pela Justiça Eleitoral |
| `registro_publico` | fato documentado sem processo (ex.: declaração pública gravada) |

Regras de escrita:

- Linguagem **neutra e factual**. Use "o MP acusa", "a Justiça condenou", nunca "corrupto", "bandido", "herói".
- Registre **absolvições e arquivamentos**. Eles fazem parte do histórico e protegem a honestidade do projeto.
- Quando a situação mudar, **atualize o item** e conte a evolução no resumo. Não apague o histórico.
- Registre o **posicionamento público do candidato** no campo `resposta`, quando existir.
- Informe o **número do processo** sempre que disponível, para qualquer pessoa conferir.

## 3. Propostas

- Resuma com fidelidade, de preferência a partir do **plano de governo registrado no TSE** (obrigatório para
  Presidente e Governador) ou de material oficial de campanha.
- Não avalie a proposta (viabilidade, custo, mérito). O projeto informa, não opina.
- Promessas genéricas podem ser registradas como tal ("propõe melhorar a saúde, sem detalhar meios").

## 4. Trajetória e realizações

- Cargos públicos ocupados, leis de autoria ou relatoria **aprovadas**, votações relevantes, atuação
  profissional verificável, prêmios e reconhecimentos públicos.
- Para parlamentares, prefira as páginas oficiais da Câmara, do Senado e das Assembleias
  (proposições, votações, presença, uso de cota parlamentar).

## 5. Equilíbrio

- O mesmo nível de profundidade deve ser buscado para todos os candidatos de um mesmo cargo e estado.
  Prioridade de cobertura: Presidente → Governador e Senador → eleitos e candidatos de 2º turno → demais.
- As cores do site foram escolhidas para **não coincidir** com cores tradicionalmente associadas a partidos.
- A ordem das listas é técnica (cargo, resultado, nome), nunca editorial.

## 6. Dados pessoais (LGPD)

- Publicamos apenas dados de interesse público ligados à candidatura, como divulgados pelo TSE.
- **Nunca** publicamos CPF, título de eleitor, endereço, telefone, e-mail pessoal ou dados de familiares
  (exceto quando o próprio familiar é agente público ou parte do fato documentado).
- O importador descarta esses campos antes de gerar qualquer arquivo.

## 7. Correções e direito de resposta

- Qualquer pessoa, incluindo candidatos e assessorias, pode pedir correção por *issue* no GitHub
  (modelo "Correção").
- Pedidos com fonte são tratados com prioridade; erros comprovados são corrigidos e registrados no histórico
  do git, que é público.
- Conteúdo contestado sem fonte suficiente é retirado até a verificação.

## 8. Período eleitoral

- O projeto não faz propaganda, não pede voto, não impulsiona conteúdo pago sobre candidatos e não
  recebe recursos de partidos ou candidatos.
- Publicações em redes sociais seguem os mesmos critérios do site e sempre apontam para as fontes.
- Recomenda-se revisão por pessoa com formação jurídica antes da divulgação ampla de registros de conduta,
  em especial no período de campanha do 2º turno.
