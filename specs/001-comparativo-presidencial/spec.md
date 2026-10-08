# Especificação: comparativo presidencial

- **Status:** revisada e com decisões aceitas pelo responsável de dados em
  2026-10-06; publicação ainda depende da validação de cada fonte e série
- **Tipo:** especificação de produto e dados
- **Público:** leitores em geral, com prioridade para uso em celular
- **Recorte proposto:** governos brasileiros iniciados a partir de 2003
- **Contexto eleitoral:** segundo turno entre Lula (PT) e Flávio Bolsonaro (PL)
  marcado para 2026-10-25. Decisões e registros: [decisoes.md](./decisoes.md).

## 1. Problema e objetivo

Leitores precisam entender como indicadores selecionados do Brasil evoluíram
durante diferentes governos e consultar evidências da atuação pública dos
candidatos, em especial em telas pequenas. O produto deve apresentar séries
comparáveis e permitir verificar origem, significado e limitações dos dados.

O objetivo é informar uma avaliação eleitoral entre Lula e Flávio Bolsonaro,
não declarar um vencedor por meio de um índice opaco. A candidatura de Flávio
se apresenta publicamente associada ao governo Jair Bolsonaro (2019–2022). Por
isso, o governo de Jair aparece no comparativo, mas como **governo de Jair**, e
não como histórico de Flávio.

O produto **não** deve afirmar que a evolução observada foi causada pelo
presidente. Indicadores dependem também de governos estaduais e municipais,
Congresso, Judiciário, condições econômicas, fatores sociais, eventos externos,
políticas anteriores e mudanças nas próprias medições.

## 2. Quem é comparado e em que papel (assimetria declarada)

Os três nomes têm históricos de natureza diferente. A tabela abaixo deve
aparecer, em versão para o leitor, no início do produto.

| Pessoa | Papel no comparativo | Cargos relevantes (a confirmar em fonte oficial) | O que pode ser mostrado |
|---|---|---|---|
| Luiz Inácio Lula da Silva | Candidato e presidente em exercício | Presidente 2003–2010 e desde 2023; deputado federal 1987–1991 | Indicadores nacionais durante seus governos (Bloco A); proposta registrada no TSE (Bloco C) |
| Jair Bolsonaro | Ex-presidente; **não é candidato** | Presidente 2019–2022; deputado federal 1991–2018 | Indicadores nacionais durante seu governo (Bloco A), como contexto do grupo político da candidatura de Flávio |
| Flávio Bolsonaro | Candidato | Deputado estadual no RJ (Alerj) 2003–2019; senador pelo RJ desde 2019 | Atuação legislativa documentada (Bloco B); proposta registrada no TSE (Bloco C) |

Regras derivadas:

1. Flávio nunca exerceu cargo executivo. Não há série de "resultados de
   Flávio" equivalente aos indicadores presidenciais.
2. Os resultados do governo Jair não são atribuídos a Flávio. A ligação entre
   os dois só pode ser mostrada com fatos documentados, por exemplo votos
   nominais de Flávio em matérias do governo Jair, cargos ocupados ou
   declarações públicas e programa registrado no TSE que mencionem continuidade.
3. O Bloco A mostra **todos** os governos do recorte (Lula I e II, Dilma,
   Temer, Jair, Lula III), não só Lula e Jair, para evitar escolher janelas
   convenientes.
4. Lula III é um mandato em curso. As séries mostram apenas os anos com dado
   publicado, que podem ser 3 de 4 anos, sempre identificados como parciais.

## 3. Estrutura do produto

- **Bloco A — Indicadores nacionais por período presidencial.** Um gráfico e
  uma tabela por indicador. Os períodos presidenciais aparecem como faixas de
  contexto temporal, não como explicação causal.
- **Bloco B — Atuação legislativa de Flávio Bolsonaro.** Seção própria, com
  escala e formato próprios: proposições, autoria e coautoria, relatorias,
  votos nominais e desfechos, na Alerj e no Senado.
- **Bloco C — Propostas registradas no TSE (aceito, ver decisoes.md).** Este é o único
  bloco em que os dois candidatos aparecem em condição simétrica. Deve
  comparar as propostas por tema, com citação literal e link para o documento
  registrado no DivulgaCandContas, sem avaliar viabilidade nem qualidade.
- **Metodologia.** Fontes, definições, regras de transição, limitações e
  histórico de revisões.

## 4. Usuários e necessidades

- Como leitor de celular, quero compreender a mensagem principal de um gráfico
  sem ampliar ou percorrer uma legenda extensa.
- Como leitor que deseja conferir uma afirmação, quero encontrar os valores,
  definições e fontes sem sair da visualização.
- Como leitor com deficiência ou que usa tecnologia assistiva, quero acessar a
  informação sem depender de cor, mouse ou imagem.
- Como leitor interessado em comparar governos, quero distinguir anos completos,
  transições, períodos parciais e dados ainda não disponíveis.
- Como eleitor, quero saber o que cada candidato efetivamente fez no cargo que
  ocupou e o que propõe, sem que um papel seja medido com a régua do outro.

## 5. Escopo inicial

### Incluído

- Série histórica nacional em cinco áreas: tecnologia, educação, economia,
  desmatamento e segurança pública.
- Comparação temporal relacionada a governos iniciados a partir de 2003, com
  datas efetivas de exercício (seção 7).
- Seção documental separada sobre a atuação legislativa de Flávio Bolsonaro,
  baseada em registros oficiais e com período e data de corte declarados.
- Uma visualização principal simples por indicador, resumo textual e tabela
  equivalente.
- Metodologia, proveniência, unidade, período de referência e limitações visíveis.
- Apresentação explícita de lacunas, revisões, períodos parciais e defasagem.

### Fora do escopo desta especificação

- Atribuir causalidade ou criar uma nota/placar geral para cada presidente.
- Atribuir a Flávio resultados do governo Jair Bolsonaro, ou a Lula resultados
  de governos de outros presidentes do mesmo partido.
- Equiparar diretamente resultados de governos presidenciais a contagens de
  atividade parlamentar, ou somá-los em uma pontuação única sem método
  validado.
- Comparar governos estaduais ou municipais como se fossem dados federais.
- Misturar definições, fontes ou populações diferentes em uma única série.
- Publicar valores sem fonte, data de referência, data de acesso e validação.
- Checagem de falas de campanha. Isso pode virar uma especificação própria.
- Definir framework, hospedagem ou identidade visual final antes da descoberta
  técnica e editorial.

## 6. Proposta de indicadores

Os itens abaixo são **candidatos para investigação**, não séries já aprovadas.
Cada um precisa passar pela validação de fonte, definição, cobertura,
periodicidade, revisões, disponibilidade histórica e licença antes de entrar no
produto. O inventário fica em
[dados/dicionario_indicadores.csv](../../dados/dicionario_indicadores.csv).

| Área | Indicador candidato | Visualização sugerida | Cuidados essenciais |
|---|---|---|---|
| Tecnologia | Percentual de domicílios com acesso à internet | Linha temporal com rótulos nos pontos disponíveis | A PNAD Contínua TIC/IBGE começa em 2016 e não cobre Lula I/II. A PNAD anual anterior tem outro desenho e não deve ser emendada sem nota. Avaliar a TIC Domicílios (Cetic.br), que tem série mais longa, e verificar comparabilidade. Distinguir domicílio de pessoa. |
| Educação | IDEB por etapa de ensino e rede pública, em séries separadas | Pequenos múltiplos por etapa, nos anos efetivamente medidos | Começa em 2005 e é bienal; não interpolar. A edição de 2021 foi afetada pela pandemia e tem notas do INEP. Não misturar etapas, redes ou metas. |
| Economia | Crescimento real do PIB e PIB real per capita; IPCA; desemprego; rendimento real; pobreza/desigualdade; resultado primário e dívida bruta, conforme séries homologadas | Painéis separados por indicador e unidade | Desemprego, renda, pobreza e Gini mudaram de pesquisa em 2012 (PNAD/PME → PNAD Contínua). Não emendar séries sem marcação de quebra; uma série que só começa em 2012 não permite comparar com Lula I/II. Verificar mudanças metodológicas da dívida bruta (BCB) e revisões das Contas Nacionais. |
| Desmatamento | Taxa anual estimada pelo PRODES para Amazônia Legal e Cerrado, em séries distintas | Painéis separados, eixo em km²/ano | O ano PRODES vai de agosto a julho. Os anos PRODES 2003, 2011, 2016, 2019 e 2023 são **mistos**, com dois presidentes no período. Verificar quando a série anual do Cerrado começa. Não somar biomas. |
| Segurança pública | Taxa de homicídios por 100 mil habitantes, série nacional homogênea (SIM/Ministério da Saúde, Atlas da Violência/IPEA) | Linha temporal com taxa e rótulos | Defasagem de cerca de dois anos. Verificar a alta de mortes violentas por causa indeterminada em anos recentes, que pode reduzir artificialmente a taxa. Segurança tem forte dimensão estadual. |

### Segurança pública: homicídios e mortes por intervenção de agentes do Estado

Fonte: Atlas da Violência (Ipea), a partir do SIM/Ministério da Saúde (ADR-011).
A seção tem duas partes, para comparação posterior:

1. **Homicídios:** taxa de homicídios registrados por 100 mil habitantes, ao
   lado das mortes violentas por causa indeterminada, que servem de indicador
   de qualidade do registro.
2. **Mortes por intervenção de agentes do Estado:** número de óbitos
   registrados como intervenção legal e sua parcela nos homicídios
   registrados, que já os incluem.
3. **Violência contra mulheres:** feminicídios (registros policiais, Sinesp
   VDE/MJSP, desde 2015) ao lado dos homicídios de mulheres (SIM), sempre em
   gráficos separados. A segunda série serve de controle para mudanças na
   classificação policial (ADR-015).

Linguagem: usar "mortes por intervenção legal" ou "mortes causadas por agentes
do Estado". O registro não informa se a morte foi legítima ou ilegal nem a
situação criminal da vítima. Por isso, não usar "assassinatos cometidos por
policiais" nem termos como "bandidos". Toda leitura deve mencionar a
subnotificação no SIM e o caráter predominantemente estadual das polícias.

### Eventos de contexto (aceito, ver decisoes.md)

Eventos externos de grande escala podem ser anotados nos gráficos, com uma
regra simétrica: só entram eventos de alcance nacional ou global com marco
temporal documentado, como a crise financeira de 2008–2009, a recessão de
2014–2016 e a pandemia de covid-19 a partir de 2020. A lista é fechada antes de
ver os gráficos, aplicada a todos os indicadores e registrada em
[decisoes.md](./decisoes.md). Anotar contexto não explica a variação.

## 7. Governos, datas e transições

Os governos são identificados por datas efetivas de exercício, registradas em
[dados/governos.csv](../../dados/governos.csv). Cada data deve ser conferida em
fonte oficial antes de a linha ser marcada como validada.

| Período | Presidente | Observação |
|---|---|---|
| 2003-01-01 a 2006-12-31 | Lula (I) | |
| 2007-01-01 a 2010-12-31 | Lula (II) | |
| 2011-01-01 a 2014-12-31 | Dilma Rousseff (I) | |
| 2015-01-01 a 2016-05-11 | Dilma Rousseff (II) | Afastada em 2016-05-12 |
| 2016-05-12 a 2016-08-30 | Michel Temer (interino) | |
| 2016-08-31 a 2018-12-31 | Michel Temer | |
| 2019-01-01 a 2022-12-31 | Jair Bolsonaro | |
| 2023-01-01 a 2027-01-05 | Lula (III) | Em exercício; o fim do mandato segue a EC 111/2021 |

Convenção: o dia da posse pertence a quem assume. Datas conferidas em
2026-10-06 na Biblioteca da Presidência, na Agência Senado e no texto da EC
111/2021. A página da Biblioteca registra o fim de Lula I e Lula II como
"31/01/2006" e "31/01/2010". Isso contradiz as posses seguintes, em 01/01, e foi
tratado como erro da fonte, com registro na coluna `nota`.

Política de transição (aceita, ADR-002):

1. Cada observação registra `inicio_periodo` e `fim_periodo` reais da fonte,
   por exemplo 2018-08-01 a 2019-07-31 para o PRODES 2019.
2. O pipeline calcula **quais governos estiveram em exercício durante o
   período e por qual fração dos dias**. É uma descrição factual, não uma
   atribuição.
3. Um período com mais de um mandato é marcado como **misto** na tabela e no
   resumo, com a participação de cada um. Quando há troca de pessoa na
   Presidência, também é marcado com `*` no gráfico. Reeleição e passagem de
   interino a titular são mistas, mas não são troca de presidente.
4. Nenhum valor de período misto entra em agregados por mandato, como médias
   ou variações, sem uma regra específica aprovada.
5. Se houver comparação de início e fim de mandato, usar como base o último
   período inteiramente anterior à posse e, como final, o último período
   inteiramente dentro do mandato, sempre declarando a defasagem de efeito.
   Aceito (ADR-002); ainda não implementado.

## 8. Atuação legislativa de Flávio Bolsonaro (Bloco B)

- **Período:** Alerj de 2003-02 a 2019-01 e Senado de 2019-02 até a data de
  corte. Datas a confirmar nos registros oficiais.
- **Data de corte:** a fixar, por exemplo a data da extração, registrada em
  cada linha.
- **Fontes:** Dados Abertos do Senado Federal (proposições, autoria,
  relatorias, votações nominais), Congresso Nacional para matérias conjuntas
  e o portal e o diário oficial da Alerj. Conferir no documento de origem.
- **Categorias, sempre separadas:** autoria principal; coautoria; relatoria;
  voto nominal (sim/não/abstenção/ausência/obstrução, conforme o registro);
  proposição aprovada em uma casa; norma promulgada ou sancionada; arquivada ou
  em tramitação.
- **Classificação temática:** se for usada, deve seguir um protocolo escrito
  antes da classificação, com duas pessoas classificando e registro das
  divergências.
- **Votações-chave (aceito, ver decisoes.md):** escolher com critério declarado antes de
  ver os votos, por exemplo matérias de maior repercussão segundo critério
  objetivo ou PECs. O voto de Flávio é mostrado ao lado do resultado geral e da
  orientação do partido.

Contagens de proposições, discursos ou votos não medem, isoladamente, impacto,
qualidade ou benefício ao país. Não atribuir ao parlamentar resultados nacionais
nem aprovação de matéria sem participação documentada. Esta seção não deve ser
plotada na mesma escala dos indicadores nacionais.

## 9. Regras de comparação temporal

1. Mostrar todos os anos disponíveis no período definido pela fonte; não cortar
   anos desfavoráveis nem escolher início/fim para produzir uma conclusão.
2. Indicar no eixo e na tabela o período observado pela fonte, que pode diferir
   do ano impresso.
3. Marcar governos como contexto temporal, com faixas neutras e rótulos de
   texto, não como explicação causal. O gráfico principal mostra os últimos
   mandatos de Bolsonaro e de Lula (ADR-013), e o histórico completo continua
   disponível ao lado.
4. Seguir a política de transição da seção 7; não atribuir automaticamente um
   período misto a um único governo.
5. Exibir mandatos incompletos e dados parciais como tais; não compará-los
   visualmente como se fossem períodos completos.
6. Usar valores absolutos e taxas apenas quando forem adequados ao indicador;
   não comparar unidades distintas em um mesmo eixo.
7. Não interpolar anos ausentes nem converter valores sem registrar fórmula,
   fonte de denominador e arredondamento.
8. Preservar revisões da fonte e identificar a versão usada. Se revisões
   mudarem a leitura, explicar e atualizar os gráficos afetados.
9. Marcar quebras de série (mudança de pesquisa ou método). Segmentos
   incompatíveis são séries distintas.
10. Separar resultados do período presidencial de métricas de atividade
    parlamentar; não inferir causalidade nem comparar escalas incompatíveis.

## 10. Requisitos funcionais

- **RF-01:** Exibir uma visualização individual para cada indicador aprovado,
  com título que identifique indicador e geografia.
- **RF-02:** Incluir unidade, período de referência, fonte, data de acesso e
  link para metodologia junto à visualização.
- **RF-03:** Apresentar um resumo textual neutro e uma tabela acessível com os
  mesmos valores e anos representados.
- **RF-04:** Distinguir de forma visível, e não só por cor, valores ausentes,
  estimativas, preliminares, revisões, anos parciais e períodos mistos.
- **RF-05:** Permitir identificar os governos no contexto temporal por faixas
  e rótulos de texto, sem usar a cor como único meio de identificação e sem
  cores partidárias.
- **RF-06:** Disponibilizar uma explicação da definição, cobertura, cálculo e
  limitações de cada indicador.
- **RF-07:** Não renderizar comparação quando as séries não passarem pelas
  regras de comparabilidade; explicar o motivo de forma clara.
- **RF-08:** Exibir a seção de atuação legislativa em formato próprio, com período,
  método de contagem, fonte oficial e distinção entre autoria, coautoria,
  relatoria, voto e resultado final.
- **RF-09:** Apresentar indicadores econômicos individualmente e com definições
  e periodicidades explícitas; não gerar uma nota econômica agregada sem método
  previamente especificado e validado.
- **RF-10:** Exibir no início do produto o quadro de papéis da seção 2, que
  explica por que Lula, Jair e Flávio aparecem em blocos diferentes.
- **RF-11:** Para cada observação, informar quais governos estiveram em
  exercício durante o período de referência e em que proporção.

## 11. Requisitos não funcionais

- **RNF-01 — Mobile-first:** conteúdo e visualizações devem caber em viewport
  de 320 px de largura sem rolagem horizontal da página.
- **RNF-02 — Acessibilidade:** navegação por teclado, foco visível, contraste
  adequado, estrutura semântica, texto alternativo/resumo e alternativa
  tabular; nenhum significado exclusivamente por cor.
- **RNF-03 — Legibilidade:** rótulos, unidades e valores importantes legíveis
  em tela pequena; evitar legenda extensa e texto sobreposto.
- **RNF-04 — Confiabilidade:** erros de carregamento e de validação devem ser
  comunicados; não apresentar dado fictício ou fallback como resultado real.
- **RNF-05 — Reprodutibilidade:** dados derivados devem poder ser reconstruídos
  a partir da origem identificada e das transformações documentadas.
- **RNF-06 — Neutralidade:** desenho, linguagem, filtros e escalas não devem
  conferir vantagem visual sistemática a um governo ou partido. Faixas de
  governo usam tons neutros alternados, sem vermelho, verde, amarelo ou azul
  associados a partidos ou campanhas. No gráfico principal, cada governo do
  recorte tem uma cor viva sem associação partidária (roxo e laranja-queimado,
  ADR-014).
- **RNF-07 — Comparabilidade de papéis:** resultados executivos e atividades
  legislativas devem permanecer conceitual e visualmente distintos.

## 12. Critérios de aceite

- [ ] Cada indicador publicado tem ficha completa de proveniência, definição,
  unidade, período, método e limitações revisada.
- [ ] Os valores exibidos correspondem à fonte e às transformações
  documentadas; períodos sem observação não viram zero nem são interpolados.
- [ ] Períodos mistos e mandatos parciais são identificáveis no gráfico, na
  tabela e no resumo, e não aparecem como mandatos completos.
- [ ] As datas de exercício de todos os governos estão conferidas em fonte
  oficial.
- [ ] Em uma largura de 320 px, cada gráfico continua legível e a página não
  exige rolagem horizontal.
- [ ] A informação pode ser compreendida por texto e consultada em tabela,
  sem depender da cor ou do gráfico interativo.
- [ ] A navegação por teclado e leitores de tela expõe título, resumo,
  unidade, fonte e alternativa tabular.
- [ ] Cores e contraste são verificados, e séries mantêm distinção também por
  rótulo ou forma.
- [ ] Escalas e arredondamentos estão identificados; não há eixos duplos ou
  efeitos 3D.
- [ ] O texto não atribui causalidade ao presidente e descreve as limitações
  relevantes junto ao indicador.
- [ ] Nenhum resultado do governo Jair é apresentado como resultado de Flávio.
- [ ] Os indicadores econômicos cobrem dimensões distintas e nenhum é usado
  isoladamente como medida total de desempenho.
- [ ] A seção legislativa de Flávio usa registros oficiais, período explícito e
  categorias de atividade claramente diferenciadas; não sugere equivalência
  direta com resultados presidenciais.
- [ ] Testes automatizados cobrem validação dos dados e transformações usadas.

## 13. Decisões aceitas e perguntas em aberto

Aceitas em 2026-10-06 (detalhes em [decisoes.md](./decisoes.md)): estrutura em
três blocos com o quadro de papéis; Bloco C na primeira versão; política de
transição por sobreposição de dias, sem agregados por mandato no protótipo;
lista fechada de eventos de contexto; votações-chave com critério prévio;
registros judiciais fora do escopo desta versão; publicação estática revisada
antes do segundo turno.

Ainda em aberto, dependentes de pesquisa ou dados:

- Quais séries e versões das fontes candidatas oferecem continuidade
  metodológica suficiente para publicação?
- Para segurança, qual série nacional de homicídios, após comparar SIM/IPEA e
  outras fontes quanto a limitações, cobertura e defasagem?
- Qual data de corte da atuação legislativa e qual lista final de
  votações-chave, a partir do critério da ADR-006?
- Qual identidade visual e quais tecnologias adotar na página final?

## 14. Protótipo Python

O script de linha de comando roda em Python local ou no Google Colab. Recebe um
CSV de observações (seção 15) e, opcionalmente, o CSV de governos. Rejeita
observações não validadas, metadados incompletos, datas inválidas, períodos
sobrepostos na mesma série, unidades inconsistentes e anos duplicados. Gera:

- dois PNGs por série, um largo e um para celular (`--celular`), com pontos
  no meio do período de referência, faixas neutras de governos com rótulos de
  texto, marcadores distintos por tipo de dado, `*` nos períodos com troca de
  presidente e rodapé com fonte, período, data de acesso e legenda;
- `dados_validados.csv`, com proveniência e, para cada observação, os governos
  em exercício no período com dias e percentual, `periodo_misto` (mais de um
  mandato, incluindo reeleição e interinidade) e `troca_de_presidente`;
- `resumos.md`, com um resumo descritivo e uma tabela por série, sem
  linguagem causal.

O protótipo **não** coleta dados, não aprova fontes, não calcula agregados por
mandato, não compara atividade legislativa com resultados executivos e não
calcula um vencedor.

## 15. Esquema do CSV de observações

| Coluna | Conteúdo |
|---|---|
| `indicador`, `serie` | Nome do indicador e recorte (por exemplo, "Brasil", "Amazônia Legal") |
| `ano` | Ano-rótulo usado pela fonte |
| `valor` | Número com ponto decimal, sem separador de milhar |
| `unidade` | Unidade, constante na série |
| `fonte`, `url_fonte` | Instituição e URL http(s) do dado |
| `periodo_ref` | Descrição do período como a fonte o publica |
| `inicio_periodo`, `fim_periodo` | Datas AAAA-MM-DD do período coberto |
| `tipo_dado` | `observado`, `revisado`, `preliminar` ou `estimativa` |
| `data_acesso` | Data AAAA-MM-DD da extração, não futura |
| `validada` | `sim` somente após conferência editorial |
| `metodologia` | Método, versão e transformações aplicadas |
