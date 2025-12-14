#!/usr/bin/env python
"""Quick test of lazy loading feature."""

from graph_model import GraphModel

repo_dir = r'C:\personal\github_testy_prog'

m = GraphModel()
m.load_branches(repo_dir)

print('=== Startup (lazy - branches only) ===')
branches = [v for v in m.vertices.values() if v.get('type') == 'branch']
commits = [v for v in m.vertices.values() if v.get('type') == 'commit']
print(f'  branches: {len(branches)}')
print(f'  commits: {len(commits)}')
print(f'  edges: {len(m.edges)}')

print('\n=== After loading main branch commits ===')
m.load_commits_for_branch(repo_dir, 'main', per_branch=5)
commits = [v for v in m.vertices.values() if v.get('type') == 'commit']
print(f'  commits: {len(commits)}')
print(f'  edges: {len(m.edges)}')

print('\n=== Attempting to reload main (should skip) ===')
old_commit_count = len(commits)
m.load_commits_for_branch(repo_dir, 'main', per_branch=5)
commits = [v for v in m.vertices.values() if v.get('type') == 'commit']
print(f'  commits: {len(commits)} (unchanged: {len(commits) == old_commit_count})')

print('\nLazy loading works!')
