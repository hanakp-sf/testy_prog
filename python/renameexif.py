#!/usr/bin/env python3
"""
Rename exif files to YYYYMMDD_HHMMSS.* based on EXIF DateTimeOriginal tag.

Examples:
  python renameexif.py .               # dry-run by default
  python renameexif.py -r -n .         # actually rename (no dry-run)
  python renameexif.py -r --on-collision number .  # append counter on collision

Options:
  -r, --recursive      Recurse into subdirectories
  -n, --rename         Perform renaming (by default the script only shows what would be done)
  --collision {skip,overwrite,number}
                       Action when the target filename already exists:
                         skip (default) - leave original, report
                         overwrite      - replace existing target
                         number         - append _1, _2, ... before extension
  -v, --verbose        More output

  Requires:  piexif
"""
from __future__ import annotations
import argparse
import os
from typing import Iterator, Tuple
import datetime
import piexif

def find_matching_files(root: str, recursive: bool) -> Iterator[Tuple[str, str]]:
    """Yield (dirpath, filename) for all files."""
    if recursive:
        for dirpath, dirs, files in os.walk(root):
            for fn in files:
                yield dirpath, fn
    else:
        for fn in os.listdir(root):
            p = os.path.join(root, fn)
            if os.path.isfile(p):
                yield root, fn

def make_new_filename(dirpath: str, fn: str) -> str:
    """Given a directory path and filename, return new filename based on EXIF DateTimeOriginal."""
    src = os.path.join(dirpath, fn)
    try:
        exif_dict = piexif.load(src)
        # Get the DateTimeOriginal tag from EXIF data (36867 is the tag ID)
        datetime_original = exif_dict.get("Exif", {}).get(36867, b"--").decode("utf-8", errors="ignore")
        if datetime_original == "--":
            return fn
        dt = datetime.datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S")
        new_name = dt.strftime("%Y%m%d_%H%M%S") + os.path.splitext(fn)[1]
        return new_name  
    except Exception as e:
        return fn

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
    parser = argparse.ArgumentParser(description="Rename EXIF files to YYYYMMDD_HHMMSS.* based on EXIF DateTimeOriginal tag")
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
        new_fn = make_new_filename(dirpath, fn)
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