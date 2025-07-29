# micro_generate
With the help of LLM, this micro service will be utilized in conjunction with AmazonMQ(rabbitMq) to listen to request from client.

## Table of content

1. Installation
2. Running
3. Features
4. Improvments
5. Purpose


## 1. Installation

- Ensure you have the latest python3, pip (Package manager)
1. $ git clone this repo
2. cd into repo
3. Install requirements.txt by running 
 - $ pip install -r requirements.txt
4. $ python3 main.py


## 2. Running

To run this script in during testing, its best to just use this command python3 main.py.
For production, the idea is to dockerize. Push to ECR or Docker hub and run as a managed service. 
Doing so ECS Faregate runs the docker iamge and forget about it. Unless you run into issues. 


## 3. Featrues

Run context aware (Prompting) API calls to your model of choice. For this application its focused on the creating assessments in the form of JSON.
This is ideally used to create on the fly quick assessments based on context described by the user. Check out Prompts.py and PromptsClient.py.


## 4. Improvments

This is my first attempt in Prompting "Enmgineering", so my only conserns as of now are token limits and possible prompt injections. The output needs to be in the format described in the Prompts.py example section. Otherwise my frontned will not be able to parse correctly. 


## 5. Purpose

Frontend 
    -> Go Backend (RabbitMQ producer) 
        -> RabbitMQ (Channel) 
            -> ECS Faregate (Consumer) Microservices

