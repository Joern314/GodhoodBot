from wiki import Entry
import wiki_parser
import reddit_crawl
import glob

# files = reddit_crawl.crawl_all(reddit_crawl.test_url, 8)
files_comm = glob.glob("./data/fhftm0/*.md")
files_wiki = glob.glob("./data/wiki/*.md")

wiki = Entry.create_wiki_root()
wiki_parser.parse_entries_and_insert_with_overwrite(wiki, files_wiki, "wiki")
wiki_parser.parse_entries_and_insert_with_overwrite(wiki, files_comm, "comment")

wiki_pages = wiki_parser.split_into_files(wiki)
