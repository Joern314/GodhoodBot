
class Link:
    def __init__(self, title, permalink):
        self.title = title
        self.permalink = permalink

    def __repr__(self):
        return f"[{self.title}](https://old.reddit.com/{self.permalink})"

class Highlight:
    def __init__(self, comment, comment_number, text_passage, format="wiki"):
        self.comment = comment
        self.comment_number = comment_number
        self.text_passage = text_passage
        self.format = format

    def link(self):
        return f"[{self.comment_number}](https://old.reddit.com/{self.comment.permalink})"

    def __repr__(self):
        if self.format == "wiki":
            return f"/u/{self.comment.author.name} : {self.link()} \n{self.text_passage}"
        elif self.format == "log":
            return f"/u/{self.comment.author.name} : {self.text_passage} {self.link()}"
        else:
            return NotImplemented

    def get_author(self):
        return self.comment.author.name

    def get_time(self):
        return self.comment.created_utc

    def comparable_key(self):
        return (self.get_author(), self.get_time())
