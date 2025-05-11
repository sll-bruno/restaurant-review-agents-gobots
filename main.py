from typing import Dict, List
import sys
import os
import re

from agents.fetch_data_agent import FetchDataAgent
from agents.review_analysis_agent import ReviewAnalysisAgent
from agents.score_agent import ScoreAgent

    
def main(user_query: str):
    
    #Instancia os agentes
    fetch_data_agent = FetchDataAgent()
    review_analysis_agent = ReviewAnalysisAgent()
    score_agent = ScoreAgent()
    
    avaliacoes = fetch_data_agent.fetch_data(user_query)
    
    # Avalia as avaliações do restaurante
    restaurant_scores = review_analysis_agent.evaluate_reviews(avaliacoes)
    
    print(restaurant_scores)
    # Calcula a nota final do restaurante
    final_score = score_agent.run_score_agent(restaurant_scores)
    print(final_score)
    
    
    
    
    
    
    
# NÃO modifique o código abaixo.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Certifique-se de incluir uma consulta para algum restaurante ao executar a função main."
    main(sys.argv[1])