# implementing gemini api

from langchain_google_genai import ChatGoogleGenerativeAI
import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(override=True)

class GenAi(object):
    def __init__(self,prompt:str,gemini_model:str|None = 'gemini-1.5-flash') -> None:
        self.prompt:str = prompt
        self.gemini_api:str = os.getenv("GEMINI_API_KEY")
        self.gemini_model:str = gemini_model

        self.llm:ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
            model= self.gemini_model,
            google_api_key= self.gemini_api
        )
        
        
    # def __repr__(self) -> str:
    #     return f"""
    #         {self.__init__.__dict__()}
    #         """
    
    def __convert_response_to_json(self,json_string):
        """
        Convert a string with JSON data into a JSON object.

        Args:
        json_string (str): A string containing JSON data.

        Returns:
        dict: A JSON object.
        """
        try:
            return json_string.replace('`',"").replace('json','')
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    def get_feedback(self)->str:
        """

        """
        try:
            prompt:str = self.prompt
            
            response:dict = self.llm.invoke(prompt)

            clean_response = response.content.replace('*','')
            
            return clean_response
        except TypeError as te:
            raise te
        except Exception as e:
            raise e