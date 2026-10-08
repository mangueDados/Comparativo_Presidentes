# Tarefas: comparativo presidencial

Prazo de referência: publicação até 2026-10-23 (ver [plan.md](./plan.md)).

## Decisões editoriais

- [x] Definir estrutura em três blocos e quadro de papéis (ADR-001).
- [x] Definir política de transição por sobreposição de dias (ADR-002).
- [x] Definir lista fechada de eventos de contexto (ADR-005).
- [x] Definir critério de votações-chave (ADR-006) e itens fora do escopo
  (ADR-007).
- [ ] Obter fonte citável para as datas dos eventos de contexto (CODACE/FGV,
  OMS) antes de anotá-los.
- [ ] Fixar a data de corte da atuação legislativa.

## Dados — Bloco A (prioridade: cobertura desde 2003)

- [x] Conferir datas de exercício presidencial em fonte oficial
  (`dados/governos.csv`); divergência da Biblioteca da Presidência registrada.
- [x] Criar o dicionário de dados com os candidatos e as ressalvas conhecidas.
- [x] PRODES Amazônia Legal: bruto salvo em `dados/brutos/`, transformação em
  `coleta/prodes_amazonia.py`, 24 anos (2002–2025, todos consolidados) em
  `dados/indicadores.csv`.
- [ ] Conferir os 24 valores do PRODES Amazônia no painel TerraBrasilis e
  marcar `validada=sim`.
- [x] IPCA acumulado no ano: bruto da API do IBGE em `dados/brutos/`,
  transformação em `coleta/ipca.py` com conferência pelo número-índice, 24 anos
  (2002–2025); 2026 excluído por ser parcial.
- [ ] Conferir os 24 valores do IPCA no SIDRA e marcar `validada=sim`.
- [x] Variação real do PIB e do PIB per capita: brutos das tabelas 6784 e 5932
  em `dados/brutos/`, transformação em `coleta/pib.py` (ADR-010); PIB 2002–2025
  (2024–2025 preliminares), per capita 2002–2023.
- [ ] Conferir os valores do PIB no SIDRA e marcar `validada=sim`; verificar a
  população usada no PIB per capita.
- [x] Segurança pública pelo Atlas da Violência (ADR-011): taxa de homicídios,
  mortes por intervenção legal, parcela nos homicídios (2002–2024) e mortes
  de causa indeterminada (2002–2023), em `coleta/atlas_violencia.py`.
- [ ] Conferir os valores do Atlas e a taxa de 2024 (20,03 contra 20,1
  noticiado) no relatório Atlas da Violência 2026; marcar `validada=sim`.
- [ ] Avaliar série complementar de mortes por intervenção de agente do Estado
  pelo Sinesp VDE (registros policiais, desde 2015), já baixado para os
  feminicídios.
- [x] Feminicídios (Sinesp VDE, 2015–2025) e homicídios de mulheres (SIM,
  2002–2024), em `coleta/sinesp_feminicidio.py` e `coleta/sim_mulheres.py`
  (ADR-015).
- [ ] IDEB por etapa, rede pública (INEP); anotar a edição de 2021.
- [ ] PRODES Cerrado: verificar o início da série anual.
- [ ] Internet nos domicílios: comparar TIC Domicílios (Cetic.br) e PNAD
  Contínua TIC; decidir ou excluir.
- [ ] Dívida bruta e resultado primário (BCB): verificar quebra metodológica.
- [ ] Séries da PNAD Contínua (desocupação, renda, pobreza, Gini) como cobertura
  parcial desde 2012, se houver tempo.
- [ ] Salvar os arquivos brutos das demais séries em `dados/brutos/` com data
  de extração.
- [x] Conferência automática independente e planilha de conferência
  (`conferencia/`): 162 de 185 valores OK, 0 divergentes, 23 manuais.
- [ ] Conferência humana na planilha e aplicação com `conferencia/aplicar.py`.

## Dados — Bloco B (Flávio Bolsonaro)

- [ ] Confirmar períodos de mandato na Alerj e no Senado em fonte oficial.
- [ ] Extrair proposições de autoria e coautoria (Dados Abertos do Senado;
  Alerj).
- [ ] Extrair votações nominais de PECs no plenário do Senado com voto de
  Flávio, resultado e orientação do partido.
- [ ] Documentar protocolo de classificação (coautoria, duplicadas, arquivadas,
  em tramitação) e, se houver classificação temática, fazê-la com duas pessoas.

## Dados — Bloco C (propostas no TSE)

- [ ] Baixar os programas registrados pelos dois candidatos no
  DivulgaCandContas; registrar URL, data e versão.
- [ ] Definir temas antes da leitura (alinhados às áreas do Bloco A) e extrair
  citações literais com página.

## Protótipo e publicação

- [x] Validador CSV com colunas, campos obrigatórios, valores finitos, URLs,
  aprovação editorial, duplicidades, unidade, datas e sobreposição de períodos.
- [x] Faixas neutras de governo, marcação de troca de presidente e tipo de
  dado por forma do marcador.
- [x] Gráfico em versão larga e para celular; resumo em texto e tabela.
- [x] Testes automatizados de validação, sobreposição de governos e saídas.
- [ ] Escolher formato da página estática e hospedagem.
- [ ] Página com quadro de papéis (RF-10), três blocos e metodologia.
- [ ] Testar em 320 px, teclado, leitor de tela e contraste.
- [ ] Revisão editorial e conferência cruzada de todos os valores.
- [ ] Documentar processo de atualização e histórico de revisões.
