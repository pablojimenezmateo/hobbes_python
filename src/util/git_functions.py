# For online sync
from git import Repo, exc
import datetime
import socket
import threading

'''
    GIT on a new thread
'''
def git_commit_and_push_threaded(path):

    t = threading.Thread(daemon=True, target=git_commit_and_push, args=[path])
    t.start()

def git_commit_threaded(path):

    t = threading.Thread(daemon=True, target=git_commit, args=[path])
    t.start()

def git_commit(path):

    # Check if git is already present on the given repo
    try:

        repo = Repo(path)

    except exc.InvalidGitRepositoryError:

        print("Creating repo")

        repo = Repo.init(path)

    # Add new changes
    repo.git.add('--all')
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_name = socket.gethostname()
    repo.index.commit('Changes: ' + date + ' Device: ' + device_name)

'''
    Given a folder, if there is no .git create it
    Then commit the changes, if origin is set up
    pull then push
'''
def git_commit_and_push(path):

        # Check if git is already present on the given repo
        try:

            repo = Repo(path)

        except exc.InvalidGitRepositoryError:

            print("Creating repo")

            repo = Repo.init(path)

        # Check if the git has a remote configured
        git_is_local = True

        try:
            repo.remote(name='origin')
            git_is_local = False

        except ValueError:

            print("Local only")
            git_is_local = True
            git_commit(path)

        # If there is a remote configured do a pull
        if not git_is_local:

            print("Not local, remote configured")

            origin = repo.remote(name='origin')

            # Pull any changes
            try:
                origin.pull()

            except exc.GitCommandError:

                print("Either not internet or origin is not well configured")

            git_commit(path)

            # Push everything
            try:
                origin.push()

            except exc.GitCommandError:

                print("Either not internet or origin is not well configured")