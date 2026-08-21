---
status: "🟢 Aprovada"
dominio: pln-assistente-conversacional
prioridade: alta
---

# Assistente Conversacional de Troubleshooting com Memória

## 1. Visão Geral
Esta spec detalha a implementação do cérebro conversacional da plataforma. Um LLM gerador de texto será integrado ao retriever RAG, atuando como um especialista de manutenção que atende os operadores e possui memória da conversa em andamento e consciência do estado dos ativos.

## 2. Regras de Negócio
1. O LLM deve receber um System Prompt com a persona "Assistente Técnico Especialista em Motores Elétricos".
2. O prompt deve instruir rigorosamente o modelo a referenciar as fontes (documentos) fornecidas pelo RAG.
3. O modelo deve informar o "nível de confiança" na resposta baseada no contexto fornecido.
4. O contexto da chamada (prompt final) deve incluir: 
   - A pergunta atual do operador.
   - O histórico recente da conversa (memória de curto prazo).
   - O contexto dos chunks recuperados (RAG).
   - O resumo atual dos alertas/estado operacional da planta (Entregável 1).
5. O LLM deve ser capaz de negar a responder ou admitir que não sabe caso a pergunta esteja fora do escopo ou o RAG não retorne documentos úteis.

## 3. Critérios de Aceite
- [ ] System prompt definido e documentado com as instruções da persona.
- [ ] Integração bem-sucedida entre o RAG (retriever) e o LLM (chain de geração).
- [ ] O estado operacional e os resumos de alertas são formatados e injetados na chamada do LLM.
- [ ] Respostas do LLM citam explicitamente a origem da informação (ex: "Conforme o manual X...").
- [ ] O LLM mantém coerência caso haja perguntas de follow-up dependentes da mensagem anterior.

## 4. Plano de Testes
### Unitários
- Construção correta do prompt final (verificar concatenação de histórico, contexto e alertas).
- Verificação do tratamento de contexto vazio (fallback do LLM para perguntas fora do escopo).
### Contrato/API
- N/A.
### E2E
- Simulação de uma conversa com 3 turnos para testar a retenção de memória e a fidelidade aos manuais recuperados.
