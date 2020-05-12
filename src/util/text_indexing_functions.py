# For text indexing
from whoosh import index
from whoosh.fields import Schema, ID, TEXT, DATETIME
from whoosh.qparser import MultifieldParser
import datetime
import os
from itertools import tee
import fnmatch

'''
    From the Whoosh docs, incremental indexing of the files
'''
def index_my_docs(db_path, dirname, clean=False):

    # If the index folder does not exist create it
    if not os.path.exists(os.path.join(db_path, dirname)):

        os.mkdir(os.path.join(db_path, dirname))
        
        # Do a clean indexing
        clean_index(db_path, dirname)
        return 

    if clean:

        clean_index(db_path, dirname)
    else:

        incremental_index(db_path, dirname)

def clean_index(db_path, dirname):
    # Always create the index from scratch
    ix = index.create_in(os.path.join(db_path, dirname), schema=get_schema())
    writer = ix.writer()

    # Assume we have a function that gathers the filenames of the
    # documents to be indexed
    for path in my_docs(db_path):
        add_doc(writer, path)

    writer.commit()

def my_docs(db_path):

    # Get all the txt files from a given path
    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(db_path) for f in filenames if os.path.splitext(f)[1] == '.md']
    return result

def get_schema():

    return Schema(path=ID(unique=True, stored=True), title=TEXT(stored=True), time=DATETIME(stored=True), content=TEXT)

def add_doc(writer, path):

    fileobj = open(path, "rb")
    content = fileobj.read()
    fileobj.close()
    title = os.path.basename(path).split(".")[0]

    # The last time the file was modified
    mtime = os.path.getmtime(path)

    # Convert seconds since epoch to readable timestamp
    modification_time = datetime.datetime.fromtimestamp(mtime)

    writer.add_document(path=path, content=content.decode("utf-8", "strict"), title=title, time=modification_time)

# Deletes a document
def del_doc(db_path, dirname, note_path):

    ix = index.open_dir(os.path.join(db_path, dirname))

    with ix.searcher() as searcher:

        writer = ix.writer()
        writer.delete_by_term('path', note_path)

        writer.commit()

def incremental_index(db_path, dirname):

    ix = index.open_dir(os.path.join(db_path, dirname))

    # The set of all paths in the index
    indexed_paths = set()

    # The set of all paths we need to re-index
    to_index = set()

    with ix.searcher() as searcher:
        writer = ix.writer()

        indexed_path = None

        # Loop over the stored fields in the index
        for fields in searcher.all_stored_fields():
            indexed_path = fields['path']
            indexed_paths.add(indexed_path)

        # There is nothing, clean reindex just in case
        if indexed_path == None:

            index_my_docs(db_path, dirname, True)

            return

        if not os.path.exists(indexed_path):
            # This file was deleted since it was indexed
            writer.delete_by_term('path', indexed_path)

        else:
            # Check if this file was changed since it
            # was indexed
            indexed_time = fields['time']
            mtime = os.path.getmtime(indexed_path)
            modification_time = datetime.datetime.fromtimestamp(mtime)

            if modification_time > indexed_time:
                # The file has changed, delete it and add it to the list of
                # files to reindex
                writer.delete_by_term('path', indexed_path)
                to_index.add(indexed_path)

        # Loop over the files in the filesystem
        # Assume we have a function that gathers the filenames of the
        # documents to be indexed
        for path in my_docs(db_path):
            if path in to_index or path not in indexed_paths:
                # This is either a file that's changed, or a new file
                # that wasn't indexed before. So index it!
                add_doc(writer, path)

        writer.commit()

# Removes all notes from indexer
def delete_folder(db_path, dirname, folder_path):

    # Find all notes
    for path, dirs, files in os.walk(folder_path):
        for filename in fnmatch.filter(files, "*.md"):

            note_path = os.path.join(path, filename)
            del_doc(db_path, dirname, note_path)

# Reindexes only one file, useful when saving a note
def reindex_one_note(db_path, dirname, note_path):

    ix = index.open_dir(os.path.join(db_path, dirname))

    with ix.searcher() as searcher:

        writer = ix.writer()
        writer.delete_by_term('path', note_path)
        add_doc(writer, note_path)

        writer.commit()

# Recursively reindexes all notes on a given dir, useful when moving folders
def reindex_one_moving_folder(db_path, dirname, prev_path, new_path):

    # Find all notes
    for path, dirs, files in os.walk(prev_path):
        for filename in fnmatch.filter(files, "*.md"):

            old_note_path = os.path.join(path, filename)

            new_note_path = old_note_path.replace(prev_path, new_path)

            reindex_moving_note(db_path, dirname, old_note_path, new_note_path)

# Reindexes a note before it is moved, useful when using shutil.move
def reindex_moving_note(db_path, dirname, old_note_path, new_note_path):

    ix = index.open_dir(os.path.join(db_path, dirname))

    with ix.searcher() as searcher:

        writer = ix.writer()
        writer.delete_by_term('path', old_note_path)

        fileobj = open(old_note_path, "rb")
        content = fileobj.read()
        fileobj.close()
        title = os.path.basename(old_note_path).split(".")[0]

        # The last time the file was modified
        mtime = os.path.getmtime(old_note_path)

        # Convert seconds since epoch to readable timestamp
        modification_time = datetime.datetime.fromtimestamp(mtime)

        writer.add_document(path=new_note_path, content=content.decode("utf-8", "strict"), title=title, time=modification_time)

        writer.commit()


# Reindexes only one file with a different path, useful when moving a note
def reindex_one_moved_note(db_path, dirname, old_note_path, new_note_path):

    ix = index.open_dir(os.path.join(db_path, dirname))

    with ix.searcher() as searcher:

        writer = ix.writer()
        writer.delete_by_term('path', old_note_path)
        add_doc(writer, new_note_path)

        writer.commit()

# Searches for a given string
def do_search(query_string, hobbes_db):

    ix = index.open_dir(os.path.join(hobbes_db, '.text_index'))

    with ix.searcher() as searcher:

        parser = MultifieldParser(["title", "content"], schema=ix.schema)

        query = parser.parse(query_string)
        results = searcher.search(query, terms=True, limit=None)

        # Return a list of named tuples
        ret = []

        for hit in results:

            ret.append({'path': hit['path'], 'title': hit['title']})

    return ret