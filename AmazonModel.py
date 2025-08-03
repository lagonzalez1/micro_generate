import os
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
load_dotenv()

MODEL_ID = os.getenv("MODEL_ID")

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

class AmazonModel:
    def __init__(self, prompt: str, temp: float, top_p: float, max_gen_len: int):
        self.prompt = prompt 
        self.temp = temp
        self.top_p = top_p
        self.max_gen_len = max_gen_len
        # Build the response
        self.response = self.generate_amazon_titan_model()
        # Verify the response and append
        self.parsed_response = None


    def generate_amazon_titan_model(self) -> dict:
        try:
            response = bedrock.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps({
                    "inputText": self.prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": self.max_gen_len,
                        "temperature": self.temp
                    }
                })
            )
            print("Response", response)
            return response
        except (ClientError, Exception) as e:
            print(f"Error: Can't invoke '{MODEL_ID}. Reason: '{e}''")

    def input_token(self):
        response_body = json.loads(self.response.get("body").read())
        usage = response_body.get("usage")
        return usage.get("inputTokens")

    def output_token(self):
        response_body = json.loads(self.response.get("body").read())
        usage = response_body.get("usage")
        return usage.get("outputTokens")

    def total_token(self):
        response_body = json.loads(self.response.get("body").read())
        usage = response_body.get("usage")
        return usage.get("totalTokens")

    def generate_meta_model(self) ->dict:
        try:
            response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": self.prompt,
                "max_gen_len": self.max_gen_len,
                "temperature": self.temp,
                "top_p": self.top_p
                })
            )
            return response
        except (ClientError, Exception) as e:
            print(f"Error: Can't invoke '{MODEL_ID}. Reason: '{e}''")
    
    def valid_response(self)->bool:
        model_response = json.loads(self.response["body"].read())
        if model_response:
            self.parsed_response = model_response
            return True
        else:
            self.parsed_response = None
            return False
    
    def get_generation(self)->str:
        return self.parsed_response["results"][0]["outputText"]



