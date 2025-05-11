import re
import os
from dotenv import load_dotenv
from typing import Dict, List
import math

from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.agents import initialize_agent, AgentType

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_MESSAGE_PROMPT_TEMPLATE = """
    Você é um avaliador de restaurantes. Seu papel é avaliar as avaliações 
    dadas à um restaurante pelos usuários e associar essa avaliação
    a uma nota de 1 a 5, para dois casos: Uma nota para a comida e outra para o 
    atendimento ao cliente. 
    
    Os criterios para a avaliação sao muito bem definidos e você deve apenas segui-lo:
    
        Os critérios são os seguintes: 
            {scores_dict}
            
    Siga à atentamente os critérios dados e não faça suposições. Atribua uma nota para 
    comida e outra para atendimento ao cliente para cada avaliação. Ou seja, caso um 
    restaurante tenha recebido 3 avaliações, você deve retornar, no campo "food_scores", 
    uma lista com 3 notas, e no campo "customer_service_scores" uma lista com 3 notas,
    cada nota referente a uma avaliação.
    
    Você ira receber um dicionario cuja chave é o nome do restaurante e o valor é uma lista de avaliações.
    """
    
HUMAN_MESSAGE_PROMPT_TEMPLATE = """
    Aqui estão as avaliações do restaurante: 
    {review}. 
    
    Me retorne as respostas seguinte essas instruções: 
    {format_instructions}.
    """

class RestaurantScores(BaseModel):
    """ Sempre se essa ferramenta para estruturar a resposta para o usuário"""
    restaurant_name: str = Field(description="Contém o nome do restaurante")
    description: str = Field(description="Breve descrição das classificações que o restaurante recebeu")
    food_scores: list[int] = Field(description="Lista de notas para a comida, cada valor se refere a uma única avaliação")
    customer_service_scores: list[int] = Field(description="Lista de notas para o atendimento, cada valor se refere a uma única avaliação")

class ReviewAnalysisAgent:
    """Essa classe é responsável por classificar, numericamente, as avaliações dos restaurantes."""

    def __init__(self):
        
        self.agent_config = {
            "model": "gpt-4o",
            "temperature": 0,
        }
        
        self.parser = PydanticOutputParser(pydantic_object=RestaurantScores)
        self.agent = ChatOpenAI(**self.agent_config).with_structured_output(RestaurantScores)
        self.scores = {
            1: ["horrível", "nojento", "terrível"],
            2: ["ruim", "desagradável", "ofensivo"],
            3: ["mediano", "sem graça", "irrelevante"],
            4: ["bom", "agradável", "satisfatório"],
            5: ["incrível", "impressionante", "surpreendente"]
        }
        
    def get_prompt(self, reviews: dict[str, list[str]]) -> str: 
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE_PROMPT_TEMPLATE),
            HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE_PROMPT_TEMPLATE)
        ]).format_prompt(
            review=reviews,
            scores_dict=self.scores,
            format_instructions=self.parser.get_format_instructions()
        )
        
    def evaluate_reviews(self, reviews: dict[str, list[str]]) -> RestaurantScores:
        prompt = self.get_prompt(reviews)
        response = self.agent.invoke(prompt)
        
        return response

