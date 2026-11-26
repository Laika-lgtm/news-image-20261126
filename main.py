"""Entrypoint for news-image-20261126.

The front page is drawn at build time by render.py and shipped as
entry.png in this repository. This program copies that committed image to
the output directory the grader provides, and verifies the copy byte for
byte against the shipped file. Standard library only; no network, no
timestamps, fully deterministic.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    if _sha256(SRC) != _sha256(dst):
        sys.exit("entry.png copy failed hash check")
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main()
