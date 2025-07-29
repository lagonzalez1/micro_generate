import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json
load_dotenv()

class Client:
    def __init__(self, body):
        try:
            self.payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            print("Unable to prase client body")
    
    def get_output_key(self) -> str:
        return self.payload.get("s3_output_key") 
    
    def get_organization_id(self) -> int:
        return self.payload.get("organization_id") 
    
    def get_district_id(self) -> int:
        return int(self.payload.get("district_id"))

    def get_subject_id(self) -> int:
        return int(self.payload.get("subject_id"))

    def get_description(self)->str:
        return self.payload.get("description")

    def get_max_points(self)->int:
        return int(self.payload.get("max_points"))

    def get_question_count(self) ->int:
        return int(self.payload.get("questions_count"))
    
    def get_grade_level(self) ->int:
        return int(self.payload.get("grade_level"))

    def get_difficulty(self) -> str:
        return self.payload.get('difficulty')
    


    