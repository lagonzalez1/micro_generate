micro_generate

A Python microservice that leverages large language models (LLMs) to generate assessments on the fly. It listens for requests via RabbitMQ (Amazon MQ) and returns JSON-formatted quizzes.

Table of Contents
	1.	Installation
	2.	Running
	3.	Features
	4.	Improvements
	5.	Architecture
	6.	Purpose

⸻

1. Installation
	1.	Clone the repository

git clone https://github.com/<your-org>/micro_generate.git


	2.	Change into the project directory

cd micro_generate


	3.	(Optional) Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate


	4.	Install dependencies

pip install -r requirements.txt


	5.	Run the service

python3 main.py



⸻

2. Running
	•	Development:

python3 main.py


	•	Production (Docker + ECS Fargate):
	1.	Build the Docker image

docker build -t micro_generate:latest .


	2.	Tag and push (ECR, Docker Hub, etc.)

docker tag micro_generate:latest <registry>/micro_generate:latest
docker push <registry>/micro_generate:latest


	3.	Deploy on ECS Fargate or your preferred container platform.

⸻

3. Features
	•	Context-aware prompting: Dynamic API calls to your chosen LLM for real-time assessment generation.
	•	JSON output: Returns quizzes, tests, and homework in a structured format.
	•	Configurable prompts: Customize and extend prompts via prompts.py and prompts_client.py.

⸻

4. Improvements
	•	Token management: Handle prompt and response size limits or automatically chunk large inputs.
	•	Input sanitization: Validate and clean user inputs to prevent prompt injection.
	•	Schema enforcement: Ensure the LLM output strictly follows the expected JSON schema for frontend compatibility.

⸻

5. Architecture

Frontend → Go backend (RabbitMQ producer) → RabbitMQ → ECS Fargate (Python consumer)

	•	RabbitMQ: Decouples request submission from processing.
	•	ECS Fargate: Hosts the always-on Python worker, auto-scales, and manages health checks.
	•	LLM integration: Invoke OpenAI, Amazon Bedrock, or other model endpoints for content generation.

⸻

6. Purpose

This microservice streamlines the creation of educational assessments, reducing overhead and accelerating content delivery in tutoring and learning platforms. It enables:
	•	Rapid quiz generation based on user-defined criteria.
	•	On-demand lesson planning tied to generated assessments.
	•	Cloud-native deployment for scalable, reliable service.