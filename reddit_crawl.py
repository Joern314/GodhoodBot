#  load stuff from reddit into the data folder
import praw
import json
import os

test_url = "https://www.reddit.com/r/testingground4bots/comments/fhftm0/testwb_game_19_turn_08/"

submodule_repo = "GWB19-Data"


class RedditReader:
    def __init__(self, thread_url: str, turn_number: int):
        self.reddit = praw.Reddit('godhoodwb_wiki_bot')  # see praw.ini for account credentials
        self.thread_url = thread_url
        self.thread = self.reddit.submission(url=self.thread_url)
        self.thread.comments.replace_more(limit=None)
        self.turn_number = turn_number

        self.folder = f"./{submodule_repo}/{self.thread.id}"

        os.makedirs(self.folder, exist_ok=True)

    def file_comment(self, comment):
        return f"{self.folder}/comment_{comment.id}.md"

    def file_meta_comment(self, comment):
        return f"{self.folder}/comment_{comment.id}.json"

    def pull_comments(self):
        for comment in self.thread.comments.list():
            self.pull_comment(comment)

    def all_files(self):
        return [self.file_comment(c) for c in self.thread.comments.list()]

    def pull_comment(self, comment):
        if comment.author is None:
            return

        with open(self.file_comment(comment), "w") as file:
            with open(self.file_meta_comment(comment), "w") as meta_file:
                meta = {
                    "id": comment.id,
                    "url": comment.permalink,
                    "turn": self.turn_number,
                    "author": comment.author.name,
                    "created_utc": comment.created_utc,
                }

                content = comment.body

                file.write(content)
                meta_file.write(json.dumps(meta))


class RedditWikiReader:
    wiki_pages = ["world", "supernatural", "politics", "divines", "misc"]

    def __init__(self):
        self.reddit = praw.Reddit('godhoodwb_wiki_bot')  # see praw.ini for account credentials

        self.wiki_pages = RedditWikiReader.wiki_pages
        self.wiki_url_prefix = "https://www.reddit.com/r/godhoodwb/wiki/godhoodwb19/wiki"

        self.folder = f"./{submodule_repo}/wiki"

        os.makedirs(self.folder, exist_ok=True)

    def file_wiki_page(self, page):
        return f"{self.folder}/wiki_{page}.md"

    def file_meta_wiki_page(self, page):
        return f"{self.folder}/wiki_{page}.json"

    def pull_wiki(self):
        for page in self.wiki_pages:
            self.pull_wiki_page(page)

    def all_files(self):
        return [self.file_wiki_page(c) for c in self.wiki_pages]

    def pull_wiki_page(self, page):
        with open(self.file_wiki_page(page), "w") as file:
            with open(self.file_meta_wiki_page(page), "w") as meta_file:
                wiki_page = self.reddit.subreddit("godhoodwb").wiki[f"godhoodwb19/wiki/{page}"]
                meta = {
                    "id": None,
                    "url": f"{self.wiki_url_prefix}/{page}",
                    "turn": None,
                    "author": None,
                    "page": page,
                    "revision_date": wiki_page.revision_date,
                }

                content = wiki_page.content_md

                file.write(content)
                meta_file.write(json.dumps(meta))

                file.write(content)


def crawl_thread(url: str, turn: int):
    rr = RedditReader(thread_url=url, turn_number=turn)
    rr.pull_comments()
    return rr.all_files()


def crawl_wiki():
    rr = RedditWikiReader()
    rr.pull_wiki()
    return rr.all_files()


def crawl_all(thread_url: str, turn_number: int):
    li = crawl_wiki()
    li += crawl_thread(thread_url, turn_number)
    return li
