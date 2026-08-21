---
status: "🟢 Aprovada"
dominio: pln-avaliacao
prioridade: alta
---

# Framework de Avaliação de RAG e Chat

## 1. Visão Geral
Define as métricas e os processos de avaliação de qualidade do pipeline de RAG e das respostas do Assistente Conversacional. Garantirá que as respostas não sejam alucinadas e que sejam relevantes ao problema perguntado.

## 2. Regras de Negócio
1. Construção de um banco de dados de avaliação (Ground Truth) contendo exatamente 20 perguntas típicas de troubleshooting.
2. Cada pergunta deve estar associada a uma resposta de referência correta, extraída manualmente dos manuais.
3. Para cada resposta gerada pelo LLM na bateria de testes, calcular 3 métricas principais:
   - **Faithfulness**: A resposta gerada é sustentada unicamente pelos documentos recuperados?
   - **Answer Relevancy**: A resposta gerada responde de fato à pergunta do usuário?
   - **Context Precision**: Os chunks recuperados pela busca semântica contêm informações relevantes para a pergunta?
4. A avaliação deve ser demonstrada passando por 3 cenários de falha distintos: Anomalia Elétrica, Anomalia Mecânica e Consulta de Procedimento Preventivo.
5. Devem ser catalogados e documentados os limites do sistema (ex: perguntas impossíveis de responder).

## 3. Critérios de Aceite
- [ ] Conjunto de avaliação de 20 pares Pergunta-Resposta criado e disponível (ex: JSON ou CSV).
- [ ] Script automatizado que roda as 20 perguntas contra o pipeline RAG+LLM e consolida os resultados.
- [ ] Geração de relatório com as pontuações médias de Faithfulness, Answer Relevancy e Context Precision.
- [ ] Documento ou artefato listando os "limites do sistema" identificados e as estratégias de mitigação.

## 4. Plano de Testes
### Unitários
- N/A (Esta spec consiste primariamente nos próprios testes de qualidade).
### Contrato/API
- N/A.
### E2E
- A execução do notebook/script de avaliação deve iterar sobre as 20 questões e emitir o score global do sistema sem interrupções.
