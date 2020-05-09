import os
import fnmatch
import re
from shutil import copyfile

'''

    - When [moving a note, moving a folder] fix relative paths of attachments

        - [Moving a note] Check that note text and fix path
            - If it has been moved between root folders, copy the attachments to the other root folder
        - [Moving a folder] Check all the notes on that directory and subdirectories
            - If it has been moved between root folders, copy the attachments to the other root folder

        - File example:   [file: Iaia_manual.pdf](../.attachments/cc304c8db3e8f4d190ed6aba143e99c0ed0e3c70df79d3305b1e40c43ce80285.pdf)
        - Image example: ![local_image](../.attachments/77b9196aff91bb1a99484c40237870a239d31a0d168d43413588e300270ba272.png)

        - https://stackoverflow.com/questions/4205854/python-way-to-recursively-find-and-replace-string-in-text-files
'''

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
