
import os
import json
import pika
import psycopg2
from dotenv import load_dotenv
from PostgresClient import PostgresClient 
from Client import Client
from PromptClient import PromptClient
from Model import Model
from google import genai
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import ssl

load_dotenv()  # loads variables from .env


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBIT_LOCAL  = os.getenv("RABBIT_LOCAL")
s3 = boto3.client('s3')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)


class RabbitMQ:
    def __init__(self, prefetch_count, exchange, queue, routing_key, exchange_type):
        params = None
        self.queue = queue
        if RABBIT_LOCAL == str(1) or RABBIT_LOCAL == 1:
            params = pika.ConnectionParameters(
                host=RABBITMQ_HOST, 
                port=RABBITMQ_PORT, 
                credentials=credentials, 
                heartbeat=60, 
                blocked_connection_timeout=30
            )
        else:
            ssl_context = ssl.create_default_context()
            params = pika.ConnectionParameters(
                host=RABBITMQ_HOST, 
                port=RABBITMQ_PORT,
                virtual_host="/",
                credentials=credentials, 
                heartbeat=60, 
                blocked_connection_timeout=30,
                ssl_options=pika.SSLOptions(context=ssl_context)
            )
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
        self.channel.basic_qos(prefetch_count=prefetch_count)
        

    def set_callback(self, callback_):
            self.channel.basic_consume(queue=self.queue, on_message_callback=callback_)

    def get_connection(self)->pika.BlockingConnection:
        return self.connection
        
    def get_channel(self):
        return self.channel