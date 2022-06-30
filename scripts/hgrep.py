import itertools, os, os.path

def hgrep(ui, repo, what, **opts):
    files = []
    status = repo.status(clean=True)

    for f in itertools.chain(status[0], status[1], status[4], status[6]):
        files.append(os.path.join(repo.root, f))

    os.system("grep -n --color %s %s" % (what, ' '.join(files)))

cmdtable = {"hgrep": (hgrep, [], "[what]")}
