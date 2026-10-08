# Plano: comparativo presidencial

## Abordagem

Começar pela confiabilidade das séries e pela experiência em celular. A camada
de dados preserva a origem e valida cada observação. A camada de apresentação
só recebe séries aprovadas e entrega visualização, resumo e tabela. A primeira
publicação é estática e revisada, antes do segundo turno de 2026-10-25
(ADR-008).

## Arquitetura lógica

1. **Fontes e proveniência:** inventário das fontes, URLs, arquivos/versões,
   datas de extração, licenças e notas metodológicas
   (`dados/dicionario_indicadores.csv`).
2. **Dados brutos:** cópias imutáveis ou referências versionadas dos arquivos
   originais, sem edição manual (`dados/brutos/`, a criar quando houver a
   primeira extração).
3. **Validação e transformação:** esquemas, datas de período explícitas,
   verificações de duplicidade, sobreposição e lacunas
   (`analise_comparativo.py`).
4. **Governos:** períodos de exercício conferidos (`dados/governos.csv`) e
   cálculo descritivo dos governos em exercício em cada período de referência
   (ADR-002).
5. **Catálogo de indicadores:** definições, cobertura, periodicidade, unidade,
   fórmula, fontes, quebras de série e limitações por indicador.
6. **Apresentação:** gráfico largo e de celular, resumo textual e tabela
   equivalente; página final com quadro de papéis (RF-10).
7. **Evidências legislativas (Bloco B):** registros oficiais de atividade
   parlamentar de Flávio Bolsonaro, classificados por autoria, coautoria,
   relatoria, voto e desfecho, em seção distinta dos indicadores nacionais.
8. **Propostas (Bloco C):** documentos registrados no TSE pelos dois candidatos,
   comparados por tema com citação literal.

## Cronograma até o segundo turno

| Período | Entrega |
|---|---|
| até 10/10 | Homologar as séries de cobertura homogênea desde 2003 (PRODES Amazônia, IPCA, PIB real, homicídios SIM, IDEB); baixar os brutos; preencher `dados/indicadores.csv` |
| até 14/10 | Extrair do Senado as votações nominais de PECs (ADR-006) e as proposições de autoria de Flávio; levantar as proposições na Alerj; baixar os programas no TSE |
| até 18/10 | Montar a página estática com os três blocos; revisar acessibilidade em 320 px, teclado e leitor de tela |
| até 21/10 | Revisão editorial e checagem cruzada de todos os valores contra a fonte, feita por uma segunda pessoa |
| 22–23/10 | Publicação, com margem antes da votação de 25/10 |

Séries da PNAD Contínua (desemprego, renda, pobreza) só entram se houver tempo,
rotuladas como de cobertura parcial desde 2012.

## Decisões a registrar

Registrar em [decisoes.md](./decisoes.md) as escolhas que afetem fonte,
definição do indicador, tratamento de transição, formato de dados, stack,
hospedagem ou atualização. Cada decisão registra contexto, alternativas
consideradas, escolha e consequências.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Séries mudam de método ou têm cobertura incompleta | Verificar notas técnicas antes de aprovar; separar segmentos incompatíveis e explicar lacunas. |
| Leitores interpretam associação temporal como efeito causal | Aviso no rodapé de cada gráfico e no resumo; evitar ranking e placar presidencial. |
| Leitores atribuem a Flávio os indicadores do governo Jair | Quadro de papéis no topo (RF-10); ligação só por fatos documentados. |
| Ano parcial ou período misto distorce a comparação | Marcação automática de período misto e de troca de presidente; agregados por mandato não implementados. |
| Visualização não funciona em celular ou com tecnologia assistiva | Versão de celular dos gráficos, resumo em texto e tabela; teste em 320 px, teclado e leitor de tela. |
| Fonte atualiza valores retroativamente | Versionar extrações, registrar data de acesso e revalidar séries afetadas. |
| Fonte oficial contém erro material | Registrar a divergência na coluna `nota` e na metodologia, como no caso das datas da Biblioteca da Presidência. |
| Atividade parlamentar é confundida com resultado executivo | Seções e escalas distintas; explicar limites das contagens. |
| Prazo curto leva a publicar dado não conferido | O validador bloqueia linhas não validadas; publicar menos indicadores (ADR-008). |
