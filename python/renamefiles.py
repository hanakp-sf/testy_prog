#!/usr/bin/env python3
"""
Rename files named like YYYYMMDD_HHMMSS.ext -> YYYY-MM-DD_HH-MM-SS.ext

Examples:
  python renamefiles.py .               # dry-run by default
  python renamefiles.py -r -n .         # actually rename (no dry-run)
  python renamefiles.py -r --on-collision number .  # append counter on collision

Options:
  -r, --recursive      Recurse into subdirectories
  -n, --rename         Perform renaming (by default the script only shows what would be done)
  --collision {skip,overwrite,number}
                       Action when the target filename already exists:
                         skip (default) - leave original, report
                         overwrite      - replace existing target
                         number         - append _1, _2, ... before extension
  -v, --verbose        More output
"""
from __future__ import annotations
import argparse
import os
import re
from typing import Iterator, Tuple

# Pattern: start-of-string, 8 digits (YYYYMMDD), underscore, 6 digits (HHMMSS), then rest as extension/name
PAT = re.compile(r'^(?P<date>\d{8})_(?P<time>\d{6})(?P<rest>\..+)$')

def find_matching_files(root: str, recursive: bool) -> Iterator[Tuple[str, str]]:
    """Yield (dirpath, filename) for files matching the pattern."""
    if recursive:
        for dirpath, dirs, files in os.walk(root):
            for fn in files:
                if PAT.match(fn):
                    yield dirpath, fn
    else:
        for fn in os.listdir(root):
            p = os.path.join(root, fn)
            if os.path.isfile(p) and PAT.match(fn):
                yield root, fn

def make_new_name(fn: str) -> str:
    """Convert 'YYYYMMDD_HHMMSS.ext' -> 'YYYY-MM-DD_HH-MM-SS.ext'"""
    m = PAT.match(fn)
    if not m:
        raise ValueError("filename does not match pattern")
    d = m.group('date')   # YYYYMMDD
    t = m.group('time')   # HHMMSS
    rest = m.group('rest')  # .ext (including dot)
    new = f"{d[0:4]}-{d[4:6]}-{d[6:8]}_{t[0:2]}-{t[2:4]}-{t[4:6]}{rest}"
    return new

def resolve_collision(target_path: str, strategy: str) -> str | None:
    """
    Given a desired target_path and collision strategy:
      - 'skip' -> return None to skip
      - 'overwrite' -> return target_path
      - 'number' -> find an available target by appending _1, _2...
    """
    if not os.path.exists(target_path):
        return target_path
    if strategy == 'skip':
        return None
    if strategy == 'overwrite':
        return target_path
    if strategy == 'number':
        base, ext = os.path.splitext(target_path)
        i = 1
        while True:
            candidate = f"{base}_{i}{ext}"
            if not os.path.exists(candidate):
                return candidate
            i += 1
    raise ValueError(f"unknown collision strategy: {strategy}")

def main():
    parser = argparse.ArgumentParser(description="Rename YYYYMMDD_HHMMSS.* -> YYYY-MM-DD_HH-MM-SS.*")
    parser.add_argument("path", nargs="?", default=".", help="Directory to process (default: current dir)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recurse into subdirectories")
    parser.add_argument("-n", "--rename", action="store_true", help="Actually perform renaming (default: dry-run)")
    parser.add_argument("--collision", choices=("skip","overwrite","number"), default="skip", help="Collision handling for existing targets")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    root = os.path.abspath(args.path)
    to_rename = []
    for dirpath, fn in find_matching_files(root, args.recursive):
        src = os.path.join(dirpath, fn)
        new_fn = make_new_name(fn)
        dst = os.path.join(dirpath, new_fn)
        to_rename.append((src, dst))

    # Sort by full path for predictable order
    to_rename.sort(key=lambda x: x[0].lower() if os.name == 'nt' else x[0])

    if not to_rename:
        print("No matching files found.")
        return

    print(f"Found {len(to_rename)} file(s) to consider.")
    performed = 0
    skipped = 0
    errors = 0

    for src, dst in to_rename:
        print(f"{src} -> {dst}")
        if not args.rename:
            continue
        # check collision
        resolved = resolve_collision(dst, args.collision)
        if resolved is None:
            skipped += 1
            if args.verbose:
                print(f"  Skipping (target exists): {dst}")
            continue
        try:
            # Ensure destination directory exists (it will, because same dir)
            if resolved != dst and args.verbose:
                print(f"  Renaming to numbered target: {resolved}")
            os.replace(src, resolved)  # atomic if on same filesystem
            performed += 1
        except Exception as e:
            print(f"  ERROR renaming {src} -> {resolved}: {e}")
            errors += 1

    print("Summary:")
    print(f"  considered: {len(to_rename)}")
    print(f"  renamed  : {performed}")
    print(f"  skipped  : {skipped}")
    print(f"  errors   : {errors}")

if __name__ == "__main__":
    main()