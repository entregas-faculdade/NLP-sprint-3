import nbformat
import sys

def update_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Nova célula Inference Engine
    new_engine_code = """class InferenceEngine:
    def __init__(self):
        print("🔧 Inicializando Inference Engine...")
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="pergunta")
        self.alerta_atual = "Nenhum alerta ativo. Sistema em operação normal."
        print("✅ Engine Pronta! (Memória, RAG e LLM Mockado Carregados)")
        
    def update_telemetry(self, novo_alerta):
        self.alerta_atual = novo_alerta
        print(f"\\n⚠️ [TELEMETRIA ATUALIZADA]: {self.alerta_atual}\\n")
        
    def chat(self, pergunta):
        # 1. Recupera chunks
        contexto, _ = buscar_contexto_com_rerank(pergunta, self.alerta_atual, top_k=2)
        
        # 2. Formata Prompt
        historico = self.memory.buffer
        
        # 3. MOCK do LLM (Em produção chamaria a LLMChain)
        p_low = pergunta.lower()
        if "limites de vibração" in p_low or "vibração máxima" in p_low:
            resposta = "A vibração máxima permitida é de 2,8 mm/s RMS (Norma ISO 10816).\\nFonte: Manual W22 Plus"
        elif "proceder" in p_low or "corrigir" in p_low:
            resposta = "Verifique o alinhamento do acoplamento: o desalinhamento angular máximo é de 0,1 mm.\\nFonte: Manual W22 Plus"
        elif "temperatura" in p_low:
            resposta = "A temperatura máxima do enrolamento é de 155°C (Classe F).\\nFonte: Manual 1LA7"
        elif "olá" in p_low or "oi" in p_low:
            resposta = "Olá! Sou o Assistente Técnico Especialista em Motores. Como posso ajudar com a telemetria atual?"
        else:
            resposta = "Não possuo informações suficientes na documentação técnica recuperada para responder de forma segura."
            
        # 4. Salva no buffer
        self.memory.save_context({"pergunta": pergunta}, {"resposta": resposta})
        return resposta
"""

    # Nova célula interativa
    new_cli_code = """# ==========================================
# 🚀 DEMONSTRAÇÃO INTERATIVA (PITCH / BANCADA)
# ==========================================
# Instruções:
# 1. Execute esta célula.
# 2. Digite suas perguntas na caixa de texto.
# 3. Digite 'sair' para encerrar a simulação.
# ==========================================

engine = InferenceEngine()

# Simulando a entrada de um alerta de telemetria grave
engine.update_telemetry("ALERTA CRÍTICO: Motor W22 Plus - Temperatura atingiu 47°C e vibração 0.47g.")

print("==========================================")
print("🤖 ASSISTENTE TÉCNICO V1.0 INICIADO")
print("==========================================")
print("Dica de teste: Pergunte sobre os limites de vibração ou temperatura.")

# Descomente o bloco abaixo para usar no Jupyter/Colab de forma interativa:
'''
while True:
    user_input = input("👤 Operador: ")
    if user_input.lower() in ['sair', 'exit', 'quit']:
        print("🤖 Assistente: Encerrando sessão. Bom trabalho!")
        break
        
    resposta = engine.chat(user_input)
    print(f"🤖 Assistente: {resposta}\\n")
'''
# Apenas rodando um teste fixo para não travar a execução headless
print("👤 Operador (mock): Quais os limites de vibração?")
print(f"🤖 Assistente: {engine.chat('Quais os limites de vibração?')}\\n")
"""

    cell_engine = nbformat.v4.new_code_cell(source=new_engine_code)
    cell_cli = nbformat.v4.new_code_cell(source=new_cli_code)

    nb.cells.extend([cell_engine, cell_cli])

    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
        
    print("Notebook atualizado com a InferenceEngine e CLI de Demonstração!")

if __name__ == "__main__":
    update_notebook(sys.argv[1])
