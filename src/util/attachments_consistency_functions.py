import os
import fnmatch
import re
from shutil import copyfile

# Function that will find all relatives paths on a note and change them accordingly
# if the note is moved to a new root folder, the attachment will also be copied accordingly
# Paths need to be absolute
def fix_note_consistency(old_path, new_path, hobbes_db):

        # First parse the text for links
        link_re = re.compile(r'^!?\[([^\]]+)\]\(([^)]+)\)$', flags=re.MULTILINE)

        with open(old_path) as f:

            text = f.read()

        # Save for substitutions
        new_text = text

        # Find all the local links on the note
        for match in link_re.findall(text):

            if 'local_image' in match[0] or 'file: ' in match[0]:

                print("Path", match[1])

                # Get the absolute path of the attachment
                os.chdir(os.path.split(old_path)[0]) 
                old_attachment_path = os.path.abspath(match[1])
                attachment_name = os.path.basename(old_attachment_path)

                # Get the root folder of the new location
                new_root_folder_name = new_path.replace(hobbes_db, '').split('/')[1]
                new_root_folder_path = os.path.join(hobbes_db, new_root_folder_name)

                # Create the attachment folder if it does not exist
                if not os.path.exists(os.path.join(new_root_folder_path, '.attachments')):

                    os.mkdir(os.path.join(new_root_folder_path, '.attachments'))

                # Path where the attachment should be
                new_attachment_path = os.path.join(new_root_folder_path, '.attachments', attachment_name)

                # Check if the attachment exists there, and copy it if necessary
                if not os.path.isfile(new_attachment_path):

                    copyfile(old_attachment_path, new_attachment_path)

                # At this point we are sure that the attachment is in the attachments
                # folder of the root folder, modify the URL
                # Add the correctly formated relative URL
                relative_path = os.path.relpath(new_attachment_path, os.path.split(new_path)[0])

                print("Change from", match[1], " to", relative_path)
                new_text = new_text.replace(match[1], relative_path)


        # Write the corrected paths to the file
        with open(old_path, "w") as f:

           f.write(new_text)

# Function that finds all notes inside a folder and calls the 
# fix_note_consistency function accoredingly
def fix_folder_consistency(old_path, new_path, hobbes_db):

    new_absolute_path = os.path.join(new_path, os.path.split(old_path)[-1])

    # FInd all notes
    for path, dirs, files in os.walk(old_path):
        for filename in fnmatch.filter(files, "*.md"):

            old_note_path = os.path.join(path, filename)
            new_note_path = old_note_path.replace(old_path, new_absolute_path)

            # Fix the consistency of each note
            fix_note_consistency(old_note_path, new_note_path, hobbes_db)