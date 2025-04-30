from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import re
import math
from dotenv import load_dotenv

data_path = "desafio-agents/restaurantes.txt"

load_dotenv()

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    restaurant_reviews_dict = {
        restaurant_name : []
    }

    with open(data_path, "r") as file:
        for line in file:
            review_name = re.match("^[^.]+", line)

            if review_name.group() == restaurant_name:
                restaurant_reviews_dict[restaurant_name].append(line[review_name.end():].strip())
        
    return restaurant_reviews_dict  

def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    num_scores = len(food_scores)
    final_sum = 0

    for i in num_scores:
        final_sum += math.sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(num_scores * math.sqrt(125)) * 10

    return {
        restaurant_name: float(f"{final_sum:.3f}")
        }

def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    # TODO
    # Função auxiliar opcional.
    # Pode ser útil organizar mensagens/prompts dentro de uma função que retorna uma string.
    # Por exemplo, você pode usar esta função para retornar um prompt que o agente de busca de dados 
    # usará para obter avaliações de um restaurante específico.
    pass

# TODO: sinta-se à vontade para escrever quantas funções adicionais quiser.
# Não modifique a assinatura da função "main".
def main(user_query: str):
    entrypoint_agent_system_message = "" # TODO
    # Exemplo de configuração de LLM para o agente de entrada
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    # O agente principal de entrada/supervisor
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Obtém as avaliações de um restaurante específico.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # TODO
    # Crie mais agentes aqui.

    # TODO
    # Preencha o argumento de `initiate_chats` abaixo, chamando os agentes corretos sequencialmente.
    # Se você decidir usar outro padrão de conversação, sinta-se à vontade para ignorar este código.

    # Descomente assim que iniciar o chat com pelo menos um agente.
    # result = entrypoint_agent.initiate_chats([{}])
    
# NÃO modifique o código abaixo.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Certifique-se de incluir uma consulta para algum restaurante ao executar a função main."
    main(sys.argv[1])