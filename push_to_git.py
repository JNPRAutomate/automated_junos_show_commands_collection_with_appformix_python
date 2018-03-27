import git
import os
import junos_devices

def collect_and_push(dev):
#    dev='10.49.124.59'
    cwd = os.getcwd()
    repo = git.Repo(cwd)
    # print repo.git.status()
    repo.git.pull('origin', 'master')
    junos_devices.collect_junos_commands(dev)
    # f=open(cwd + '/test.md', 'w')
    # f.write("blabla")
    # f.close()

    # print repo.git.status()
    # print repo.git.add("test.md")
    # repo.git.add("test.md")
    print repo.git.add(".")

    # print repo.git.status()
    # print repo.git.commit(m = "from Gitpython")
    repo.git.commit(m = "from Gitpython")
    # print repo.git.status()
    # print repo.git.push()
    repo.git.push('origin', 'master')
    return "done"
