import logging
import os
from openai import OpenAI
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResearchGenerator:
    """
    Generates Wall Street style research notes using OpenAI API
    based on quantitative features and SHAP values.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Research Notes will not be generated.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            
        self.system_prompt = (
            "You are a quantitative research analyst at a top Wall Street firm specializing in prediction markets. "
            "Write a concise, professional research note (max 2 paragraphs) explaining why the provided market is currently ranked as a top opportunity. "
            "Base your analysis STRICTLY on the provided quantitative metrics (Volume, Liquidity, Velocity) and SHAP feature importances. "
            "SHAP values explain how much each feature contributed to the model's high opportunity score. "
            "Do not hallucinate external events unless absolutely obvious from the market title. Maintain a formal, analytical tone."
        )

    def generate_note(self, market_title: str, metrics: Dict[str, Any], shap_values: Dict[str, float]) -> str:
        if not self.client:
            return "No OpenAI API key provided."

        user_prompt = f"""
        Market Title: {market_title}
        
        Quantitative Metrics:
        {metrics}
        
        SHAP Feature Contributions (Model Explainability):
        {shap_values}
        
        Please provide the research note.
        """

        try:
            logger.info(f"Generating research note for market: {market_title[:30]}...")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=250
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate research note: {e}")
            return f"Error generating note: {e}"
