---
status: "🟠 Em revisão"
dominio: infraestrutura-inferencia
prioridade: media
---

# Sistema de Inferência Unificado

## 1. Visão Geral
Como o código será desenvolvido em notebooks Colab para fins acadêmicos e analíticos, o sistema também deve possuir um modo de operação contínuo (uma classe orquestradora ou pequena API) para permitir a demonstração "viva" da solução (onde o operador entra com uma pergunta e o sistema executa o fluxo inteiro).

## 2. Regras de Negócio
1. O sistema deve centralizar a inicialização do RAG (Index e Encoder) e do LLM em uma única instância gerenciada.
2. Deve existir um ponto de entrada para o fluxo de IoT/Alertas (receber novos dados CSV/JSON e atualizar o "Estado Operacional Atual").
3. Deve existir um ponto de entrada para o Chat (receber a `query` do operador e o `user_id` ou `session_id` para controle da memória).
4. O módulo de chat deve orquestrar sequencialmente:
   - Recuperação (Search) no RAG aplicando o filtro do Estado Operacional.
   - Formatação do Prompt com Memória, Estado e Chunks.
   - Invocação do LLM generativo.
   - Retorno da resposta acompanhada das referências usadas.

## 3. Critérios de Aceite
- [ ] Módulo Python centralizador (`InferenceEngine` ou similar) implementado, instanciando LLM e FAISS uma única vez.
- [ ] Função/método `chat_interaction(query)` retorna a resposta com clareza e executa a atualização de memória internamente.
- [ ] O sistema permite rodar as avaliações da Spec 04 através de uma chamada de método assíncrono/lote.
- [ ] Previsão para gravação em vídeo: a interface (seja texto via CLI, ipywidgets no Colab, ou Gradio/Streamlit simples) roda limpa nos 3 cenários de demonstração sem quebras por erro de dependência.

## 4. Plano de Testes
### Unitários
- Validação da injeção de dependência na classe gerenciadora (garantir que modelos só são carregados uma vez).
### Contrato/API
- Caso exposto como API FastAPI: verificar contratos de Request (JSON com query/session) e Response (JSON com answer/sources).
### E2E
- Executar um fluxo de simulação onde dados falsos de sensores entram, e imediatamente um usuário pergunta sobre o problema, garantindo o funcionamento do ciclo em memória.
