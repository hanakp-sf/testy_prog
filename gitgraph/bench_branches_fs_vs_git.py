#!/usr/bin/env python3
"""Benchmark: filesystem refs vs `git for-each-ref`.

Compares:
 - filesystem: read refs from .git/refs and packed-refs via GraphModel helpers
 - git: run `git for-each-ref --format="%(refname:short) %(objectname)" refs/heads/`

Adjust `RUNS` for iterations. Runs from the repository root by default.
"""
import time
import subprocess
import os
import sys

from graph_model import GraphModel

REPO = os.path.abspath(os.getcwd())
# allow passing repo path as first arg
if len(sys.argv) > 1:
    REPO = os.path.abspath(sys.argv[1])

RUNS = 30

def method_fs(repo, runs=RUNS):
    gm = GraphModel()
    gitdir = gm._resolve_git_dir(repo)
    if not gitdir:
        raise RuntimeError('.git directory not found')
    t0 = time.perf_counter()
    out = None
    for _ in range(runs):
        out = gm._read_refs_from_gitdir(gitdir)
    t = time.perf_counter() - t0
    return t, out


def method_git(repo, runs=RUNS):
    cmd = ['git', '-C', repo, 'for-each-ref', '--format=%(refname:short) %(objectname)', 'refs/heads/']
    t0 = time.perf_counter()
    out = None
    for _ in range(runs):
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = p.stdout
    t = time.perf_counter() - t0
    return t, out


def summarize_fs(out):
    branches = sorted(out.keys()) if isinstance(out, dict) else []
    return branches


def summarize_git(out):
    lines = [l for l in out.splitlines() if l.strip()]
    branches = [l.split()[0] for l in lines]
    return sorted(branches)


if __name__ == '__main__':
    print('Repository:', REPO)
    print('Runs per method:', RUNS)
    print()

    print('Running filesystem-based ref read...')
    try:
        t_fs, out_fs = method_fs(REPO)
        branches_fs = summarize_fs(out_fs)
        print(f'  total: {t_fs:.4f}s, avg: {t_fs/RUNS*1000:.3f} ms')
    except Exception as e:
        print('  filesystem method failed:', e)
        branches_fs = []

    print('\nRunning git for-each-ref...')
    try:
        t_git, out_git = method_git(REPO)
        branches_git = summarize_git(out_git)
        print(f'  total: {t_git:.4f}s, avg: {t_git/RUNS*1000:.3f} ms')
    except Exception as e:
        print('  git method failed:', e)
        branches_git = []

    print('\nSample branches (fs):', branches_fs[:10])
    print('Sample branches (git):', branches_git[:10])

    # show counts and equality
    print('\nCount fs:', len(branches_fs), 'Count git:', len(branches_git))
    print('Branches equal:', branches_fs == branches_git)
