"""Helps deploy what we have built."""

import os
import time
from distutils.dir_util import copy_tree
from warnings import warn

from xonsh.api import subprocess

try:
    import hglib
except ImportError:
    hglib = None


def ensure_deploy_dir(rc):
    """Ensure deployment dir is on rc and physically exists."""
    if not hasattr(rc, "deploydir") or rc.deploydir is None:
        rc.deploydir = os.path.join(rc.builddir, "deploy")
    if not os.path.isdir(rc.deploydir):
        os.makedirs(rc.deploydir, exist_ok=True)


def deploy_git(rc, name, url, src="html", dst=None):
    """Loads a git database."""
    targetdir = os.path.join(rc.deploydir, name)
    # get or update the database
    if os.path.isdir(targetdir):
        cmd = ["git", "pull"]
        cwd = targetdir
    else:
        cmd = ["git", "clone", url, targetdir]
        cwd = None
    subprocess.check_call(cmd, cwd=cwd)
    # copy the files over
    srcdir = os.path.join(rc.builddir, src)
    dstdir = os.path.join(targetdir, dst) if dst else targetdir
    copy_tree(srcdir, dstdir, verbose=1)
    # commit everything
    cmd = ["git", "add", "."]
    subprocess.check_call(cmd, cwd=targetdir)
    # commit
    cmd = [
        "git",
        "commit",
        "-m",
        "regolith auto-deploy at {0}".format(time.time()),
    ]
    try:
        subprocess.check_call(cmd, cwd=targetdir)
    except subprocess.CalledProcessError:
        warn("Could not git commit to " + targetdir, RuntimeWarning)
        # don't return, just in case...
    # deploy!
    cmd = ["git", "push"]
    try:
        subprocess.check_call(cmd, cwd=targetdir)
    except subprocess.CalledProcessError:
        warn("Could not git push from " + targetdir, RuntimeWarning)
        return


def deploy_hg(rc, name, url, src="html", dst=None):
    """Loads an hg database."""
    if hglib is None:
        raise ImportError("hglib")
    targetdir = os.path.join(rc.deploydir, name)
    # get or update the database
    if os.path.isdir(targetdir):
        client = hglib.open(targetdir)
        client.pull(update=True)
    else:
        # Strip off hg+
        hglib.clone(url[3:], targetdir)
        client = hglib.open(targetdir)
    # copy the files over
    srcdir = os.path.join(rc.builddir, src)
    dstdir = os.path.join(targetdir, dst) if dst else targetdir
    copy_tree(srcdir, dstdir, verbose=1)
    # commit everything
    client.commit(
        message="regolith auto-deploy at {0}".format(time.time()),
        addremove=True,
    )
    client.push()


def deploy(rc, name, url, src="html", dst=None):
    """Deploys a target."""
    ensure_deploy_dir(rc)
    if url.startswith("git") or url.endswith(".git"):
        deploy_git(rc, name, url, src=src, dst=dst)
    elif url.startswith("hg+"):
        deploy_hg(rc, name, url, src=src, dst=dst)
    else:
        raise ValueError("Do not know how to deploy to this kind of URL: " + url)
