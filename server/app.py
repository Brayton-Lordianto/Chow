from modal import Image, Stub, wsgi_app
import modal

stub = Stub(
    "example-web-flask",
    image=Image.debian_slim().pip_install("flask", "pymongo", "openai", "flask-cors"),
    secrets=[modal.Secret.from_name("flask_secrets")],
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
def search_command(gname, query):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname]["command"]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    query_vector = generate_vector.local(query)
    pass


@stub.function()
def add_command(gname, command):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname]["command"]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pass


@stub.function()
def add_env(gname, repo, content):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname]["command"]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pass


@stub.function()
def get_env(gname, repo):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname]["command"]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pass


@stub.function()
def make_commit(gname, repo, diff_contents):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname][repo]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pass


@stub.function()
def add_commit(gname, repo, commit_message, commit_hash, branch):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname][repo]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pass


@stub.function()
def search_commit(gname, repo, query):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname][repo]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pass


@stub.function()
@wsgi_app()
def flask_app():
    from flask import Flask, request
    from flask_cors import CORS, cross_origin

    web_app = Flask(__name__)
    cors = CORS(web_app)

    @web_app.post("/search_command")
    @cross_origin()
    def search_command_route():
        gname = request.json["gname"]
        query = request.json["query"]
        return search_command.remote(gname, query)

    @web_app.post("/add_command")
    @cross_origin()
    def add_command_route():
        gname = request.json["gname"]
        command = request.json["command"]
        return add_command.remote(gname, command)

    @web_app.post("/add_env")
    @cross_origin()
    def add_env_route():
        gname = request.json["gname"]
        repo = request.json["repo"]
        content = request.json["content"]
        return add_env.remote(gname, repo, content)

    @web_app.post("/get_env")
    @cross_origin()
    def get_env_route():
        gname = request.json["gname"]
        repo = request.json["repo"]
        return get_env.remote(gname, repo)

    @web_app.post("/make_commit")
    @cross_origin()
    def make_commit_route():
        gname = request.json["gname"]
        repo = request.json["repo"]
        diff_contents = request.json["diff_contents"]
        return make_commit.remote(gname, repo, diff_contents)

    @web_app.post("/add_commit")
    @cross_origin()
    def add_commit_route():
        gname = request.json["gname"]
        repo = request.json["repo"]
        commit_message = request.json["commit_message"]
        commit_hash = request.json["commit_hash"]
        branch = request.json["branch"]
        return add_commit.remote(gname, repo, commit_message, commit_hash, branch)

    @web_app.post("/search_commit")
    @cross_origin()
    def search_commit_route():
        gname = request.json["gname"]
        repo = request.json["repo"]
        query = request.json["query"]
        return search_commit.remote(gname, repo, query)

    return web_app
