import os

dirs = ["Addendum", "Bookmarks", "IMDEA", "Miscellaneous", "Personal", "Personal projects", "Quotes", "Technology", "Vegan"]

for d in dirs:
    for path, subdirs, files in os.walk(dirs):
        for name in files:
            print(os.path.join(path, name))