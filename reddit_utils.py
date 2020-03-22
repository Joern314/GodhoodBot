import praw
import argparse
import urllib.parse

from wiki import Entry
from bot_wiki import WikiParser

# reddit wiki


def get_url(entry: Entry):
    path = entry.get_path()
    major = Entry.normalize(path[1])  # cut off wiki root
    assert (major in wiki_pages)
    minor = path[-1]

    return create_wiki_link(major, minor)


def create_wiki_link(page: str, content: str):
    from urllib import parse
    tmp = content.lower().replace(" ", "_")
    new = parse.quote(tmp.encode('latin-1'), safe='').replace("%", ".")
    link = "#wiki_" + new
    return f"{wiki_url_prefix}/{page}#wiki_{new}"


def fetch_wiki_page(page: str):
    return


def write_wiki_page(page: str, content_md: str):
    return subreddit.wiki[f"godhoodwb19/wiki/{page}"].edit(
        content=content_md,
        reason="wikibot pushed changes"
    )


def parse_wiki():
    wiki = Entry.create_wiki_root()
    for p in wiki_pages:
        content = fetch_wiki_page(p)
        WikiParser.take_and_parse(content.splitlines(), None, wiki)
    wiki.sort_children_recursive()
    return wiki


def write_wiki(wiki: Entry):
    for p in wiki_pages:
        node = wiki.find_child(p)
        if node is None:
            continue
        write_wiki_page(p, repr(node))
