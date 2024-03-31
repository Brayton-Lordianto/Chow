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
def generate_expl(text):
    import openai
    import os

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = "Generate a summary of the users command Say nothing else except one line about what it does:\n\n"
    prompt += f"{text}"
    # print(prompt)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
    )
    print(response.choices[0].message.content)
    expl = response.choices[0].message.content

    return expl


@stub.function()
def generate_commit(text):
    import openai
    import os

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = "Generate a commit message based on the diff:\n\n"
    prompt += f"{text}"
    # print(prompt)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a software developer writing a commit message.\n"
                + "Write a commit message title then a newline and the commit message body.",
            },
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
    )
    print(response.choices[0].message.content)
    expl = response.choices[0].message.content

    return expl


@stub.function()
def search_command(gname, query):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname]["command"]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    query_vector = generate_vector.local(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "vec",
                "queryVector": query_vector,
                "numCandidates": 5,
                "limit": 3,
            }
        }
    ]
    results = db.aggregate(pipeline)
    results = [
        {"command": result["content"], "explanation": result["explanation"]}
        for result in results
    ]
    return {"result": 200, "commands": results}


@stub.function()
def add_command(gname, command):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    command = command.strip()
    if command == '':
        return {"result": 200}
    print(gname)
    db = client[gname]["command"]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    existing_command = db.find_one({"content": command})

    if existing_command:
        return {
            "result": 200,
            "message": "Command already exists",
            "inserted_id": str(existing_command["_id"]),
        }

    explanation = generate_expl.local(command)
    vector = generate_vector.local(explanation)
    result = db.insert_one(
        {"content": command, "explanation": explanation, "vec": vector}
    )
    print(gname, command, explanation)

    return {"result": 200, "inserted_id": str(result.inserted_id)}


@stub.function()
def add_env(gname, repo, content):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    db = client[gname][repo]["env"]
    db.drop()
    result = db.insert_one({"content": content})

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    return {"result": 200, "inserted_id": str(result.inserted_id)}


@stub.function()
def get_env(gname, repo):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    db = client[gname][repo]["env"]
    documents = list(db.find())
    return {"result": 200, "env": str(documents[0]["content"])}


@stub.function()
def make_commit(gname, repo, diff_contents):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname][repo]
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    explanation = generate_commit.local(diff_contents)
    return {"result": 200, "commit_message": explanation}


@stub.function()
def add_commit(gname, repo, commit_message, commit_hash, branch):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    db = client[gname][repo]["commits"]
    openai.api_key = os.environ["OPENAI_API_KEY"]

    vector = generate_vector.local(commit_message)
    commit = {
        "hash": commit_hash,
        "message": commit_message,
        "branch": branch,
        "vec": vector,
    }
    db.insert_one(commit)
    return {"result": 200, "inserted_id": str(commit["_id"])}


@stub.function()
def search_commit(gname, repo, query):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    db = client[gname][repo]["commits"]
    openai.api_key = os.environ["OPENAI_API_KEY"]

    query_vector = generate_vector.local(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "vec",
                "queryVector": query_vector,
                "numCandidates": 5,
                "limit": 3,
            }
        }
    ]
    results = db.aggregate(pipeline)
    results = [
        {
            "hash": result["hash"],
            "message": result["message"],
            "branch": result["branch"],
        }
        for result in results
    ]
    return {"result": 200, "commits": results}


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
        # print(str(request))
        gname = request.json["gname"]
        command = request.json["command"]
        return add_command.remote(gname, command)

    @web_app.post("/add_env")
    @cross_origin()
    def add_env_route():
        gname = request.json["gname"]
        repo = request.json["repo"]
        content = request.json["content"]
        print(gname, repo, content)
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
