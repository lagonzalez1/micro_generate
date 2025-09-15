import os
import json
import logging
import pika
import psycopg2
from dotenv import load_dotenv
from Config.PostgresClient import PostgresClient 
from Config.RabbitMQ import RabbitMQ
from Client import Client
from PromptClient import PromptClient
from Models.AmazonModel import AmazonModel
from Models.GeminModel import GeminiModel
from google import genai
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import ssl
import logging


load_dotenv()  # loads variables from .env

# --- 1. Set up basic logging to stdout ---
logging.basicConfig(
    level=logging.INFO, # Adjust to logging.DEBUG for more verbose logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


EXCHANGE     = os.getenv("EXCHANGE")
QUEUE        = os.getenv("QUEUE")
ROUTING_KEY  = os.getenv("ROUTING_KEY")
RABBIT_LOCAL  = os.getenv("RABBIT_LOCAL")
s3 = boto3.client('s3')
PREFETCH_COUNT = 1
EXCHANGE_TYPE = "direct"

def create_callback(db):
    def on_message_test(channel, method, properties, body):
        parse_client = Client(body)
        try:
            # Query the postgres db to get the values of district, subject
            district_data = db.get_district_data((parse_client.get_organization_id(), parse_client.get_district_id()))
            if not district_data:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                raise ValueError("Missing district data")

            subject_data = db.get_subject_data((parse_client.get_organization_id(), parse_client.get_subject_id()))
            if not subject_data:
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                raise ValueError("Missing subject data")

            # Right now the values must be provided. 
            # It should be possible to not include district
            prompt = PromptClient(district_data, subject_data, parse_client.get_description(), 
                                  parse_client.get_max_points(), parse_client.get_question_count(), parse_client.get_grade_level(),
                                  parse_client.get_difficulty())
            print(f"Input token count: '{prompt.get_token_length()}'")
            # Invoke Amazon Bedrock model
            model = AmazonModel(prompt=prompt.get_prompt(), temp=0.5, top_p=0.9, max_gen_len=3072)
            #print(f"Total tokens: {model.total_token()} ")

            # Invoke Gemini model for testing
            #model = GeminiModel(prompt=prompt.get_prompt())
            response = model.valid_response()
            logger.info(f"Valid_response boolean '{response}'.")
            logger.info(f"The outputkey '{parse_client.get_output_key()}'.")
            if response:
                try:
                    s3.put_object(
                        Bucket="tracker-client-storage",
                        Key="assessments/"+parse_client.get_output_key(),
                        Body=model.get_generation(),
                        ContentType='application/json'
                    )
                    success_request = db.update_question_task(("COMPLETE", prompt.get_token_length(), model.total_token(), parse_client.get_output_key()))
                    if success_request:
                        channel.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        channel.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
                except (BotoCoreError, ClientError) as e:
                    logger.info(f"Unable to upload s3 '{e}'.")
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)                 
            else:
                # Did not get a response so try again log to db as well
                retry_request = db.update_question_task_retry(("RETRY", parse_client.get_output_key()))
                if retry_request:
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                else:
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            print("error occured: ", e)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return on_message_test

def main():
    db = PostgresClient()
    rabbit_assessment_queue = RabbitMQ(PREFETCH_COUNT, EXCHANGE, QUEUE, ROUTING_KEY, EXCHANGE_TYPE)
    
    callback = create_callback(db)
    rabbit_assessment_queue.set_callback(callback)
    channel = rabbit_assessment_queue.get_channel()
    connection = rabbit_assessment_queue.get_connection()

    print(f"[*] Waiting for messages in '{QUEUE}'. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted, closing...")
    finally:
        channel.close()
        connection.close()
        db.close()


if __name__ == "__main__":
    main()