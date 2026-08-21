import nbformat
import sys

def update_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    new_retriever_llm = """from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# 1. Configuração da Memória
memory = ConversationBufferMemory(memory_key="chat_history", input_key="pergunta")

# 2. Definição do Prompt Avançado
template = \"\"\"Você é um Assistente Técnico Especialista em Motores Elétricos.
Sua função é auxiliar operadores no diagnóstico de falhas, sempre baseando-se RIGOROSAMENTE nos manuais fornecidos.

[ESTADO ATUAL DO ATIVO (TELEMETRIA/ALERTAS)]
{alerta_atual}

[MANUAIS RECUPERADOS]
{contexto}

[HISTÓRICO DA CONVERSA]
{chat_history}

[NOVA PERGUNTA]
{pergunta}

INSTRUÇÕES:
1. Responda à pergunta baseando-se APENAS nos [MANUAIS RECUPERADOS].
2. Se a informação não estiver lá, diga explicitamente: "Não possuo informações suficientes na documentação técnica recuperada".
3. Leve em consideração o [ESTADO ATUAL DO ATIVO] para contextualizar a gravidade da situação.
4. Ao final da resposta, classifique seu "Nível de Confiança" (ALTO, MÉDIO, BAIXO) e cite as fontes (ex: "Fonte: Manual do Motor W22").

Resposta:\"\"\"

prompt_template = PromptTemplate(
    input_variables=["alerta_atual", "contexto", "chat_history", "pergunta"],
    template=template
)

# 3. Cadeia de Conversação (Simulada para rodar sem API Key no Colab local)
# Em produção, usariamos: llm = ChatOpenAI(temperature=0.0) ou HuggingFacePipeline()
# chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)

def chat_troubleshooting(user_input, alerta_ativo):
    # a. Recuperar documentos (Re-ranking)
    contexto_recuperado, _ = buscar_contexto_com_rerank(user_input, alerta_ativo)
    
    # b. Carregar histórico
    historico = memory.buffer
    
    # c. Formatar Prompt
    prompt_formatado = prompt_template.format(
        alerta_atual=alerta_ativo,
        contexto=contexto_recuperado,
        chat_history=historico,
        pergunta=user_input
    )
    
    print("\\n=== PROMPT ENVIADO AO LLM ===")
    print(prompt_formatado)
    print("===============================\\n")
    
    # Simulação da Resposta do LLM 
    if "limites de vibração" in user_input.lower():
        resposta_llm = "A vibração máxima permitida é de 2,8 mm/s RMS conforme a norma ISO 10816, que se aplica ao Motor W22 Plus. Dado que a telemetria atual indica 0.47g, é crucial monitorar a evolução para não ultrapassar este limite.\\n\\nNível de Confiança: ALTO\\nFonte: Manual do Motor W22 Plus"
    elif "como devo proceder" in user_input.lower():
        resposta_llm = "Conforme o manual, verifique o alinhamento do acoplamento: o desalinhamento angular máximo deve ser de 0,1 mm e o paralelo de 0,05 mm. Tente reajustar seguindo esses parâmetros.\\n\\nNível de Confiança: ALTO\\nFonte: Manual do Motor W22 Plus"
    else:
        resposta_llm = "Não possuo informações suficientes na documentação técnica recuperada para responder."
    
    # d. Salvar na memória
    memory.save_context({"pergunta": user_input}, {"resposta": resposta_llm})
    
    return resposta_llm

alerta_ativo = "ALERTA CRÍTICO: Motor W22 Plus - Temperatura atingiu 47°C e vibração 0.47g."

print(">>> TURNO 1")
resposta = chat_troubleshooting("Quais são os limites de vibração aceitáveis?", alerta_ativo)
print(">>> RESPOSTA DO LLM:\\n" + resposta + "\\n")

print(">>> TURNO 2")
resposta = chat_troubleshooting("E como devo proceder para corrigir caso ultrapasse?", alerta_ativo)
print(">>> RESPOSTA DO LLM:\\n" + resposta + "\\n")
"""

    nb.cells[5].source = new_retriever_llm

    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
        
    print("Notebook atualizado com sucesso! (LLM Memory & Prompting)")

if __name__ == "__main__":
    update_notebook(sys.argv[1])
