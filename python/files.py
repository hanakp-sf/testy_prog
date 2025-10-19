#!/usr/bin/env python3
"""
List files in a directory tree printing full path and size.

Usage:
  python list_files.py [path] [--human-readable] [--follow-symlinks]

If no path is given, the current directory is used.
"""
import os
import sys
import argparse

def human_readable_size(num, suffix="B"):
    for unit in ("", "K", "M", "G", "T", "P"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"

def list_files(base_path, human_readable=False, follow_symlinks=False, out_file=None, sort=True):
    """
    Traverse base_path and collect lines (full_path\tsize).
    If sort is True, return them sorted alphabetically (case-insensitive on Windows).
    If out_file is provided, the caller will write lines to it after sorting.
    """
    lines = []
    # Use os.walk to traverse directory tree
    for root, dirs, files in os.walk(base_path, followlinks=follow_symlinks):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                # If follow_symlinks is False, use lstat to avoid following links
                if follow_symlinks:
                    st = os.stat(full_path)
                    size = st.st_size
                else:
                    st = os.lstat(full_path)
                    if os.path.islink(full_path):
                        # try to get target size, fall back to link size
                        try:
                            size = os.stat(full_path).st_size
                        except Exception:
                            size = st.st_size
                    else:
                        size = st.st_size

                if human_readable:
                    size_str = human_readable_size(size)
                else:
                    size_str = str(size)

                line = f"{full_path.split(':')[-1]}:{size_str}"
                lines.append(line)
            except (OSError, PermissionError) as e:
                print(f"ERROR: {full_path}: {e}", file=sys.stderr)

    if sort:
        # On Windows, sort case-insensitively to match Explorer behavior
        if os.name == "nt":
            lines.sort(key=lambda s: s.lower())
        else:
            lines.sort()

    return lines

def main():
    parser = argparse.ArgumentParser(description="Traverse directory and print file path and size")
    parser.add_argument("path", nargs="?", default=".", help="Directory to traverse (default: current dir)")
    parser.add_argument("--human-readable", "-H", action="store_true", help="Show sizes in human readable form (e.g., 1.2K, 3.4M)")
    parser.add_argument("--follow-symlinks", "-L", action="store_true", help="Follow symbolic links")
    parser.add_argument("--output", "-o", help="Write results to this file")
    parser.add_argument("--append", "-a", action="store_true", help="Append to output file instead of overwriting")
    #parser.add_argument("--no-sort", dest="no_sort", action="store_true", help="Don't sort results; stream in filesystem order")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: path does not exist: {args.path}", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(2)
    out_f = None
    if args.output:
        mode = "a" if args.append else "w"
        try:
            out_f = open(args.output, mode, encoding="utf-8")
        except Exception as e:
            print(f"Error: cannot open output file {args.output}: {e}", file=sys.stderr)
            sys.exit(3)

    try:
        lines = list_files(args.path, human_readable=args.human_readable, follow_symlinks=args.follow_symlinks, out_file=out_f, sort=True)
        for line in lines:
            print(line)
            if out_f:
                try:
                    out_f.write(line + "\n")
                except Exception as e:
                    print(f"ERROR writing to output file: {e}", file=sys.stderr)
    finally:
        if out_f:
            out_f.close()

if __name__ == "__main__":
    main()