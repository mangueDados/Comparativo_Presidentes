# Registro de decisões: comparativo presidencial

Cada decisão registra contexto, alternativas, escolha e consequências. As ADRs
de 001 a 008 foram aceitas pelo responsável de dados em 2026-10-06. Aceitar a
regra não valida dados: valores e datas continuam exigindo conferência na fonte.

## ADR-001 — Três blocos e quadro de papéis

- **Contexto:** o segundo turno é entre Lula, ex-presidente e presidente em
  exercício, e Flávio Bolsonaro, parlamentar sem cargo executivo, cuja
  candidatura se associa ao governo Jair Bolsonaro.
- **Alternativas:** comparar Lula × Flávio só por atuação legislativa; usar
  Lula × Jair como se fosse Lula × Flávio; criar um índice comum.
- **Escolha:** Bloco A com indicadores nacionais de todos os governos desde
  2003; Bloco B com a atuação legislativa de Flávio; Bloco C com as propostas
  registradas no TSE pelos dois candidatos. Um quadro inicial explica os papéis.
- **Consequências:** não há placar. O governo Jair aparece como governo de Jair.
  A ligação com Flávio só se faz por fatos documentados, como votos, cargos e
  programa.

## ADR-002 — Transições por sobreposição de dias

- **Contexto:** 2016 tem dois presidentes, e o ano PRODES (agosto–julho) cruza
  todas as posses.
- **Alternativas:** atribuir o ano a quem governou mais tempo; atribuir ao
  presidente de 1º de janeiro; excluir anos de transição.
- **Escolha:** registrar as datas reais de cada período e calcular os governos
  em exercício e a fração de dias de cada um. Um período com mais de um governo
  é marcado como misto e não entra em agregados por mandato. Uma futura
  comparação de início e fim de mandato usará o último período inteiramente
  anterior à posse e o último período inteiramente dentro do mandato.
- **Consequências:** é descritivo e não atribui causa. Exige colunas
  `inicio_periodo` e `fim_periodo` no CSV (ADR-003).

## ADR-003 — Esquema do CSV de observações, versão 2

- **Escolha:** acrescentar `inicio_periodo`, `fim_periodo`, `tipo_dado`
  (`observado`, `revisado`, `preliminar`, `estimativa`) e `data_acesso` como
  colunas obrigatórias.
- **Consequências:** atende às regras de ouro 2 e 3 e à distinção entre
  observado e estimado. O modelo `dados/indicadores_modelo.csv` foi atualizado;
  ainda não havia dados preenchidos, então nenhuma série precisou ser migrada.

## ADR-004 — Faixas de governo neutras

- **Escolha:** faixas em dois tons de cinza alternados, linhas verticais nas
  posses e rótulos de texto. Não há cores partidárias. Pontos usam uma única cor
  neutra, e o tipo de dado é diferenciado por forma do marcador.
- **Consequências:** a identificação não depende de cor. Períodos curtos, como
  a interinidade de Temer, podem ficar sem rótulo no gráfico; o nome aparece na
  tabela e no resumo.

## ADR-005 — Lista fechada de eventos de contexto

- **Escolha:** anotar apenas: crise financeira global de 2008–2009; recessão
  brasileira de 2014–2016; pandemia de covid-19 a partir de 2020. As datas exatas
  devem vir de fonte citável (por exemplo, datação de ciclos do CODACE/FGV e
  declarações da OMS) antes do uso. A lista vale para todos os indicadores.
- **Consequências:** novos eventos só entram por nova ADR, nunca depois de ver
  um gráfico específico. A anotação não está implementada no protótipo.

## ADR-006 — Critério de votações-chave de Flávio

- **Escolha:** incluir todas as votações nominais em plenário do Senado de
  propostas de emenda à Constituição (PECs) durante o mandato de Flávio, até a
  data de corte. Mostrar o voto registrado ao lado do resultado e da orientação
  do partido. Ausência é registrada como ausência, sem inferir posição.
- **Alternativas:** escolher matérias pela repercussão, o que é subjetivo, ou
  pela lista de outro veículo, o que gera dependência externa.
- **Consequências:** o critério é objetivo e reproduzível, mas pode deixar de
  fora projetos de lei relevantes. Ampliá-lo exige nova ADR. A atuação na Alerj
  é tratada por proposições e autoria; votos nominais da Alerj dependem da
  disponibilidade dos registros.

## ADR-007 — Fora do escopo desta versão

- **Escolha:** registros judiciais e investigações de candidatos, e checagem de
  falas de campanha.
- **Motivo:** exigem protocolo próprio, simétrico e com situação processual
  atualizada, incluindo arquivamentos e anulações. O prazo até o segundo turno
  não permite fazê-lo com o rigor necessário. Podem virar uma especificação
  `002`.

## ADR-008 — Publicação estática antes do segundo turno

- **Contexto:** segundo turno em 2026-10-25.
- **Escolha:** publicação estática e revisada. A primeira entrega prioriza
  séries com cobertura homogênea de 2003 em diante. Séries que começam depois,
  como a PNAD Contínua desde 2012, só entram rotuladas como de cobertura
  parcial. Atualização automática, filtros e interatividade ficam para depois.
- **Consequências:** é melhor publicar menos indicadores validados do que mais
  indicadores com ressalvas pendentes.

## ADR-009 — Eixo vertical e ano-base das séries

- **Data:** 2026-10-06, aceita pelo responsável de dados.
- **Escolha:** séries com todos os valores não negativos têm eixo vertical a
  partir de zero, sem exceção por indicador. Cada série começa no último
  período inteiramente anterior à posse de 2003, como base (ADR-002), e vai até
  o último dado publicado. No PRODES, isso é o ano PRODES 2002 (ago/2001–jul/2002).
- **Motivo:** um eixo cortado amplia visualmente as variações, e escolher o
  início caso a caso abriria espaço para recortes convenientes.
- **Consequências:** em séries com valores negativos, como a variação do PIB,
  o zero também fica visível e é marcado por uma linha de referência contínua.
  Isso está implementado. O período anterior a 2003
  aparece sem faixa de governo; se for preciso rotulá-lo, acrescentar FHC II a
  `dados/governos.csv` com fonte.

## ADR-010 — Combinar contas anuais e trimestrais do PIB

- **Data:** 2026-10-06, aceita pelo responsável de dados.
- **Contexto:** a conta anual consolidada do IBGE vai até 2023. Para 2024 e
  2025, só existe a estimativa das contas trimestrais.
- **Alternativas:** encerrar a série em 2023, o que deixaria Lula III com um
  único ano; usar só as contas trimestrais, que são menos definitivas; ou
  combinar as duas, marcando a diferença.
- **Escolha:** usar a conta anual até o último ano publicado e a taxa
  acumulada no 4º trimestre das contas trimestrais nos anos seguintes, com
  `tipo_dado=preliminar` (marcador vazado). A combinação só é aceita se, nos
  anos em comum, as duas fontes diferirem no máximo 0,1 ponto; senão, a coleta
  falha. Em 2026-10-06, as diferenças foram 0,1 ponto em 2018 e em 2019 e zero
  nos demais anos. O PIB per capita não recebe valores preliminares, porque as
  contas trimestrais não têm população.
- **Consequências:** quando o IBGE publicar a conta anual de 2024, a coleta
  troca o valor e o tipo automaticamente, e a linha volta a exigir conferência.
  A mesma regra vale para outras séries com versão preliminar e consolidada.

## ADR-011 — Segurança pública pelo Atlas da Violência

- **Data:** 2026-10-06, aceita pelo responsável de dados.
- **Escolha:** usar a API do Atlas da Violência (Ipea), a partir do SIM, para a
  taxa de homicídios registrados (série 20), o número de homicídios (328), as
  mortes por intervenção legal (77) e as mortes violentas por causa
  indeterminada (78), só para o Brasil. A parcela das intervenções legais nos
  homicídios é calculada pelo projeto (77 ÷ 328). A coleta confere a taxa
  publicada contra homicídios ÷ população do IBGE (tabela 6784) e falha se a
  diferença passar de 0,006; em 2002–2023, o resultado foi idêntico.
- **Linguagem:** "mortes por intervenção legal (agentes do Estado)", porque o
  registro não qualifica a legalidade da morte nem a vítima.
- **Alternativas:** Anuário Brasileiro de Segurança Pública (registros
  policiais, mais completos para letalidade policial, mas só desde cerca de
  2013); série de homicídios estimados do Atlas, que só cobre 2013–2023.
  Ambas podem entrar depois como comparação, com marcação de cobertura parcial.
- **Ressalvas registradas:** subnotificação de intervenção legal no SIM; salto
  de 121 (2002) para 491 (2003) óbitos, que sugere mudança de registro; queda
  dos homicídios em 2019 junto com alta das mortes de causa indeterminada;
  taxa de 2024 na API (20,03) diferente da noticiada (20,1), a conferir;
  metadado oficial das séries 77 e 114 incompleto; anos duplicados na série
  114 entre 1989 e 1999, fora do recorte.

## ADR-012 — Nota de contexto obrigatória por gráfico

- **Data:** 2026-10-06, aceita pelo responsável de dados.
- **Escolha:** o dicionário de dados liga cada série ao CSV (`indicador_csv`)
  e traz uma nota curta (`nota_grafico`, até 240 caracteres), exibida no
  rodapé do gráfico e no resumo. O script se recusa a gerar gráficos de séries
  sem nota; `--sem-notas` existe só para testes.
- **Motivo:** regra de ouro 4, que exige contexto e limites junto ao
  indicador, e não só em notas distantes.

## ADR-013 — Gráfico principal com os últimos mandatos de Bolsonaro e Lula

- **Data:** 2026-10-06, pedido e aceito pelo responsável de dados.
- **Contexto:** o gráfico com todos os governos desde 2003 ficou confuso para
  o leitor. A eleição opõe o grupo político do governo Bolsonaro (2019–2022) ao
  presidente em exercício (Lula III, desde 2023).
- **Escolha:** o gráfico principal de cada série é de barras, com o valor
  escrito em cada barra, só com os períodos que tocam os mandatos Bolsonaro e
  Lula III. O mesmo critério vale para os dois: o último mandato de cada um.
  Períodos com dias de dois governos (por exemplo, PRODES 2019 e 2023) ficam
  em branco hachurado com `*` e não são atribuídos a nenhum. Dados
  preliminares ficam em cinza-claro pontilhado. O mandato em curso é indicado
  com o último dado disponível. Os governos do recorte podem ser trocados com
  `--recorte`.
- **Salvaguarda (regra de ouro 7 e seção 9 da spec):** o gráfico histórico
  completo, desde 2002, continua sendo gerado (arquivos `*--historico.png`), é citado no
  rodapé do gráfico principal e deve estar acessível na página. A tabela e o
  resumo mantêm todos os anos. Assim, o recorte facilita a leitura sem
  esconder a tendência anterior.
- **Consequências:** o recorte é curto, então variações de um ano pesam mais.
  Lula III tem menos anos com dado (2 ou 3, contra 4), e o período Bolsonaro
  inclui a pandemia (ADR-005). Essas limitações devem aparecer no texto que
  acompanha cada gráfico. Esta ADR ajusta o item 3 da ADR-001: todos os
  governos continuam no histórico, mas não no gráfico principal.

## ADR-014 — Cores dos governos no gráfico principal

- **Data:** 2026-10-07, escolhida pelo responsável de dados.
- **Contexto:** o cinza do gráfico principal (ADR-013) foi considerado pouco
  atraente. Foi pedida a cor de cada partido.
- **Alternativas:** cores partidárias (vermelho para PT, azul para PL), com
  vermelho lido como "pior" em gráficos e ambiguidade do partido de
  Bolsonaro, que governou pelo PSL e hoje está no PL; verde-amarelo contra
  vermelho, com a bandeira associada a um lado e o par mais confundido por
  daltônicos; cores vivas neutras.
- **Escolha:** cores vivas sem associação partidária: roxo `#6A3D9A` para o
  primeiro governo do recorte (Bolsonaro) e laranja-queimado `#B4510B` para o
  segundo (Lula III). Contraste com o branco de 7,6:1 e 5,1:1. O nome do
  governo aparece acima das barras na mesma cor; dado preliminar usa a cor
  clareada com pontilhado; período com dois governos continua branco
  hachurado.
- **Consequências:** atualiza a ADR-004 só no gráfico principal; o histórico
  mantém faixas cinza. Se o recorte mudar, as cores seguem a ordem de
  `--recorte`, nunca o partido.

## ADR-015 — Feminicídios e homicídios de mulheres

- **Data:** 2026-10-07, aceita pelo responsável de dados.
- **Escolha:** duas séries separadas e lado a lado.
  1. **Feminicídios (registros policiais):** bases Sinesp VDE do MJSP, de 2015
     em diante, com a soma de `total_vitima` do evento "Feminicídio". Anos
     incompletos (2026) ficam de fora, e 2025 é marcado como preliminar.
  2. **Homicídios de mulheres:** SIM/DATASUS pelo TabNet, sexo feminino,
     agressões (X85-Y09) e intervenções legais (Y35-Y36), por residência, de
     2002 a 2024. A série bate com a do Atlas da Violência (série 40) em todos
     os anos de 2002 a 2023.
- **Motivo:** feminicídio é uma qualificação jurídica e depende da
  classificação policial, que mudou desde a lei de 2015. A série do SIM mede
  todos os assassinatos de mulheres e serve de controle: alta de feminicídios
  junto com queda de homicídios de mulheres sugere efeito de classificação.
- **Ressalvas:** a base do MJSP é revisada com envios atrasados (2024: 1.464
  divulgado em 2025, 1.501 em outubro de 2026); os números diferem do Anuário
  do FBSP; algumas vítimas de feminicídio não têm marcação de sexo feminino.
  As bases brutas (~290 MB) ficam fora do git, com URL e sha256 em
  `dados/brutos/sinesp_vde/MANIFESTO.csv`.
- **Oportunidade registrada:** a mesma base traz "Morte por intervenção de
  agente do Estado" a partir de registros policiais, alternativa mais completa
  que o SIM para letalidade policial (ver ADR-011).
