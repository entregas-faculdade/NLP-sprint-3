---
status: "🟠 Em revisão"
dominio: pln-rag
prioridade: alta
---

# Pipeline RAG Avançado (Chunking e Re-ranking)

## 1. Visão Geral
Esta spec define a evolução do módulo de recuperação (retrieval) semântica. O objetivo é implementar um sistema de RAG (Retrieval-Augmented Generation) que processe manuais técnicos do ativo com inteligência e utilize informações de telemetria em tempo real para influenciar a busca.

## 2. Regras de Negócio
1. Os documentos técnicos (manuais, fichas) devem passar por um processo de chunking semântico.
2. O chunking deve preservar cabeçalhos técnicos e o contexto imediato (coerência semântica).
3. Os chunks devem ser vetorizados e indexados utilizando FAISS (ou banco vetorial equivalente).
4. Durante a busca, o sistema deve implementar uma etapa de re-ranking (ou filtragem híbrida).
5. O re-ranking deve priorizar chunks de documentos associados aos equipamentos que estão atualmente com "alertas ativos" ou em falha no estado operacional.

## 3. Critérios de Aceite
- [ ] Rotina de pré-processamento de texto implementa chunking consciente de estrutura (ex: usando separadores de Markdown ou LangChain RecursiveCharacterTextSplitter).
- [ ] Indexação vetorial está funcionando e suporta consulta rápida (K-NN).
- [ ] O retriever ajusta o peso ou a ordem dos resultados baseado no estado operacional atual (alertas ativos).
- [ ] O pipeline é capaz de recuperar trechos técnicos relevantes quando perguntado sobre falhas.

## 4. Plano de Testes
### Unitários
- Teste da lógica de divisão de texto (chunking) garantindo que os cabeçalhos não sejam perdidos.
- Teste do sistema de re-ranking garantindo que um equipamento com alerta ativo suba na prioridade da busca.
### Contrato/API
- N/A. (A API será coberta na Spec 05).
### E2E
- Consulta simulando um estado de alerta em um motor específico e verificando se os top-k chunks recuperados são pertinentes àquele motor e ao problema reportado.
