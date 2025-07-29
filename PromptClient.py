import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json
from Prompts import get_examples_prompt, get_identity_prompt, get_instructions_prompt, get_user_description_prompt, get_rules_prompt




class PromptClient:
    def __init__(self, district_data: dict, subject_data: dict, description_context, max_points, question_count, grade_level, difficulty):
        self.district_context = district_data["name"] + " , " + district_data["city"] + " , " + district_data["state"] + " , " +district_data["region"]
        self.subject_context = subject_data["title"] + " , " + subject_data["description"]
        self.prompt = self.build_prompt(self.district_context, self.subject_context, description_context, max_points, question_count, grade_level, difficulty)

    
    def build_prompt(self, district_context, subject_context, description_context, max_points, question_count, grade_level, difficulty) -> str:
        return (get_identity_prompt()
                 + get_instructions_prompt(question_count, max_points, district_context, subject_context, grade_level, difficulty)
                 + get_rules_prompt()
                 + get_user_description_prompt(description_context)
                 + get_examples_prompt()
                 )


    def get_prompt(self)->str:
        return self.prompt
    
    def get_token_length(self) ->int:
        compressed = ''.join(self.get_prompt().split())
        return (len(compressed) + 2) // 3


    
    