import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()

class PostgresClient:
	def __init__(self):
		self.conn = psycopg2.connect(
			host=os.getenv("POSTGRES_URL"),
			port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB_NAME")
		)
		self.conn.autocommit = True
	

	def fetch_one(self, query, params=None):
		with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
			cursor.execute(query, params)
			return cursor.fetchone()
	
	def fetch_all(self, query, params=None):
		with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
			cursor.execute(query, params)
			return cursor.fetchall()

	def execute(self, query, params=None):
		with self.conn.cursor() as cursor:
			cursor.execute(query, params)
		
	def update_status(self, task_id, status):
		with self.conn.cursor() as cursor:
			query = """
				UPDATE stu_tracker.Generate_question_task
				SET status = %s WHERE id = %s;
			"""
			cursor.execute(query, (status, task_id))

	def close(self):
		return self.conn.close()
		
