#!/usr/bin/env python3
"""news-image-20261126 round-2 entrypoint (grader style).

Copies the pre-rendered front page (entry.png) into the output directory
and verifies the copy byte-for-byte. Stdlib only, no network, deterministic.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def read_png_size(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"\x89PNG\r\n\x1a\n":
            raise ValueError("not a PNG file: %s" % path)
        (length,) = struct.unpack(">I", f.read(4))
        ctype = f.read(4)
        if ctype != b"IHDR" or length != 13:
            raise ValueError("missing IHDR in %s" % path)
        w, h = struct.unpack(">II", f.read(8))
    return w, h


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 2
    src = os.path.join(HERE, "entry.png")
    w, h = read_png_size(src)
    if (w, h) != (1024, 1024):
        print("entry.png must be 1024x1024, got %dx%d" % (w, h), file=sys.stderr)
        return 2
    size = os.path.getsize(src)
    if size > 1024 * 1024:
        print("entry.png over 1 MiB: %d bytes" % size, file=sys.stderr)
        return 2
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    digest = sha256_file(src)
    if digest != sha256_file(dst):
        print("copy verification failed", file=sys.stderr)
        return 2
    print("OK entry.png %dx%d %d bytes sha256=%s" % (w, h, size, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
