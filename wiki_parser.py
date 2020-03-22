import regex as re
import json

from wiki import Entry
from reddit_crawl import RedditWikiReader


class WikiParser2:
    def __init__(self, tree: Entry, syntax="wiki"):
        self.mode = "entry-title"
        self.title = None
        self.entry = None

        self.syntax = syntax

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
        self.entry['info'] = info

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
    def parse_entries_and_insert_with_overwrite(lines, wiki, syntax="wiki"):
        pars = WikiParser2(tree=wiki, syntax=syntax)
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


class WikiParser:
    def __init__(self, lines, default_info_string=None, context_tree=None, syntax_version="wiki"):
        self.lines = lines
        self.pointer = 0
        self.default_info_string = default_info_string
        self.syntax_version = syntax_version
        if context_tree is None:
            context_tree = Entry.create_wiki_root()
        self.context_tree = context_tree

    @staticmethod
    def take_and_parse(lines, default_info, wiki):
        parser = WikiParser(lines, default_info)
        root = parser.parse_tree()
        remainder = lines[parser.pointer:]
        for branch in root.children:
            WikiParser.merge_into(wiki, branch)
        return remainder

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

    def ptr(self):
        return self.lines[self.pointer]

    def inc(self):
        self.pointer += 1
        return not self.ended()

    def ended(self):
        return self.pointer >= len(self.lines)

    def skip_empty_lines(self):
        while not self.ended() and self.line_empty(self.ptr()):
            self.inc()
        return not self.ended()

    def parse_entry(self):
        self.skip_empty_lines()
        if self.ended():
            return None, None  # can't parse

        name, context = self.line_title_with_context(self.ptr())
        if name is None:
            name, context = self.line_title(self.ptr()), None
        self.inc()

        if self.syntax_version == "wiki":  # can't have context switches in the wiki!
            context = None

        if name is None:
            return None, None  # can't parse

        self.skip_empty_lines()
        if not self.ended():
            info = self.line_entry_info(self.ptr())
            if info is not None:
                self.inc()
            else:
                info = self.default_info(name)
        else:
            info = self.default_info(name)

        content = ""
        while not self.ended() and self.line_content(self.ptr()):
            content += self.ptr() + "\n"
            self.inc()

        entry = Entry(print_name=name, aliases=None, parent=None, children=None, info=info, content=content)

        return entry, context

    def default_info(self, title):
        level = Entry.level_of_title(title)
        if level <= 2:  # part of the standard tree
            return None
        else:
            return self.default_info_string

    def parse_tree(self):
        flat = []
        while True:
            e, c = self.parse_entry()
            if c is not None:
                c = self.context_tree.find_child(c)
                if c is not None:
                    flat.append(c.copy_no_children())
                else:
                    raise Exception("context not found")
            if e is None:
                if self.ended():
                    break  # no entry is coming, end of loop
                else:
                    continue  # might have more luck next time
            else:
                flat.append(e)

        root = Entry("wiki")  # level 0 root
        branch = [root]

        while len(flat) > 0:
            node = flat.pop(0)
            level_new = node.level()

            if root.find_child(node.print_name):  # warning: duplicate
                # instead of adding to tree, just jump to this node
                branch = [root.find_child(node.print_name)]
                while branch[0].parent is not None:
                    branch.insert(0, branch[0].parent)
                # instead of insert: merge
                branch[-1].merge_with(node)
            else:  # not a duplicate, sort into tree
                while len(branch) > 1:  # cut back the branch if necessary
                    level_old = branch[-1].level()
                    if level_new <= level_old:  # cut
                        branch = branch[:-1]
                    else:  # no cut
                        break
                parent = branch[-1]
                parent.add_child(node)
                branch.append(node)

        return root

    @staticmethod
    def merge_into(dst: Entry, src: Entry):  # jump over missing layers wherever possible
        opt = dst.find_children(src.print_name)
        if len(opt) == 1 and opt[0] != dst:  # jump downwards the branch
            WikiParser.merge_into(opt[0], src)
            return
        elif len(opt) == 1 and opt[0] == dst:  # we arrived
            dst.merge_with_no_recursion(src)
            for c in src.children:
                WikiParser.merge_into(dst, c)
            return
        elif len(opt) >= 2:  # dst was illegal
            return RuntimeError
        else:  # nothing found, let's make a new destination and use it
            trg = src.copy_no_children()
            dst.add_child(trg)
            WikiParser.merge_into(trg, src)
            return


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
                WikiParser2.parse_entries_and_insert_with_overwrite(lines, wiki, syntax)

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
