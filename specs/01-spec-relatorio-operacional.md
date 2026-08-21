---
status: drafting
dominio: inteligencia-operacional
prioridade: alta
---

# Sistema de Geração de Alertas e Relatório Operacional

## 1. Visão Geral
Este módulo é responsável por processar dados de telemetria dos sensores e gerar alertas descritivos em linguagem natural. Além disso, deve consolidar esses eventos em um relatório diário ou semanal que sumarize as tendências, equipamentos em risco e apresente rastreabilidade aos dados de origem.

## 2. Regras de Negócio
1. O sistema deve receber um fluxo ou lote de leituras de sensores (temperatura, aceleração).
2. Devem existir ao menos três templates de alerta (Leve, Moderado, Crítico).
3. Os templates devem descrever explicitamente o **sensor afetado** e a **magnitude do desvio**.
4. O relatório agregado deve consolidar os alertas do período e identificar tendências de degradação.
5. O relatório deve ser gerado utilizando técnicas de NLG (ex: via prompt para LLM).
6. O texto gerado do relatório deve ser avaliado contra um referencial usando métricas ROUGE.

## 3. Critérios de Aceite
- [ ] A função de geração de alertas mapeia corretamente os 3 níveis de severidade com templates dinâmicos contendo sensor e tipo de desvio.
- [ ] Existe uma função ou script que agrupa alertas e gera um relatório consolidado.
- [ ] O relatório consolidado referencia sensores e equipamentos específicos.
- [ ] O ROUGE score do relatório gerado é calculado contra um ground truth pré-definido.
- [ ] Um checklist manual ou automatizado de "Clareza, Precisão e Utilidade" é aplicado e documentado.

## 4. Plano de Testes
### Unitários
- Mapeamento correto dos limites numéricos para severidade (Leve, Moderado, Crítico).
- Formatação correta das strings de alerta (substituição de variáveis).
### Contrato/API
- N/A. O escopo desta spec foca na lógica interna em script/notebook. O contrato será testado na Spec 05.
### E2E
- Validação da saída do pipeline fim-a-fim: entrada de CSV simulado gerando o relatório final textual e as métricas.
