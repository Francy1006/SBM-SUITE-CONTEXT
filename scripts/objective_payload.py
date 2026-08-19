#!/usr/bin/env python3

import argparse
import base64
import binascii
import gzip
from pathlib import Path

COMPACT_MARKER = b"SBM-GZIP-BASE64-V1\n"


class ObjectivePayloadError(ValueError):
    pass


def decode_payload_bytes(raw: bytes) -> bytes:
    if not raw.startswith(COMPACT_MARKER):
        return raw

    encoded = b"".join(raw[len(COMPACT_MARKER):].split())
    if not encoded:
        raise ObjectivePayloadError("compact objectives payload is empty")

    try:
        compressed = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ObjectivePayloadError("compact objectives payload is not valid base64") from exc

    try:
        return gzip.decompress(compressed)
    except (OSError, EOFError) as exc:
        raise ObjectivePayloadError("compact objectives payload failed gzip CRC/integrity validation") from exc


def decode_file(source: Path, target: Path) -> None:
    target.write_bytes(decode_payload_bytes(source.read_bytes()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("decode",))
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        decode_file(Path(args.input), Path(args.output))
    except (OSError, ObjectivePayloadError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
