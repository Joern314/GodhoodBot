#!/bin/env python3

import argparse
import regex as re
import git
import os.path, glob
from datetime import datetime

import reddit_crawl
import wiki_parser
from wiki import Entry

args = {
    "url": r"https://www.reddit.com/r/testingground4bots/comments/fhftm0/testwb_game_19_turn_08/",
    "turn": r"8",
}

# parser = argparse.ArgumentParser(description='godhoodwb bot')
# parser.add_argument('--url', help="url of turn thread")
# parser.add_argument('--turn', help="turn number")
# args = parser.parse_args()

reader = reddit_crawl.RedditReader(thread_url=args['url'], turn_number=int(args['turn']))
wiki_reader = reddit_crawl.RedditWikiReader()

thread_id = reader.thread.id
time = datetime.now().strftime("%m/%d-%H:%M")
commit_msg = f"{thread_id}/{time}"

repo = git.Repo(reddit_crawl.submodule_repo)
assert not repo.bare


def everything():
    pull_wiki()
    pull_comments()
    parse_comments()
    merge_comments()
    merge_wiki()

    accept_joined()


def pull_wiki():
    repo.git.checkout("wiki")

    reddit_crawl.crawl_wiki()

    repo.git.add('./wiki/*')
    repo.git.commit("--allow-empty", m=f'"Wiki-{commit_msg}"')
    print(repo.git.status())


def pull_comments():
    repo.git.checkout("comments")

    reddit_crawl.crawl_thread(turn=int(args['turn']), url=args['url'])

    repo.git.add(f'./{reader.thread.id}')
    repo.git.commit("--allow-empty", m=f"Comments-{commit_msg}")
    print(repo.git.status())


def parse_comments():
    repo.git.checkout("comments")

    files_comm = glob.glob(f"./{reddit_crawl.submodule_repo}/{thread_id}/*.md")
    files_wiki = glob.glob(f"./{reddit_crawl.submodule_repo}/wiki/*.md")

    wiki = Entry.create_wiki_root()
    wiki_parser.parse_entries_and_insert_with_overwrite(wiki, files_wiki, "wiki")
    wiki_parser.parse_entries_and_insert_with_overwrite(wiki, files_comm, "comment")

    wiki.sort_children_recursive()

    wiki_pages = wiki_parser.split_into_files(wiki)

    for page, node in wiki_pages.items():
        with open(wiki_reader.file_wiki_page(page), "w") as file:
            if node is not None:
                content = node.to_string(short=False)
            else:
                content = ""
            file.write(content)

    repo.git.add(f'./wiki')
    repo.git.commit("--allow-empty", m=f"Parsed-{commit_msg}")
    print(repo.git.status())

    return wiki


def merge_comments():
    repo.git.checkout("joined")
    repo.git.merge("comments")
    print(repo.git.status())


def merge_wiki():
    repo.git.checkout("joined")
    repo.git.merge("wiki")
    print(repo.git.status())


def accept_joined():
    repo.git.checkout("wiki")
    repo.git.merge("joined")

    print(repo.git.status())

    repo.git.checkout("comments")
    repo.git.merge("joined")

    print(repo.git.status())

def push_wiki_to_reddit():

