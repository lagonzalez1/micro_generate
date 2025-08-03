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

	def get_district_data(self, params):
		try:
			district_query = "SELECT name, city, state, region FROM stu_tracker.District WHERE organization_id = %s AND id = %s"
			return self.fetch_one(district_query, params)
		except Exception as e:
			raise RuntimeError("unable to get district data from database")
	
	def get_subject_data(self, params):
		try:	
			subject_query = "SELECT title, description FROM stu_tracker.Subjects WHERE organization_id = %s AND id = %s"
			return self.fetch_one(subject_query, params)
		except Exception as e:
			raise RuntimeError("unable to get subject data")
	
	def update_question_task(self, params):
		try:	
			success_query = "UPDATE stu_tracker.Generate_questions_task SET status = %s WHERE s3_output_key = %s;"
			return self.execute(success_query, params)
		except Exception as e:
			raise RuntimeError("unable to get update question task")
		
	def update_question_task_retry(self, params):
		try:	
			retry_query = "UPDATE stu_tracker.Generate_questions_task SET status = %s, retry_count = retry_count + 1 WHERE s3_output_key = %s;"
			return self.execute(retry_query, params)
		except Exception as e:
			raise RuntimeError("unable to update retry question task")
			
	def close(self):
		return self.conn.close()
		
