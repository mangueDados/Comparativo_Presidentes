# Comparativo de presidentes do Brasil

Projeto de informação pública para o segundo turno de 2026, entre Lula e
Flávio Bolsonaro. O produto tem três blocos:

- **A. Indicadores nacionais** durante todos os governos desde 2003: Lula I e
  II, Dilma, Temer, Jair Bolsonaro e Lula III.
- **B. Atuação legislativa de Flávio Bolsonaro** na Alerj e no Senado.
- **C. Propostas registradas no TSE** pelos dois candidatos.

O governo de Jair Bolsonaro aparece como governo de Jair, e não como histórico
de Flávio. Indicadores nacionais durante um governo não provam, por si só, que
o presidente os causou. Atuação executiva e legislativa são papéis diferentes e
não são tratadas como resultados equivalentes. As decisões editoriais estão em
[decisoes.md](./specs/001-comparativo-presidencial/decisoes.md).

## Princípios

- Dados rastreáveis, com fonte, definição, unidade e período visíveis.
- Comparações metodologicamente consistentes e limites explicados.
- Contexto econômico em múltiplos indicadores, sem placar partidário simplista.
- Visualizações legíveis em celular e com alternativa em tabela.
- Neutralidade editorial e acessibilidade desde o início.

## Desenvolvimento orientado por especificação (SDD)

Leia primeiro [CLAUDE.md](./CLAUDE.md) e a especificação em
[specs/001-comparativo-presidencial/spec.md](./specs/001-comparativo-presidencial/spec.md).
Cada mudança de produto deve seguir a sequência especificação → plano → tarefas
→ implementação → validação. Não publicar valores até validar e registrar as
fontes e a metodologia.

## Primeira versão Python

O script [analise_comparativo.py](./analise_comparativo.py) valida CSVs de
indicadores com fonte e metodologia documentadas. Para cada série, gera:

- um gráfico de pontos em versão larga e outra para celular, com faixas cinza
  dos períodos presidenciais;
- uma tabela CSV acessível;
- um resumo em texto (`resumos.md`).

Para cada observação, a tabela informa quais governos estiveram em exercício
durante o período de referência, com dias e percentual, e marca períodos com
mais de um mandato (`periodo_misto`) ou com troca de presidente
(`troca_de_presidente`). Isso descreve coincidência temporal, não causa. O
script não baixa nem inventa dados e não interpola lacunas.

### Preparar o VS Code (Linux)

1. Na primeira configuração, instale as extensões **Python** e **Pylance** da
   Microsoft, se ainda não estiverem instaladas.
2. Na primeira configuração deste projeto, crie o ambiente virtual e instale
   as dependências:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Abra a pasta do projeto no VS Code. As configurações do workspace selecionam
   `.venv/bin/python` como interpretador e ativam o ambiente nos novos terminais.
   Se o VS Code já estava aberto, selecione `.venv/bin/python` uma vez em
   `Python: Select Interpreter` (`Ctrl+Shift+P`).

Depois disso, não precisa recriar o ambiente nem reinstalar dependências a cada
uso. Para executar, abra `Terminal > Run Task` (`Ctrl+Shift+P` → `Tasks: Run
Task`) e escolha **Comparativo: executar testes**, **Comparativo: verificar
ambiente** ou **Comparativo: gerar gráficos**. A tarefa de gerar gráficos só
funciona depois de criar `dados/indicadores.csv` com observações validadas.

O diagnóstico informa a versão e o caminho do Python efetivamente selecionado.

### Formato dos dados

Use [dados/indicadores_modelo.csv](./dados/indicadores_modelo.csv) como
referência para o cabeçalho; as colunas estão descritas na seção 15 da
especificação. Cada linha representa uma observação de uma série. Preencha
apenas dados reais conferidos na fonte e registre período, datas de início e fim
do período (`AAAA-MM-DD`), tipo de dado (`observado`, `revisado`, `preliminar`
ou `estimativa`), data de acesso, unidade, URL e método. `validada` deve ser
`sim` somente depois da conferência editorial. Números usam ponto como
separador decimal.

Os períodos presidenciais estão em [dados/governos.csv](./dados/governos.csv),
conferidos em fontes oficiais em 2026-10-06. Cada indicador candidato e suas
ressalvas estão em
[dados/dicionario_indicadores.csv](./dados/dicionario_indicadores.csv).

Execute localmente, depois de criar `dados/indicadores.csv` preenchido:

```bash
python analise_comparativo.py --input dados/indicadores.csv --output saida
```

O script recusa linhas sem documentação, não validadas, com ano, valor ou
datas inválidos, data de acesso futura, URLs fora de HTTP(S), linhas com
colunas a mais, anos duplicados ou períodos sobrepostos na mesma série e
unidades inconsistentes. Cada gráfico mostra só pontos observados, posicionados
no meio do período de referência. Assim, o ano PRODES (agosto–julho) não é
convertido silenciosamente em ano-calendário. Use `--sem-governos` para gerar
gráficos sem as faixas presidenciais.

### Coleta

Cada série tem um script em [coleta/](./coleta/). O script lê o arquivo bruto
salvo sem edição em `dados/brutos/` e grava as linhas da série em
`dados/indicadores.csv`, sempre com `validada=nao`. Por exemplo:

```bash
python coleta/prodes_amazonia.py
python coleta/ipca.py
python coleta/pib.py
python coleta/atlas_violencia.py
python coleta/sim_mulheres.py
python coleta/sinesp_feminicidio.py   # ~10 min; baixe antes as bases (MANIFESTO.csv)
```

Rodar uma coleta de novo não apaga conferências já feitas: uma linha idêntica
à anterior mantém `validada=sim`, e uma linha com qualquer campo alterado volta
para `nao`.

Para cada série saem dois gráficos, cada um em versão larga e de celular:

- **principal** (`<serie>.png`): barras com o valor escrito, só nos últimos
  mandatos de Bolsonaro (2019–2022) e Lula III (desde 2023), conforme a
  ADR-013. Use `--recorte` para escolher outros governos;
- **histórico** (`<serie>--historico.png`): todos os anos desde 2002, com
  faixas de todos os governos.

Para ver os gráficos antes da conferência, rode a tarefa **Comparativo: gerar
prévia (não publicar)** ou `python analise_comparativo.py --previa`. Ela aceita
linhas com `validada=nao`, grava em `previa/` (versionada só para revisão interna) e
marca cada imagem com "PRÉVIA — DADOS NÃO CONFERIDOS — NÃO PUBLICAR". Todas as
outras validações continuam valendo.

### Conferência

1. Rode a tarefa **Conferência: verificar e gerar planilha**. Ela baixa cada
   série de novo por um caminho independente (API SIDRA "values", TabNet do
   SIM/DATASUS e notícias do INPE), compara valor a valor e gera
   `conferencia/conferencia_comparativo_v1_AAAAMMDD.xlsx` no padrão Mangue.
2. Na aba **Conferência**, confira à mão as linhas `MANUAL`, `DIVERGE` e com
   pendência e faça uma amostra das linhas `OK`. Escolha `aprovar` ou
   `rejeitar` em `decisao` e assine em `conferido_por`. Leia também a aba
   **Pendências**.
3. Rode `python conferencia/aplicar.py <planilha>`. O script marca
   `validada=sim` só nas linhas aprovadas, assinadas e com valor inalterado, e
   registra quem aprovou em `conferencia/registro_conferencia.csv`.

Cada indicador coletado precisa de uma nota de contexto no dicionário
(`indicador_csv` e `nota_grafico`), exibida no rodapé do gráfico. Sem ela, o
script não gera o gráfico.

Depois de conferir cada valor na fonte, troque `nao` por `sim` e rode a tarefa
**Comparativo: gerar gráficos**. Os PNGs aparecem em `saida/` e abrem no VS
Code com um clique. `saida/resumos.md` tem pré-visualização com `Ctrl+Shift+V`.

### Rodar no Google Colab

Faça upload de `analise_comparativo.py`, de `dados/governos.csv`, de
`dados/dicionario_indicadores.csv` e do CSV preenchido em uma célula:

```python
from google.colab import files

arquivos = files.upload()
csv_enviado = next(
    nome for nome in arquivos
    if nome.lower().endswith(".csv")
    and nome not in {"governos.csv", "dicionario_indicadores.csv"}
)
```

Instale as dependências e rode o mesmo script em outra célula:

```python
%pip install -q pandas matplotlib
!python analise_comparativo.py --input "{csv_enviado}" --governos governos.csv --dicionario dicionario_indicadores.csv --output saida
```

Para baixar os arquivos gerados:

```python
!zip -qr saida.zip saida
files.download("saida.zip")
```

O primeiro protótipo gera gráficos de evolução temporal; não calcula um
“vencedor”, não compara atividade legislativa a resultados presidenciais e não
prova causalidade. Fontes, indicadores e períodos continuam sujeitos à
homologação definida na especificação. O plano e as tarefas de descoberta estão em
[plan.md](./specs/001-comparativo-presidencial/plan.md) e
[tasks.md](./specs/001-comparativo-presidencial/tasks.md).
