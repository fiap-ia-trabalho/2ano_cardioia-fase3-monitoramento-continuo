# Relatório comparativo: regressão logística vs. modelo neuromórfico LIF

## Objetivo

Este estudo compara dois paradigmas de modelagem para séries temporais de saúde: um classificador tradicional baseado em features extraídas e um modelo bioinspirado em neurônios LIF. A pergunta principal é se a dinâmica temporal capturada por um modelo neuromórfico oferece vantagens reais em comparação com um baseline simples e interpretável.

## Metodologia

Foi gerado um conjunto sintético de janelas de séries temporais com padrões regulares e irregulares, simulando cenários de sinais vitais normais e anormais. Para cada janela, foram extraídas estatísticas clássicas e uma representação baseada em dinâmica de neurônios LIF.

A regressão logística foi treinada sobre as features estatísticas, enquanto o modelo LIF foi usado como codificador de dinâmica temporal para produzir um vetor de atributos de disparo e atividade. Por fim, ambos foram avaliados com métricas de classificação.

## Resultados

Os resultados demonstram que o baseline clássico tende a obter desempenho robusto em dados estruturados e bem separáveis. Seu grande diferencial é a simplicidade, a precisão e a facilidade de interpretação. Em contraste, o modelo LIF apresenta um comportamento mais sensível à dinâmica temporal e pode capturar variações transientes que indicadores estatísticos simples podem perder.

No entanto, o modelo LIF exige cuidado na definição de parâmetros como limiar, decaimento e reset. Isso impacta diretamente o desempenho e torna a implementação mais dependente de calibração. Em conjunto, o estudo sugere que a vantagem neuromórfica aparece mais claramente quando a temporalidade e os eventos discretos são centrais no problema.

## Discussão crítica

A regressão logística é uma referência forte para problemas em que as features são bem conhecidas. Ela costuma ser mais simples de treinar, explicar e depurar. O modelo LIF, por sua vez, é mais interessante em contextos onde a sinalização temporal e a dinâmica de entrada são fundamentais, como lida com padrões de risco, transientes e variações não lineares.

A principal limitação deste estudo é o uso de dados sintéticos. Em dados clínicos reais, a heterogeneidade, ruído, baixa amostra e falta de rótulos confiáveis podem afetar tanto o baseline quanto o modelo neuromórfico. Portanto, a interpretação precisa ser feita com cautela.

## Conclusão

A comparação mostra que não existe um vencedor absoluto. A regressão logística continua sendo excelente como baseline pela clareza e desempenho prático. O modelo LIF oferece um caminho mais bioinspirado e promissor para a modelagem temporal, mas exige mais ajustes, melhor calibração e validação em dados reais. Em cenários de saúde digital, a escolha depende do problema: interpretabilidade, tempo de treinamento e capacidade de capturar padrões temporais são critérios decisivos.
