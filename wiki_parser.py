import regex as re
import json

from wiki import Entry
from reddit_crawl import RedditWikiReader


class WikiParser:
    def __init__(self, tree: Entry, syntax="wiki", default_info_string=None):
        self.mode = "entry-title"
        self.title = None
        self.entry = None

        self.syntax = syntax
        self.default_info_string = default_info_string

        self.tree = tree
        self.working_node = self.tree

    @staticmethod
    def new_entry():
        return {
            "print_name": None,
            "info": None,
            "content": [],
            "node": None  # where to merge these changes into
        }

    def process_end_of_text(self):
        if self.entry is not None:
            self.end_entry()

    def process_line(self, line):
        if self.mode == "entry-title":  # waiting for the entry to begin
            title, context = WikiParser.line_title_with_context(line)
            if title is None:
                title, context = WikiParser.line_title(line), None

            if title is None:
                return True  # continue search for title

            if context is not None:
                self.switch_context(context)
                self.start_entry(title)
                return True  # proceed with next line
            else:
                self.switch_context_by_level(title)
                if self.syntax == "comment" and self.working_node == self.tree:  # we ascended outside the previous entries!
                    return True  # proceed with next line, waiting for the next title
                else:  # we are still inside the wiki tree OR every headline simply is an entry (wiki syntax)
                    self.start_entry(title)
                    return True  # proceed with next line

        elif self.mode == "entry-info":  # await info section
            if WikiParser.line_empty(line):
                return True  # wait longer
            info = WikiParser.line_entry_info(line)
            if info is None:
                self.set_info(None)
                return False  # nope, not an info, retry

        elif self.mode == "entry-content":  # await random content but no headlines or separators
            if WikiParser.line_content(line):
                self.add_content(line)
                return True
            else:  # end
                self.end_entry()
                return False  # entry ended, retry

    def switch_context(self, context: str):
        node = self.tree.find_child(context)
        if node is None:
            raise RuntimeError("Context not found: ", context, self)
        else:
            self.working_node = node
            return

    def switch_context_by_level(self, title):  # go up until "title" is a child of working_node (concerning levels)
        while True:
            level_old = Entry.level_of_title(self.working_node.print_name)
            level_new = Entry.level_of_title(title)

            if level_old >= level_new:
                self.working_node = self.working_node.parent
            else:
                break

    def __repr__(self):
        return f"WikiParser2"

    def start_entry(self, title: str):
        node = self.tree.find_child(title)

        if node is None:
            node = Entry(print_name=title, info=None, content=None, aliases=None)
            self.working_node.add_child(node)
            self.working_node = node
        else:
            if Entry.level_of_title(title) != node.level():  # the two don't fit!
                raise RuntimeError("Existing Node and New Node collide with different levels!", self)
            # switch to existing node
            self.working_node = node

        self.mode = "entry-info"
        self.entry = self.new_entry()
        self.entry['print_name'] = title
        self.entry['node'] = node

    def set_info(self, info: str):
        self.mode = "entry-content"

        if info is not None:
            self.entry['info'] = info
        else:
            self.entry['info'] = self.default_info_string

    def add_content(self, line: str):
        self.entry['content'].append(line)

    def end_entry(self):
        if self.entry is None or self.entry['print_name'] is None:  # shouldn't happen thanks to prev. null-checks
            raise RuntimeError("Don't have an entry to end!", self)

        content = "\n".join(self.entry['content'])
        content = Entry.format_content(content)
        info = self.entry['info']
        print_name = self.entry['print_name']
        child = Entry(print_name=print_name, aliases=None, info=info, content=content)

        self.working_node.merge_with(child, replace=True)

        self.mode = "entry-title"
        self.entry = None

    @staticmethod
    def parse_entries_and_insert_with_overwrite(lines, wiki, syntax="wiki", default_info_string=None):
        pars = WikiParser(tree=wiki, syntax=syntax, default_info_string=default_info_string)
        while True:
            line = lines.pop(0) if len(lines) > 0 else None

            if line is None:
                pars.process_end_of_text()
                break
            else:
                no_retry = pars.process_line(line)
                if no_retry is False:
                    lines.insert(0, line)
                continue

    @staticmethod
    def line_title(line: str):
        m = re.match(r"^([#]+)[\s]*([\S][\S\s]*?)[\s]*$", line)
        return line.strip() if m else None

    @staticmethod
    def line_title_with_context(line: str):
        m = re.match(r"^([#]+)[\s]*([\S].*?)[\s]*\[(.*?)\][\s]*$", line)
        return (m.group(1) + " " + m.group(2), m.group(3).strip()) if m else (None, None)

    @staticmethod
    def line_empty(line):
        m = re.match(r"^[\s\-]*$", line)
        return m is not None

    @staticmethod
    def line_entry_info(line):
        m = re.match(r"^[\s\*\:]*info[\s\*\:]*([\s\S]*)$", line, re.IGNORECASE)
        return m.group(1) if m else None

    @staticmethod
    def line_content(line):
        if re.match(r"^[\s]*\-\-[\-]+[\s]*$", line):  # separator ---
            return False
        if re.match(r"^([#]+)(.*)$", line):  # headline
            return False
        return True


def parse_entries_and_insert_with_overwrite(wiki, files: list, syntax="wiki"):
    for f in files:
        f = f[:-3]
        print(f)
        with open(f"{f}.md", "r") as file:
            with open(f"{f}.json", "r") as meta_file:
                meta = json.loads(meta_file.read())
                lines = file.readlines()

                if meta['url'] is None or meta['author'] is None:
                    default_info_string = None
                else:
                    default_info_string = f"/u/{meta['author']} [Turn {meta['turn']}]({meta['url']})"
                WikiParser.parse_entries_and_insert_with_overwrite(lines, wiki, syntax, default_info_string)

    return wiki


def split_into_files(wiki: Entry):
    wiki_pages = RedditWikiReader.wiki_pages

    topcats = {}

    wiki = wiki.copy()

    for page in wiki_pages:
        topcats[page] = wiki.find_child(page)
        if topcats[page] is not None:
            wiki.children.remove(topcats[page])

    if len(wiki.children) > 0:
        topcats['misc'] = wiki
    else:
        topcats['misc'] = None

    return topcats
