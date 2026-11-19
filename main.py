#!/usr/bin/env python3
"""Copy the committed entry.png to the output directory.

The poster for 18 November 2026's world news is shipped as entry.png in
this repository. This program's only job is to place a byte-identical copy
at $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Standard library only: no third-party imports, so it runs on a bare
python:3.13 image. Before copying it validates that the file is a whole
PNG within the competition's limits (at most 1 MiB, at most 1024x1024
pixels, correct PNG signature and IHDR dimensions); anything else fails
with a clear message and a non-zero exit code. The copy is deterministic:
two runs write the same bytes.
"""

import os
import shutil
import struct
import sys

MAX_BYTES = 1048576
MAX_DIMENSION = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    """Print an error to stderr and exit non-zero."""
    print("error: " + message, file=sys.stderr)
    return 1


def validate_png(path):
    """Check path is a whole PNG within the size limits.

    Returns (width, height) on success, or raises ValueError with a
    clear reason on failure.
    """
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError(
            "entry.png is %d bytes, over the %d-byte limit" % (size, MAX_BYTES)
        )
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        raise ValueError("entry.png does not start with the PNG signature")
    # The first chunk must be IHDR: 4-byte length, 4-byte type, then
    # width and height as big-endian 32-bit integers.
    length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or length != 13:
        raise ValueError("entry.png has no valid IHDR chunk")
    width, height = struct.unpack(">II", header[16:24])
    if width == 0 or height == 0:
        raise ValueError("entry.png has a zero width or height")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            "entry.png is %dx%d, over the %dx%d limit"
            % (width, height, MAX_DIMENSION, MAX_DIMENSION)
        )
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        return fail("entry.png not found next to main.py")
    try:
        width, height = validate_png(source)
    except (OSError, ValueError) as exc:
        return fail(str(exc))

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(output_dir, exist_ok=True)
        destination = os.path.join(output_dir, "entry.png")
        shutil.copyfile(source, destination)
    except OSError as exc:
        return fail("could not write output: %s" % exc)

    print(
        "wrote %s (%dx%d, %d bytes)"
        % (destination, width, height, os.path.getsize(destination))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
