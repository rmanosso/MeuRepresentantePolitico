# Instagram: guia do perfil e das primeiras postagens

As imagens saem de `python MeuRepresentante.py instagram` (assinatura padrão: **@meurepresentantepolitico**, definida em `meurep/config.py`), na pasta `instagram/`.
Os cards de candidatos saem de `cards --segundo-turno` e `cards --id ...`, na pasta `cards/`.

## 1. Configuração do perfil

| Campo | O que colocar |
|---|---|
| **Tipo de conta** | Profissional, categoria **Comunidade** (ou *Organização sem fins lucrativos*, se o projeto for formalizado). Libera estatísticas. |
| **Foto** | `instagram/perfil.png`, o triângulo dos três pilares. Funciona bem recortada em círculo. |
| **Usuário** | `@meurepresentantepolitico` |
| **Nome** (aparece na busca) | `Meu Representante Político \| Eleições 2026` |
| **Bio** | Escolha uma das opções abaixo (todas têm até 150 caracteres). |
| **Link** | Endereço do site assim que publicado no GitHub Pages. Enquanto isso, o link do repositório. |
| **Contato** | Um e-mail do projeto, não o pessoal (ex.: meurepresentantepolitico@gmail.com). |

**Endereços alinhados:** Instagram `@meurepresentantepolitico`, repositório `MeuRepresentantePolitico` no GitHub e, se possível, o domínio `meurepresentantepolitico.com.br`. O nome da marca continua "Meu Representante".

**Opções de bio**

A. Mais direta (144 caracteres):
```
Dossiê aberto e apartidário das Eleições 2026 🗳️
Propostas, trajetória e conduta de candidatos e eleitos, sempre com fonte.
👇 Compare o 2º turno
```
B. Mais convidativa (147):
```
Quem decide o futuro do país? 🔺
Informação verificável sobre candidatos e eleitos de 2026.
Apartidário · com fontes · aberto à colaboração
👇 Acesse
```
C. Mais curta (133):
```
Presidência, Senado e Câmaras: conheça quem representa você.
Propostas e histórico com fonte oficial.
Projeto cidadão e apartidário 👇
```
Recomendação: **A** durante o 2º turno. Depois de 25/10, trocar para **C**, que fala do acompanhamento dos eleitos.

## 2. Destaques (stories fixados)

| Destaque | Capa | Conteúdo |
|---|---|---|
| 2º turno | `destaques/2turno.png` | Um story por disputa, com o card comparativo e o link |
| Como funciona | `destaques/como-funciona.png` | Os 6 slides do lançamento, um por story |
| Colabore | `destaques/colabore.png` | Convite para revisores e envio de informações |
| Executivo · Senado · Câmaras | `destaques/executivo.png`, `senado.png`, `camaras.png` | Para depois do 2º turno: eleitos de cada pilar |

## 3. Calendário até o 2º turno (25/10)

| Quando | Postagem | Material |
|---|---|---|
| Dia 1 | **Lançamento** (carrossel de 6 slides) e fixar no perfil | `instagram/lancamento/` |
| Dia 1 | Stories: os slides 1, 4 e 6, com o link | idem |
| Dia 2 | **Presidência: Flávio Bolsonaro x Lula** (carrossel: comparativo e os dois cards individuais) e fixar | `cards/2turno/2turno_BR_presidente.png`, `cards/BR/*.png` |
| Dia 3 | **Chamada para revisores** (slide 6 + legenda própria) e fixar | `instagram/lancamento/06-colabore.png` |
| Dias 4 a 18 | Um governo por dia, à medida que os dossiês forem revisados: AC, AM, DF, ES, RJ, RN, TO | `cards/2turno/` |
| A cada 3 ou 4 dias | "Como ler um processo": investigado, réu e condenado (post educativo) | criar |
| Dia 19 (23/10) | Resumo: "Todas as disputas do 2º turno num só lugar" | `instagram/lancamento/05-segundo-turno.png` |
| 25/10 (eleição) | Somente mensagem neutra ("Hoje é dia de votar. Leve documento com foto."), **sem conteúdo de candidatos** | criar |

## 4. Legendas prontas

**Lançamento**
```
Quem vai decidir o futuro do país? 🔺

O Meu Representante reúne, num só lugar, informação verificável sobre candidatos e eleitos de 2026: propostas, trajetória, conduta e dados oficiais do TSE.

✔️ Toda informação tem fonte
✔️ Investigação não é condenação: informamos a situação de cada processo
✔️ O mesmo critério para todos os partidos
✔️ Projeto aberto: você pode enviar informações e ajudar a revisar

No 2º turno (25/10), compare lado a lado os candidatos à Presidência e a 7 governos.
🔗 Link na bio

#Eleições2026 #SegundoTurno #VotoConsciente #Transparência #DadosAbertos
```

**Presidência**
```
2º turno · Presidência: Flávio Bolsonaro (PL) x Lula (PT)

No 1º turno, Flávio Bolsonaro teve 47,03% dos votos válidos e Lula, 45,16% (totalização do TSE).

Arraste para ver os destaques dos planos de governo registrados no TSE. No site, a comparação completa: propostas por tema, trajetória, processos (com a situação de cada um) e patrimônio declarado, tudo com link para a fonte.

O Meu Representante não apoia candidatos. Viu algo errado? Peça correção pelo site.
🔗 Link na bio

#Eleições2026 #SegundoTurno #Presidência
```

**Chamada para revisores**
```
Procuramos revisores voluntários 🔍

Antes de ir ao ar, cada informação é conferida por duas pessoas. Para processos e controvérsias, uma delas é da área jurídica.

⚖️ Advocacia, estudantes de Direito, núcleos de prática jurídica
📰 Jornalismo e checagem
👀 Qualquer pessoa atenta, para comparar os resumos com os planos de governo do TSE

Quem revisa se compromete a usar o mesmo critério para todos os partidos. Inscrição pelo link na bio → Colabore.

#Voluntariado #DireitoEleitoral #Jornalismo #Eleições2026
```

**Governo (modelo)**
```
2º turno · Governo de [ESTADO]: [CANDIDATO A] ([PARTIDO]) x [CANDIDATO B] ([PARTIDO])

No 1º turno: [A] [X]% · [B] [Y]% dos votos válidos (TSE).
Propostas lado a lado, trajetória e processos com fonte no site.
🔗 Link na bio

#Eleições2026 #SegundoTurno #[UF]
```

## 5. Regras de neutralidade e cuidados (para conferência do jurídico)

- **Sempre os dois candidatos juntos**, no mesmo post e no mesmo dia, em ordem de votação no 1º turno e com o mesmo espaço.
- **Legendas sem adjetivos, sem pedido de voto e sem "melhor/pior".** O projeto informa, não opina.
- **Não impulsionar (pagar) posts que mostrem candidatos.** A lei eleitoral restringe o impulsionamento de conteúdo eleitoral a partidos e candidatos (Lei 9.504/97, art. 57-C). Impulsionar só posts institucionais, como o de recrutamento de revisores, e só depois de confirmar com o jurídico.
- **Só publicar o que está no site**, ou seja, itens confirmados. Itens em revisão nunca vão para o Instagram, nem em story.
- **No dia da eleição, nada sobre candidatos.**
- **Comentários:** fixar uma regra no primeiro post: *"Debate respeitoso é bem-vindo. Removemos ofensas, ataques pessoais e afirmações graves sem fonte. Encontrou um erro? Peça correção pelo link na bio."* Não apagar críticas ao projeto. Responder pedidos de correção com o link do formulário.
- **Direitos de imagem:** as fotos vêm do TSE (divulgação oficial da candidatura). Manter o crédito "Foto: TSE" nos posts com candidatos.

## 6. Acompanhamento

Uma vez por semana, olhar alcance, salvamentos, compartilhamentos e cliques no link. Os posts mais salvos indicam o formato a repetir. Registrar quantas inscrições de revisores chegam por semana.
