#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import List
import os

def perform_commit(repo):
    print(repo)

def perform_search(query):
    print(query)

def perform_fetch(env):
    print(env)

def perform_ask(question):
    print(question)

def perform_env(repo):
    print(repo)

def perform_exit():
    print("Exit")

def perform_gname(gname):
    print(gname)

def main(commit, git_search, fetch_env, ask, env, exit, gname):
    if(commit is not None):
       perform_commit(commit)
    elif(git_search is not None):
       perform_search(git_search)
    elif(fetch_env is not None):
       perform_fetch(fetch_env)
    elif(ask is not None):
       perform_ask(ask)
    elif(env is not None):
       perform_env(env)
    elif(exit):

       perform_exit()
    elif(gname is not None):
       perform_gname(gname)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = """This script sets up an environment that logs terminal commands allowing 
                         for future semantic search"""
    )

    parser.add_argument(
        "-c",
        "--commit",
        help = "get repo name for commiting"
    )

    parser.add_argument(
        "-s",
        "--git_search",
        help = "get a query to search for commits"
    )

    parser.add_argument(
        "-f",
        "--fetch_env",
        help = "fetches an environment from a repo"
    )

    parser.add_argument(
        "-a",
        "--ask",
        help = "ask a question based on current env"
    )

    parser.add_argument(
        "-e",
        "--env",
        help = "load a current environment into the server"
    )

    parser.add_argument(
        "--exit",
        default = False,
        action='store_true',
        help = "exit the current environment"
    )

    parser.add_argument(
        "--gname",
        help="create a hidden file given a group name"
    )

    args = parser.parse_args()

    main(args.commit, args.git_search, args.fetch_env, args.ask, args.env, args.exit, args.gname)







