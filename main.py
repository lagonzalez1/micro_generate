import os
import json
import pika
import psycopg2
from dotenv import load_dotenv
from PostgresClient import PostgresClient 
from Client import Client
from PromptClient import PromptClient
from google import genai
import boto3
from botocore.exceptions import BotoCoreError, ClientError

load_dotenv()  # loads variables from .env

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
EXCHANGE     = os.getenv("EXCHANGE")
QUEUE        = os.getenv("QUEUE")
ROUTING_KEY  = os.getenv("ROUTING_KEY")
s3 = boto3.client('s3')

def create_callback(db):
    def on_message_test(channel, method, properties, body):
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        parse_client = Client(body)
        try:
            # Query the postgres db to get the values of district, subject
            district_query = "SELECT name, city, state, region FROM stu_tracker.District WHERE organization_id = %s AND id = %s"
            district_params = (parse_client.get_organization_id(), parse_client.get_district_id())
            district_data = db.fetch_one(district_query, district_params)
            if not district_data:
                raise ValueError("Missing district data")

            subject_query = "SELECT title, description FROM stu_tracker.Subjects WHERE organization_id = %s AND id = %s"
            subject_params = (parse_client.get_organization_id(), parse_client.get_subject_id())            
            subject_data = db.fetch_one(subject_query, subject_params)
            if not subject_data:
                raise ValueError("Missing subject data")
            
            prompt = PromptClient(district_data, subject_data, parse_client.get_description(), 
                                  parse_client.get_max_points(), parse_client.get_question_count(), parse_client.get_grade_level(),
                                  parse_client.get_difficulty())
            print(prompt.get_token_length())
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt.get_prompt()
            )
            if response:
                print(len(response.text))
                success_query = "UPDATE stu_tracker.Generate_questions_task SET status = %s WHERE s3_output_key = %s;"
                success_params = ("COMPLETE", parse_client.get_output_key())
                try:
                    s3.put_object(
                        Bucket="tracker-client-storage",
                        Key=parse_client.get_output_key(),
                        Body=response.text,
                        ContentType='application/json'
                    )
                    success_data = db.execute(success_query, success_params)
                    if success_data:
                        channel.basic_ack(delivery_tag=method.delivery_tag)
                except (BotoCoreError, ClientError) as e:
                    print("unable to upload to s3", e)
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)                    
            else:
                # Did not get a response so try again log to db as well
                retry_query = "UPDATE stu_tracker.Generate_questions_task SET status = %s, retry_count = retry_count + 1 WHERE s3_output_key = %s;"
                retry_params = ("RETRY", parse_client.get_output_key())
                success_data = db.execute(retry_query, retry_params)
                channel.basic_ack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            print("error occured: ", e)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return on_message_test

def main():
    db = PostgresClient()
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST, 
        port=RABBITMQ_PORT, 
        credentials=credentials, 
        heartbeat=60, 
        blocked_connection_timeout=30
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

    print(f"[*] Waiting for messages in '{QUEUE}'. To exit press CTRL+C")
    channel.basic_qos(prefetch_count=1)

    callback = create_callback(db)
    channel.basic_consume(queue=QUEUE, on_message_callback=callback)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted, closing...")
    finally:
        channel.close()
        connection.close()


if __name__ == "__main__":
    main()