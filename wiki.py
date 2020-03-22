import regex as re


class Entry:
    """A node in the wiki tree"""

    def __init__(self, print_name, aliases=None, parent=None, children=None, info=None, content=None,
                 is_category=False):
        self.print_name = print_name  # "## The X"
        self.aliases = set(map(Entry.normalize, aliases or [print_name]))  # ["x"]

        self.parent = parent or None
        self.children = children or []

        self.info = info
        self.content = content

        self.is_category = is_category  # disable Info-Line and allow switching in parser

    def has_alias(self, name):
        return Entry.normalize(name) in self.aliases

    def find_children(self, alias):
        a = []
        if self.has_alias(alias):
            a += [self]
        for c in self.children:
            a += c.find_children(alias)
        return a

    def find_child(self, alias):
        a = self.find_children(alias)
        if len(a) == 1:
            return a[0]
        elif len(a) == 0:
            return None
        else:
            raise RuntimeError("too many children with alias", alias)

    def get_path(self):
        return (self.parent.get_path() if self.parent is not None else []) + [self.reference_name()]

    def reference_name(self):
        m = re.match(r"^([#]*)([\s]*)([\S][\S\s]*?)([\s]*)$", self.print_name)
        return m.group(3)

    def add_child(self, child):
        if self.find_child(child.print_name) is not None:
            raise RuntimeError("already have child", child.print_name)

        self.children.append(child)
        child.parent = self

    def merge_with_no_recursion(self, other, check_identity=True, replace=False):
        if check_identity and not self.has_alias(other.print_name):
            raise RuntimeError("not the same node as self")

        if other.content is not None and self.content != other.content:
            if self.content is None or replace:
                self.content = other.content
            else:
                raise RuntimeError("two differing contents!")

        if other.info is not None and self.info != other.info:
            if self.info is None or replace:
                self.info = other.info
            else:
                raise RuntimeError("two differing infos")  # two differing infos!
        return True

    def merge_with(self, other, check_identity=True, replace=False):
        self.merge_with_no_recursion(other, check_identity, replace)

        for co in other.children:
            cs = [c for c in self.children if c.has_alias(co.print_name)]
            if len(cs) == 0:
                self.add_child(co.copy())
            elif len(cs) >= 2:
                raise RuntimeError("self was broken")  # self was already broken!
            else:
                ci = cs[0]
                ci.merge_with(co)
        return True

    def copy_no_children(self):
        return Entry(self.print_name, self.aliases, None, None, self.info, self.content, self.is_category)

    def copy(self):
        e = self.copy_no_children()
        for c in self.children:
            e.add_child(c.copy())
        return e

    def __repr__(self):
        return self.to_string(short=True)

    def to_string(self, short=True):
        r = self.print_name + "\n\n"

        if not short and self.info is not None and not self.is_category:
            r += "Info: " + self.info + "\n\n"
        if not short and self.content is not None:
            r += self.content
        for c in self.children:
            r += "\n\n" + c.to_string(short=short) + "\n\n"
        if not short:
            r += "---\n\n"
        return re.sub(r"\n\n[\n]+", "\n\n", r)

    def short_description(self):
        r = self.content
        return re.sub(r"\n[\n]+", "\n", r)

    def sort_children(self):
        self.children.sort(key=lambda c: (-c.level(), Entry.normalize(c.print_name)))

    def sort_children_recursive(self):
        self.sort_children()
        for c in self.children:
            c.sort_children_recursive()

    @staticmethod
    def create_wiki_root():
        tree = (["Wiki"], [
            (["The World"], [
                (["Celestial Bodies"]),
                (["Regions"]),
                (["Landmarks"]),
                (["Lifeforms"]),
                (["Materials"]),
            ]),
            (["The Supernatural"], [
                (["Metaphysics"]),
                (["Magics"]),
                (["Artifacts"]),
                (["Planes"]),
            ]),
            (["Politics"], [
                (["Mortal Races"]),
                (["Cultures"]),
                (["Nations"]),
                (["Organizations"]),
                (["Persons"]),
                (["Technology"]),
            ]),
            (["Divines"], [
                (["Gods"]),
                (["Demigods"]),
                (["Servitors"]),
                (["Avatars"]),
            ]),
        ])

        def from_skeleton(skeleton, level):
            if len(skeleton) == 2:
                aliases, children = skeleton
            else:
                aliases, children = skeleton, []
            name = aliases[0]

            print_name = (("#" * level + " ") if level > 0 else "") + name

            entry = Entry(print_name=print_name, aliases=aliases)
            for c in children:
                ce = from_skeleton(c, level + 1)
                entry.add_child(ce)

            return entry

        return from_skeleton(tree, 0)

    @staticmethod
    def normalize(alias):
        m = re.match(r"^([#]*)([\s]*)(the[\s]*)?([\S][\S\s]*?)([\s]*)$", alias, re.IGNORECASE)
        if m is not None:
            alias = m.group(4)
        else:
            raise RuntimeError("not a valid alias")  # not a valid alias

        return alias.lower()

    @staticmethod
    def level_of_title(title):
        m = re.match(r"^[\s]*([#]*)([\S\s]*)$", title, re.IGNORECASE)
        if m is not None:
            return len(m.group(1))
        else:
            raise RuntimeError("not a valid self")  # self not valid

    def level(self):
        return Entry.level_of_title(self.print_name)

    @staticmethod
    def format_content(content):
        content = re.sub(r"\n\n[\n]+", "\n\n", content)
        content = content.strip()
        return content
