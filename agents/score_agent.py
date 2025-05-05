import re
import os
from dotenv import load_dotenv
from typing import Dict, List
import math

from review_analysis_agent import RestaurantScores

from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.agents import initialize_agent, AgentType

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_MESSAGE_PROMPT_TEMPLATE = """
    Voçe é um avaliador de restaurantes. Seu papel é obter a nota final
    com base nas notas de comida e atendimento ao cliente. 
    A formula para a nota final é bem conhecida e você possui, como ferramenta,
    a função calculate_overall_score, para calcula-la.
    
    Use sua tool para o calculo da nota e não faça suposições. 
    """
    
HUMAN_MESSAGE_PROMPT_TEMPLATE = """
    Entrada do usuário: 
    {scores_dict}
"""

def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    num_scores = len(food_scores)
    final_sum = 0

    for i in num_scores:
        final_sum += math.sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(num_scores * math.sqrt(125)) * 10

    return {
        restaurant_name: float(f"{final_sum:.3f}")
    }

class ScoreAgent:
    """Essa classe é responsável por calcular a nota final de um restaurante, com base nas notas de comida e atendimento ao cliente."""
    
    def __init__(self):
        self.agent_config = {
            "model": "gpt-4",
            "temperature": 0,
        }
        
        self.agent = ChatOpenAI(**self.agent_config)
        
        tool_calculate_overall_score = Tool.from_function(
            func=calculate_overall_score,
            name="calculate_overall_score",
            description="Calcula a nota final de um restaurante com base nas notas de comida e atendimento ao cliente.",
            return_direct=True,
        )
        
        self.score_agent = initialize_agent(
            tools=[self.tool_calculate_overall_score],
            llm=self.agent,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
        )
        
        def get_prompt(scores_dict: RestaurantScores) -> str:
            return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE_PROMPT_TEMPLATE),
            HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE_PROMPT_TEMPLATE)
        ]).format_prompt(
            scores_dict=scores_dict,
            format_instructions=self.parser.get_format_instructions()
        )
        
        def run_score_agent(self, scores_dict: RestaurantScores):
            prompt = self.get_prompt(scores_dict)
            response =  self.score_agent.run(prompt)
            
            return response