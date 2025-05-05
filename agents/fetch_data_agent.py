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
    Você é um assistente que busca dados de restaurantes em um banco de dados.
    Seu papel é avaliar à qual restaurante o usuário se refere e buscar as avaliações do 
    restaurante mencionado. 

    Use a ferramenta disponível para retornar as avaliações do restaurante.

    Retorne os dados *exatamente** no seguinte formato JSON:

    {format_instructions}
    """
    
HUMAM_MESSAGE_PROMPT_TEMPLATE = """
    Entrada do usuário: 
    {query}
    """

class RestaurantReviews(BaseModel):
    Avaliacoes: Dict[str, List[str]]  

class FetchDataAgent:    
    
    def __init__(self):
        
        self.data_path = "restaurantes.txt"
        self.encoding = "utf-8" 
        self.agent_config = {
            "model": "gpt-4o",
            "temperature": 0,
        }
        self.fetch_data_agent = ChatOpenAI(**self.agent_config)
                
        self.tool_fetch_data = Tool.from_function(
            func= self.fetch_restaurant_data,
            name="fetch_restaurant_data",
            description="Essa função busca as avaliações de um restaurante específico. O nome do restaurante deve ser passado como argumento.",
        )
        
        self.fetch_data_agent = initialize_agent(
            tools=[self.tool_fetch_data],
            llm= self.fetch_data_agent,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        self.parser = PydanticOutputParser(pydantic_object=RestaurantReviews)

    def fetch_restaurant_data(self,restaurant_name: str) -> Dict[str, List[str]]:
        """
            Função responsável por buscar as avaliações de um restaurante específico.
            O nome do restaurante deve ser passado como argumento.
            Retorna um dicionário com o nome do restaurante e as avaliações que ele recebeu.
        """
        restaurant_reviews_dict = {
            restaurant_name : []
        }

        with open(self.data_path, "r", encoding= self.encoding) as file:
            for line in file:
                review_name = re.match("^[^.]+", line)

                if review_name.group() == restaurant_name:
                    restaurant_reviews_dict[restaurant_name].append(line[review_name.end() +1:].strip())
            
        return restaurant_reviews_dict 
    
    def get_prompt(self, restaurant_query: str) -> str:
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE_PROMPT_TEMPLATE),
            HumanMessagePromptTemplate.from_template(HUMAM_MESSAGE_PROMPT_TEMPLATE)
        ]).format_messages(
            query=restaurant_query,
            format_instructions= self.parser.get_format_instructions()

        )
    
    def run_agent(self, query: str):
        """ Função responsável por executar o agente."""

        prompt = self.get_prompt(query)
        response = self.fetch_data_agent.invoke(prompt)
        return response

    
