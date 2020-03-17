## GodhoodWB Bot

This project aims to create a bot for r/godhoodwb which helps the people in various ways.

The bot should have the following properties:

1. **easy**: no complex syntax is required to use it
2. **fail-safe**: texts only ever experience minor changes, and always with human supervision
3. **non-intrusive**: the bot syntax is subtle and bot messages are short
4. **non-essential**: the bot can (to some degree) be instantly replaced by a human worker
5. **helpful**: the bot offers small pieces of help, but does not require you to take any or all of them

The following features are planned:

### Wiki-Parsing [![Generic Badge](https://img.shields.io/badge/completion-100%25-green)](https://shields.io)

The wiki is parsed into a tree of ***entries***.
 
An entry has the following syntax:
```
### The Name of Entry

Info: /u/responsible_player [Turn X](link_to_relevant_comment)

A description follows, over multiple lines.
It may not contain any headlines (##), as those start a new entry, although perhaps a child entry.
Separators (---) are also forbidden.

#### Child Entry

Every entry needs to have a description, but the info line is optional.

Child entries need to have more "#"s in their headline than the parent entry.

---

Horizontal separators signal the end of an entry, no more description or child entries will follow.
They usually aren't required to be added by the user, and if the user adds some, 
they might be removed during formatting.
```

### Wiki-Sorting and -Formatting [![Generic Badge](https://img.shields.io/badge/completion-100%25-green)](https://shields.io)

The parsed wiki tree can be sorted and formated. 
The tree structure is retained, child entries are sorted such that deepest headlines come first, and then alphabetically.

Example:
```
# The World
#### Master Copy
## Biomes
### North Pole
#### The Arktis
#### Bering Strait
### Rainforest
```

### Wiki-Parsing from Comments [![Generic Badge](https://img.shields.io/badge/completion-33%25-orange)](https://shields.io)

Besides the wiki pages, the bot can also parse sections of comments. 
The sections need to be marked with a start and end command, each taking a whole line.
Markdown formatting and out-of-context brackets (`[]`) are optional.

The start command is `wikibot start <entry>`, where `<entry>` is some existing entry in the wiki.
The subsequently parsed entries are then inserted as the children of `<entry>`.
If a child-entry already exists, instead it is updated.

End commands either have the form `wikibot end` or are simply the end of a comment.

### Human Wiki-Editing [![Generic Badge](https://img.shields.io/badge/completion-0%25-red)](https://shields.io)

If a human edits the wiki, the bot will not overwrite the changes with older information (it uses timestamps for that). 
Changes to the info or the description of some wiki entry are safe in that regard, 
and can even be used to fix errors the bot made.

Only syntax formatting and ordering of posts will not be retained.

Adding a new wiki entry is easily doable as well.

Deleting a wiki entry might be a bit more elaborate, and the bot will have to be updated when that becomes necessary.

### Wiki-Links [![Generic Badge](https://img.shields.io/badge/completion-50%25-yellow)](https://shields.io)

If you use a wiki-link in your comments, the bot will respond with a collection of links to the respective wiki entries, 
using the tooltip to display their description.

The syntax in your comment is `[[arktis]]`, which is displayed as [[arktis]].

The bot's respond will be displayed as
[The Arktis](https://www.reddit.com/r/godhoodwb/wiki/godhoodwb19/wiki/world#wiki_arktis "lots of ice"),
with syntax

`[The Arktis](https://www.reddit.com/r/godhoodwb/wiki/godhoodwb19/wiki/world#wiki_arktis "lots of ice")`

### Website - Checking the Bot [![Generic Badge](https://img.shields.io/badge/completion-0%25-red)](https://shields.io)

There is a website which runs the bot.

It allows you to check how the bot will interpret your comment, displaying which line is which and
providing error messages.

You can use it to learn how the bot works, although I think using it to write/pre-format the reddit comments
is too much of a hastle (switching browser taps etc.).

It also won't safe your work, so beware sudden loss of text!

