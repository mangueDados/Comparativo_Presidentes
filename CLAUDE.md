# CLAUDE.md — Regras do projeto

## Propósito

Construir um comparativo público, verificável e acessível sobre indicadores do
Brasil durante governos presidenciais iniciados a partir de 2003, junto a
evidências documentadas da atuação legislativa dos candidatos comparados. O
produto deve ajudar leitores, especialmente em celulares, a avaliar
informações sem sugerir causalidade ou tomar partido.

## Regras de ouro

1. **Especificação antes de implementação (SDD).** Requisitos, critérios de
   aceite e decisões de dados devem estar registrados e revisados antes de
   implementar a funcionalidade correspondente.
2. **Nenhum número sem fonte.** Todo dado publicado deve ter fonte primária ou
   institucional identificável, URL, período de referência, data de acesso,
   unidade, método de cálculo e licença/condições de uso quando aplicável.
3. **Não inventar nem preencher lacunas silenciosamente.** Ausências, revisões,
   estimativas e mudanças metodológicas devem ser explicitadas. Nunca converter
   ausência em zero nem interpolar sem justificativa documentada.
4. **Correlação não é causalidade.** A coincidência temporal com um governo não
   prova que o governo causou a variação. Contexto e limites devem aparecer
   junto ao indicador e não apenas em notas distantes. Não confundir indicadores
   nacionais observados durante um governo com resultados causados por ele.
5. **Comparações justas.** Comparar a mesma definição, unidade, cobertura,
   periodicidade e metodologia. Separar anos incompletos, mudanças de governo
   durante o ano e séries revisadas; não tratar períodos parciais como mandatos
   completos.
6. **Acessibilidade é requisito, não acabamento.** Gráficos devem funcionar em
   telas pequenas, ter contraste suficiente, não depender apenas de cor e
   oferecer título, resumo textual, rótulos e dados equivalentes em tabela.
7. **Neutralidade editorial.** Usar critérios simétricos para todos os
   governos, linguagem descritiva e paleta que não associe partidos a juízos de
   valor. Não escolher escalas ou recortes para exagerar uma conclusão.
8. **Privacidade e segurança por padrão.** Não coletar dados pessoais sem
   necessidade. Validar e sanitizar conteúdo externo e manter dependências e
   segredos fora do código e do controle de versão.
9. **Qualidade verificável.** Mudanças precisam de testes proporcionais,
   revisão dos critérios de aceite, checagem de acessibilidade e atualização
   da documentação diretamente relacionada.
10. **Mudanças rastreáveis.** Registrar decisões relevantes, fontes, versões
    dos dados e alterações de escopo. Não alterar definições ou séries sem
    documentar o impacto no comparativo.
11. **Comparar papéis equivalentes ou declarar a assimetria.** Um histórico
    presidencial e uma atuação legislativa não são medidas equivalentes.
    Apresentá-los em seções e escalas próprias; não criar nota comum sem método
    válido, justificável e previamente documentado.

## Fluxo SDD obrigatório

1. Registrar a necessidade e o resultado esperado em
   `specs/<id>-<nome>/spec.md`.
2. Definir comportamento, público, requisitos, casos-limite e critérios de
   aceite mensuráveis.
3. Pesquisar fontes e registrar indicador, definição, limitações e proveniência
   antes de publicar dados.
4. Descrever a abordagem técnica e as decisões relevantes em `plan.md`.
5. Dividir o trabalho em tarefas verificáveis em `tasks.md`.
6. Implementar, testar e revisar contra a especificação; atualizar os documentos
   se os requisitos ou decisões mudarem.

Não iniciar uma implementação com impacto de produto ou dados se houver
requisito ambíguo, fonte não validada ou critério de aceite indefinido. Peça
esclarecimento em vez de presumir uma decisão editorial relevante.

## Requisitos de dados e análise

- Manter um dicionário de dados com identificador, nome, definição, unidade,
  fórmula, população/cobertura, periodicidade, fonte, limitações e versão.
- Guardar os dados brutos separados dos dados transformados; registrar as
  transformações de forma reproduzível.
- Preservar datas e períodos originais da fonte. Não converter período
  agosto–julho em ano-calendário sem deixar a conversão explícita.
- Identificar governos por datas efetivas de exercício, e não apenas por rótulos
  de mandato. Explicitar regras para transições e períodos parciais.
- Para evidências legislativas, distinguir autoria, coautoria, votos,
  relatorias, proposições aprovadas e normas efetivamente promulgadas; registrar
  período, contexto, resultado e fonte oficial. Não equiparar contagem de
  proposições a impacto ou qualidade.
- Distinguir dado observado, estimativa e revisão; exibir ano parcial ou
  defasagem de publicação.
- Incluir referência junto de cada visualização e uma página ou seção de
  metodologia acessível.

## Requisitos de visualização e conteúdo

- Priorizar leitura em largura de 320 px ou maior, sem rolagem horizontal da
  página.
- Mostrar uma pergunta por gráfico, título informativo, unidade, período,
  fonte e resumo do principal padrão sem juízo causal.
- Fornecer alternativa tabular acessível com os mesmos valores relevantes.
- Não comunicar categoria apenas por cor; combinar cor com rótulo, padrão,
  forma ou anotação. Verificar contraste e navegação por teclado.
- Usar escalas adequadas e claramente identificadas. Em barras, iniciar em zero
  salvo justificativa explícita; em séries temporais, indicar cortes e lacunas.
- Preferir gráficos simples e comparáveis; evitar 3D, eixos duplos e rankings
  que misturem indicadores ou populações diferentes.
- Preservar os valores e a fonte em formatos legíveis por tecnologias
  assistivas. Não renderizar a informação exclusivamente em imagem.

## Engenharia e revisão

- Seguir os padrões, ferramentas e convenções já adotados no repositório.
- Preferir componentes pequenos e reutilizáveis, com limites claros entre
  obtenção/validação de dados, domínio e apresentação.
- Validar esquemas, unidades, períodos, valores ausentes e duplicidades na
  entrada dos dados; falhas devem ser visíveis e acionáveis.
- Tratar estados de carregamento, erro, dado indisponível e atualização
  separadamente; não apresentar um fallback como se fosse dado válido.
- Cobrir transformações e regras de comparação com testes automatizados.
- Executar validações pertinentes à mudança e relatar o que não foi possível
  verificar.
- Evitar dependências, abstrações, comentários e configurações desnecessários.

## Limites deste arquivo

Estas regras orientam o trabalho assistido por Claude e outros colaboradores;
não substituem a especificação funcional nem a revisão humana de dados,
metodologia, acessibilidade ou conteúdo editorial. A especificação inicial está
em `specs/001-comparativo-presidencial/`.
