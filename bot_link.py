import regex as re
import markdown_to_text

from wiki import Entry
import reddit_utils


class Link:
    """Helper class to format links"""

    def __init__(self, title, url, tooltip):
        self.title = title
        self.url = url
        self.tooltip = tooltip

    def __repr__(self):
        n = Link.markdown_escape(self.title)
        u = Link.markdown_escape(self.url)
        if self.tooltip is not None:
            t = Link.markdown_escape(self.tooltip)
            return f'[{n}]({u} "{t}")'
        else:
            return f'[{n}]({u})'

    @staticmethod
    def markdown_escape(url):
        special = ["\\", "(", ")", "[", "]", "\""]
        for s in special:
            url = url.replace(s, "\\" + s)
        return url

    @staticmethod
    def simplify_tooltip(content):
        content = markdown_to_text.markdown_to_text(content)  # no formatting
        content = " ".join(content.splitlines())  # get rid of newlines
        return content

    @staticmethod
    def from_entry(entry: Entry):
        title = entry.reference_name()
        url = reddit_utils.get_url(entry)
        tooltip = Link.simplify_tooltip(entry.content)
        return Link(title, url, tooltip)


class LinkParser:
    """Detect request for wiki-links and fulfill them"""

    def __init__(self, wiki: Entry):
        self.wiki = wiki

    @staticmethod
    def extract_and_replace_links(text, wiki):
        links = []

        # ms = re.findall(r"\[(.+?)\]\((.+?)\)", text)
        # for m in ms:
        #    title = m.group(1)
        #    url = m.group(2)
        #    full = m.group(0)
        #    if url.strip().startswith("#"):
        #        links.append((title, url, full))

        ms = re.findall(r"\[\[(.+?)(\|(.+?))?\]\]", text)
        for m in ms:
            full = m.group(0)
            url = m.group(1)
            title = m.group(3) or url
            links.append((title, url, full))

        output = []

        for title, url, full in links:
            alias = Entry.normalize(url)
            entry = wiki.find_child(alias)
            if entry is None:  # couldn't resolve
                continue
            link = Link.from_entry(entry)
            output.append(link)
            text = text.replace(full, repr(link))
        return text, output

    @staticmethod
    def bot_comment(content_md, wiki):
        new, links = LinkParser.extract_and_replace_links(text=content_md, wiki=wiki)
        comment = "References: " + (" ; ".join(map(repr, links)))
        return comment
