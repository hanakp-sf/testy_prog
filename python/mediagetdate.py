#!/usr/bin/env python3
"""
Extract creation date from a .mov/.3gp file using pymediainfo (MediaInfo).

Usage:
    python mediagetdate.py /path/to/files

Requires: pymediainfo (install via pip)
"""
import sys
import os
import argparse
from datetime import datetime, timezone
from pymediainfo import MediaInfo

def parse_mediainfo_date(s):
    """
    MediaInfo often returns dates like 'UTC 2019-04-10 08:12:34' or '2019-04-10 08:12:34'.
    Try to parse common formats and return an ISO string or None.
    """
    if not s:
        return None
    s = s.strip()
    # remove 'UTC' prefix if present
    if s.upper().startswith("UTC"):
        s = s.split(None, 1)[1]
    # Try several formats
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.isoformat()
        except Exception:
            continue
    # Last resort: return raw string
    return s

def get_creation_time(path):
    """
    Try to extract creation time from media metadata using MediaInfo.
    Returns a string like 'attr: ISO_DATE' or None.
    """
    media_info = MediaInfo.parse(path)
    # Check the general track first
    for track in media_info.tracks:
        if track.track_type == 'General':
            for attr in ("encoded_date", "tagged_date", "file_last_modification_date", "recorded_date", "creation_time"):
                val = getattr(track, attr, None)
                if val:
                    parsed = parse_mediainfo_date(val)
                    return f"{attr}: {parsed}"
    # Check other tracks (video/audio) for similar tags
    for track in media_info.tracks:
        if track.track_type in ("Video", "Audio"):
            for attr in ("encoded_date", "tagged_date", "recorded_date", "creation_time"):
                val = getattr(track, attr, None)
                if val:
                    parsed = parse_mediainfo_date(val)
                    return f"{attr} ({track.track_type}): {parsed}"
    return None


def get_filesystem_ctime(path):
    """Return filesystem creation time as ISO string (UTC aware)."""
    try:
        ts = os.path.getctime(path)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()
        return dt.isoformat()
    except Exception:
        return None


def find_media_files(path, fileformat='mov', recursive=True):
    """Yield absolute paths to media files. If recursive is False, only list in top dir."""
    path = os.path.abspath(path)
    suffix = '.' + fileformat
    if os.path.isfile(path):
        if path.lower().endswith(suffix):
            yield path
        return
    if not os.path.isdir(path):
        return
    if recursive:
        for root, dirs, files in os.walk(path):
            for fn in files:
                if fn.lower().endswith(suffix):
                    yield os.path.join(root, fn)
    else:
        for fn in os.listdir(path):
            full = os.path.join(path, fn)
            if os.path.isfile(full) and fn.lower().endswith(suffix):
                yield full

def main():
    parser = argparse.ArgumentParser(description="Print creation date for .mov/.3gp files in a folder")
    parser.add_argument('path', nargs='?', default='.', help='File or directory to process (default: current dir)')
    parser.add_argument('-n', '--no-recursive', action='store_true', help='Do not recurse into subdirectories')
    parser.add_argument('--no-sort', action='store_true', help='Do not sort output alphabetically')
    args = parser.parse_args()

    root = args.path
    filesmov = list(find_media_files(root, fileformat='mov',recursive=not args.no_recursive))
    files3gp = list(find_media_files(root, fileformat='3gp', recursive=not args.no_recursive))
    files = filesmov + files3gp
    if not files:
        print('No .mov/.3gp files found.', file=sys.stderr)
        sys.exit(2)

    # Sort files: case-insensitive on Windows, case-sensitive elsewhere
    if not args.no_sort:
        if os.name == 'nt':
            files.sort(key=lambda s: s.lower())
        else:
            files.sort()

    for f in files:
        info = None
        try:
            info = get_creation_time(f)
        except Exception as e:
            print(f"{f}\tERROR reading media info: {e}")
            continue
        if info:
            print(f"{f}\t{info}")
        else:
            # fallback to filesystem ctime
            fs = get_filesystem_ctime(f)
            if fs:
                print(f"{f}\tfilesystem_ctime: {fs}")
            else:
                print(f"{f}\tNo creation date found")

if __name__ == "__main__":
    main()