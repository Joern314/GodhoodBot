import praw
import argparse
import regex as re

from wiki import WikiEntry, WikiEntryParser, WikiTree
from formating import Link, Highlight

reddit = praw.Reddit('godhoodwb_wiki_bot') # see praw.ini for account credentials
subreddit = reddit.subreddit('GodhoodWB')

class Bot:
    def __init__(self):
        parser = argparse.ArgumentParser(description = 'Parse a turn-post to update the wiki')
        parser.add_argument('--url', help="url of turn thread")
        parser.add_argument('--turn', help="turn number")

        args = parser.parse_args()
        self.turn_thread = reddit.submission(url=args.url)
        self.turn_thread.comments.replace_more(limit=None)
        self.comment_list = self.turn_thread.comments.list()

        self.turn_number = args.turn

    def process_wikientrybot(self):
        wiki = WikiTree([])
        for comment in self.comment_list:
            default_info = WikiEntryParser.default_info(comment, self.turn_number)
            parsed = WikiEntryParser(comment.body, default_info)
            for p in parsed.emitted:
                wiki.insert(p)
        print(wiki)


    def process_logbot(self):
        print("PROCESS LOGBOT\n---\n---")

        highlight_list = []
        for comment in self.comment_list:
            comment_number = comment.id
            author_name = comment.author.name
            text_body = comment.body
            parsed = LogParser(text_body)
            for p in parsed.emitted:
                highlight_list.append(Highlight(comment, comment_number, p, "log"))

        highlight_list.sort(key=Highlight.comparable_key)
        for h in highlight_list:
            print(h)



class LogParser:
    def __init__(self, text: str):
        self.start = re.compile(r"LOGBOT", re.IGNORECASE)
        self.emitted = []
        self.parse(text)

    def parse(self, text: str):
        lines = text.splitlines()
        for line in lines:
            if re.search(self.start, line):
                self.emitted.append(line)

def main():
    bot = Bot()
    bot.process_logbot()
    bot.process_wikientrybot()

if __name__=="__main__":
    main()
