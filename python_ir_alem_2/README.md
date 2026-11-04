# Inteligência Artificial em Séries Temporais de Saúde

Este projeto compara um classificador tradicional com um modelo neuromórfico inspirando-se em neurônios LIF (Leaky Integrate-and-Fire) para a análise de séries temporais de sinais vitais.

## Ir Além 1 e 2

Este trabalho foi estruturado como extensão do projeto principal de monitoramento contínuo em saúde digital e também atende às exigências dos desafios de inovação conhecidos como Ir Além 1 e Ir Além 2.

### Ir Além 1: comunicação automatizada com REST e RPA

No primeiro desafio, a ideia é ampliar a solução com automação de monitoramento e resposta inteligente a dados de sinais vitais. O fluxo inclui:

- cliente REST em Python;
- consumo de API com dados de monitoramento;
- avaliação de risco baseada em regras clínicas didáticas;
- geração de alerta automatizado;
- comunicação por e-mail em modo simulado.

Esse componente reforça a lógica de monitoramento proativo, em que a aplicação não apenas coleta dados, mas também interpreta sinais e responde automaticamente.

### Ir Além 2: inteligência artificial em séries temporais de saúde

No segundo desafio, a proposta é aplicar técnicas de IA para análise de séries temporais de sinais vitais e comparar modelos tradicionais com abordagens bioinspiradas. O foco aqui é:

- processamento temporal de sinais vitais;
- comparação entre regressão logística e modelo neuromórfico LIF;
- avaliação de desempenho por métricas clássicas;
- discussão crítica sobre vantagens, limitações e aplicabilidade real.

## Objetivo

Aplicar técnicas de IA para classificar padrões de saúde em janelas temporais de sinais vitais e comparar:

- Regressão logística como baseline tradicional.
- Modelo LIF como alternativa bioinspirada para exploração da dinâmica temporal.

## Estrutura do projeto

- `notebooks/analise_series_saude.ipynb`: notebook Python comentado com a análise completa.
- `src/health_series_ai.py`: script executável com geração de dados, treinamento e comparação dos modelos.
- `report/relatorio_comparativo.md`: relatório técnico em formato de duas páginas.
- `requirements.txt`: dependências do projeto.

## Execução

### Ir Além 1: REST + RPA

```bash
cd python_ir_alem_1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python3 mock_api.py
python3 app.py --patient Maria --temperature 39.2 --bpm 128 --idle-ms 65000
```

### Ir Além 2: IA em séries temporais

```bash
cd python_ir_alem_2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/health_series_ai.py
```

Para abrir o notebook:

```bash
jupyter notebook notebooks/analise_series_saude.ipynb
```

## Modelo comparado

### Regressão logística

- Vantagens: simplicidade, interpretabilidade e alta velocidade.
- Limitações: depende de features handcrafted e não modela diretamente a dinâmica temporal.

### Modelo LIF

- Vantagens: incorpora dinamismo temporal e inspiração biológica.
- Limitações: maior sensibilidade a parâmetros e menor interpretabilidade direta em comparação ao baseline clássico.

## Resultado esperado

O script produz:

- métrica de acurácia;
- F1-score;
- recall;
- matriz de confusão;
- comparação visual dos modelos;
- gráficos das séries e do desempenho.

## Vídeo do resultado

> O vídeo de apresentação deve ser publicado no YouTube como "não listado" e o link deve ser atualizado nesta seção.

Exemplo de placeholder:

```text
https://youtu.be/SEU_VIDEO_ID
```

## Observação

Este projeto é acadêmico e usa um gerador de séries sintéticas para ilustrar a comparação entre modelos de IA em sinais vitais. A ideia é demonstrar metodologia, comparação crítica e interpretação dos resultados, não substituir diagnóstico clínico real.
