from modal import Image, Stub, wsgi_app
import modal

stub = Stub(
    "example-web-flask",
    image=Image.debian_slim().pip_install("flask", "pymongo", "openai", "flask-cors"),
    secrets=[modal.Secret.from_name("flask_secrets")]
)

@stub.function()
def generate_vector(text):
    import openai
    import os
    import random
    import time
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    while True:
        try:
            response = client.embeddings.create(
                input=text, model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except openai.RateLimitError:
            attempt += 1
            wait_time = min(2**attempt + random.random(), 60)
            if attempt == 10:
                break
            time.sleep(wait_time)
        except Exception as e:
            break
    return None

@stub.function()
def search_documents(query, id):
    import pymongo
    import openai
    import os
    client = pymongo.MongoClient(os.environ['MONGO_URL'])

    db = client[id]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    query_vector = generate_vector.local(query)
   
    return {
        "response": query_vector
    }

@stub.function()
def mongo_updater(id, collection_type, item):
    import pymongo
    import os
    client = pymongo.MongoClient(os.environ['MONGO_URL'])

    db = client[id]

    return {"result": "success"}

@stub.function()
def get_notifs(id):
    import pymongo
    import openai
    import os
    client = pymongo.MongoClient(os.environ['MONGO_URL'])

    db = client[id]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    responses = []
    return responses

@stub.function()
@wsgi_app()
def flask_app():   
    from flask import Flask, request
    from flask_cors import CORS, cross_origin

    web_app = Flask(__name__)
    cors = CORS(web_app)

    @web_app.post("/search")
    @cross_origin()
    def search():
        return search_documents.remote(request.json["query"], request.json["id"])

    @web_app.post("/get_notifs")
    @cross_origin()
    def notif_updates():
        return get_notifs.remote(request.json["id"])
    
    @web_app.post("/add_item")
    @cross_origin()
    def add_item():
        return mongo_updater.remote(request.json["id"], request.json["type"], request.json["content"])

    return web_app
