# OLD VERSION!
# used different syntax

raise Exception("old package")

import regex as re

from wiki import Entry


class WikiParser:
    def __init__(self, lines, default_info_string=None):
        self.lines = lines
        self.pointer = 0
        self.default_info_string = default_info_string

    @staticmethod
    def line_attention_start(line: str):
        m = re.match(r"^([\s\[\*]*)wikibot([\s\*]+)start([\s\*]+)(.*?)([\s\]\*]*)$", line, re.IGNORECASE)
        if m is None:
            return None
        else:
            return m.group(4)

    @staticmethod
    def line_attention_end(line: str):
        m = re.match(r"^([\s\[\*]*)wikibot([\s\*]+)end([\s\]\*]*)$", line, re.IGNORECASE)
        return m is not None

    @staticmethod
    def attention_filter(lines):
        filtered = []
        active = False
        for line in lines:
            cat = WikiParser.line_attention_start(line)
            end = WikiParser.line_attention_end(line)
            if cat is not None:
                cat = Entry.normalize(cat)
                active = True
                filtered.append("# " + cat)  # top-level context switch
            elif end is True:
                assert (active is True)
                active = False
            else:
                if active:
                    filtered.append(line)
                else:
                    continue
        return filtered

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
        old_ptr = self.pointer

        self.skip_empty_lines()
        if self.ended():
            self.pointer = old_ptr
            return None  # can't parse, roll back

        name = self.line_title(self.ptr())
        if name is None:
            self.pointer = old_ptr
            return None  # can't parse, roll back
        else:
            self.inc()

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

        return entry

    def default_info(self, title):
        level = Entry.level_of_title(title)
        if level <= 2:  # part of the standard tree
            return None
        else:
            return self.default_info_string

    def parse_tree(self):
        flat = []
        while True:
            e = self.parse_entry()
            if e is None:  # no entry is coming
                break
            else:
                flat.append(e)

        root = Entry("root")  # level 0 root
        branch = [root]

        while len(flat) > 0:
            node = flat.pop(0)
            level_new = node.level()
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
