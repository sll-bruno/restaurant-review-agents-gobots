from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import re
import math
from dotenv import load_dotenv
from langchain_core.tools import tool, Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
import unicodedata
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

    
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

grades_dict = {
    1: ["horrível", "nojento", "terrível"],
    2: ["ruim", "desagradável", "ofensivo"],
    3: ["mediano", "sem graça", "irrelevante"],
    4: ["bom", "agradável", "satisfatório"],
    5: ["incrível", "impressionante", "surpreendente"]
}

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    """ Description"""

    data_path = "restaurantes.txt"

    restaurant_reviews_dict = {
        restaurant_name : []
    }

    with open(data_path, "r", encoding="utf-8") as file:
        for line in file:
            review_name = re.match("^[^.]+", line)
            print(review_name.group())

            if review_name.group() == restaurant_name:
                restaurant_reviews_dict[restaurant_name].append(line[review_name.end() +1:].strip())
        
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
    
    grades_dict = {
    1: ["horrível", "nojento", "terrível"],
    2: ["ruim", "desagradável", "ofensivo"],
    3: ["mediano", "sem graça", "irrelevante"],
    4: ["bom", "agradável", "satisfatório"],
    5: ["incrível", "impressionante", "surpreendente"]
    }
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    fetch_data_agent = ChatOpenAI(model_name="gpt-4", temperature=0)

    tool_fetch_data = Tool.from_function(
        func=fetch_restaurant_data,
        name="fetch_restaurant_data",
        description="Essa função busca as avaliações de um restaurante específico. O nome do restaurante deve ser passado como argumento.",
    )
    
    tool_calculate_overall_score = Tool.from_function(
        func=calculate_overall_score,
        name="calculate_overall_score",
        description="Essa função calcula a nota geral de um restaurante com base nas notas de comida e atendimento ao cliente. Ela deve receber o nome do restaurante e as notas de comida e atendimento ao cliente como argumentos.",
    )

    fetch_data_agent = initialize_agent(
        tools=[tool_fetch_data],
        llm= fetch_data_agent,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    reviews = fetch_data_agent.run(f"Busque as avaliações do restaurante mencionado: {user_query}")
    print("hello world")
    print(reviews)
    
    class TuplaSaida(BaseModel):
        restaurant_name: str
        food_score: int
        customer_service_score: int
        
    parser = PydanticOutputParser(pydantic_object=TuplaSaida)
    
    
    get_review_grades_agent = ChatOpenAI(model_name="gpt-4", temperature=0)
    get_review_grades_template = ChatPromptTemplate([
        SystemMessagePromptTemplate.from_template(
            """Você é um avaliador de restaurantes. Seu papel é avaliar as avaliações dadas à um restaurante pelos usuários e associar essa avaliação
            a uma nota de 1 a 5, para dois casos: Uma nota para a comida e outra para o atendimento ao cliente. Os criterios para a avaliação sao muito bem definidos e você deve apenas segui-lo:
                
                Os critérios são os seguintes: 
                    {grades_dict}
                    
            Siga à risca os critérios dados e não faça suposições. Retorne tuplaS com duas notas, a primeira para comida e a segunda para atendimento ao cliente, e NADA mais do que isso.
            
            Você ira receber um dicionario cuja chave é o nome do restaurante e o valor é uma lista de avaliações. Para cada avaliação, retorne uma tupla
            """
        ),
        HumanMessagePromptTemplate.from_template(
            """Aqui estão as avaliações do restaurante: {review}. Me retorne as respsotas seguinte essas instruções: {format_instructions}."""
        )
    ])
    
    chain = get_review_grades_template | get_review_grades_agent | parser
    result = chain.invoke(
    input={
        "grades_dict": grades_dict,
        "review": reviews,
        "format_instructions": parser.get_format_instructions()
    }
)
    print(result)
    print(type(result))
    print(result.food_score)
    print(type(result.food_score))
    #grades = get_review_grades_agent.invoke(
    #    get_review_grades_template.format_messages(grades_dict = grades_dict,review=reviews, format_instructions = parser.get_format_instructions())
    #)
    
    
    score_agent = ChatOpenAI(model_name="gpt-4", temperature=0)
    
    """entrypoint_agent_system_message = "" # TODO
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
    # result = entrypoint_agent.initiate_chats([{}])"""
    
# NÃO modifique o código abaixo.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Certifique-se de incluir uma consulta para algum restaurante ao executar a função main."
    main(sys.argv[1])