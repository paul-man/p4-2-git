import json
import os
import subprocess
import sys
import pdb

root = os.getcwd()

f = open('repos.json')
data = json.load(f)
f.close()

def callSubProcess(cmd, shell_flag):
    print('* CMD: {}'.format(cmd))
    subprocess.call(cmd, shell = shell_flag)

def clone(repo, env, depot_str, exclude):
    repo_dir = repo['repo_dir']
    callSubProcess("~/gitfiles/git-p4 clone --branch=refs/remotes/p4/{0}{1}{2} {3}".format(env, exclude, depot_str, repo_dir), True)
    os.chdir(repo_dir)
    if repo_dir == 'www':
        callSubProcess("rm -rf js_lib", True)
    callSubProcess("git remote add origin {}".format(repo['origin']), True)

def sync(repo, env, depot_str, exclude):
    callSubProcess("~/gitfiles/git-p4 sync --branch=refs/remotes/p4/{0}{1}{2}".format(env, exclude, depot_str), True)

def branchAndPush(env, subtree_dir, subtree_repo, update=False):
    checkout_flag = "" if update else "-b "
    callSubProcess("git checkout {0}{1} refs/remotes/p4/{1}".format(checkout_flag, env), True)
    if subtree_dir:
        if repo_dir == 'www':
            callSubProcess("rm -rf js_lib", True)
        callSubProcess("git subtree add -P {0} {1} {2}".format(subtree_dir, subtree_repo, env), True)
    callSubProcess("git push origin {} --force".format(env), True)

for repos in data['repos']:
    for repo_name, repo in repos.items():
        repo_dir = repo['repo_dir']
        if len(sys.argv) > 1 and (repo_dir not in sys.argv):
            continue
        # pdb.set_trace()
        print("-"*100)
        branches = repo['branches']
        origin = repo['origin']
        parent_dir = repo['parent_dir']
        try:
            exclude = " " + repo['exclude'] + " "
        except KeyError:
            exclude = " "
        update = False

        # Create ents/ent_bat + chdir
        new_parent = root + "/" + parent_dir
        if not os.path.exists(new_parent):
            os.mkdir(new_parent)
        elif os.path.exists(new_parent + "/" + repo_dir):
            update = True
            print('--- Updating ---')
        if not update:
            print('--- Creating ---')
        os.chdir(new_parent)

        for i, env in enumerate(branches):
            try:
                exclude = " " + repo['exclude'] + " "
            except KeyError:
                exclude = " "
            exclude = exclude.replace("{env}", env)
            depot_str = "//depot/{0}/{1}@all".format(env, parent_dir)
            if not repo_dir == ".":
                depot_str = "//depot/{0}/{1}/{2}@all".format(env, parent_dir, repo_dir)

            if i == 0:
                if update:
                    os.chdir(repo_dir)
                    sync(repo, env, depot_str, exclude)
                else:
                    clone(repo, env, depot_str, exclude)
            else:
                sync(repo, env, depot_str, exclude)
            branchAndPush(env, repo.get('subtree_dir'), repo.get('subtree_repo'), update)

            print("-"*50)
        
        # Go back to root after done with all branches
        os.chdir(root)

print("-"*100)
