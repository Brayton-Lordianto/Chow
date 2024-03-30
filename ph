#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import List
import os
import subprocess
import tkinter as tk
import requests

url = "https://tanzhasan--example-web-flask-flask-app.modal.run/"

"""/search_command gname query
/add_command gname command 
/add_env gname repo content
/get_env gname repo
/make_commit gname repo diff_contents #returns llm response
/add_commit gname repo commit_message commit_hash branch #adds to mongo
/search_commit gname repo query 
"""

def get_gname():
    # make a subprocess that echoes and returns $PH_GNAME
    gname = os.environ.get("PH_GNAME")
    gname = gname if gname is not None else "default"
    return gname
def git_diff():
    exclude_paths = ["node_modules/", "venv/", "*.log", "*.swp", "*.bak", ".cache", ".env", ".config"] # useless files 
    git_diff_command = ["git", "diff"]
    for path in exclude_paths:
        git_diff_command.append(f":(exclude){path}")
    diff_output = subprocess.check_output(git_diff_command)
    diff_output = diff_output.decode('utf-8')
    return diff_output

root, text_box = None, None
def on_closing():
    global root, text_box
    text = text_box.get("1.0", tk.END)
    print("Text before closing:", text)
    root.destroy()

def create_text_box(initial_text): 
    global root, text_box
    # Create the main window
    root = tk.Tk()
    root.title("Editable Text Box")

    # Create a text box
    text_box = tk.Text(root)
    text_box.pack(fill=tk.BOTH, expand=True)
    text_box.insert(tk.END, initial_text)

    # Center the window on the screen
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Bind the closing event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Run the application
    root.mainloop()

def perform_commit(repo):
    # git diff file 
    diff = git_diff()
    print(get_gname())
    # send to post request to server
    
    
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







