#!/usr/bin/env python3
"""Transfer one selected local song using a receipt from Recoup's private upload tool.

Read the receipt from stdin or a permission-restricted JSON file. No Recoup API
key is needed. Output contains finalize arguments, never the signed capability.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import ssl
import stat
import sys
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

MAX_BYTES = 50 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    """Never forward audio bytes or signed capabilities to a redirect target."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def send_upload(request):
    # macOS Python may not have its optional certifi setup installed.
    bundle = "/etc/ssl/cert.pem"
    context = ssl.create_default_context(cafile=bundle if Path(bundle).is_file() else None)
    opener = build_opener(NoRedirect(), HTTPSHandler(context=context))
    with opener.open(request, timeout=120) as response:
        if not 200 <= response.status < 300:
            raise ValueError("Upload was not accepted")


def upload_audio(path, receipt, send=send_upload):
    """Validate the selected file and signed destination, then transfer its bytes."""
    if not isinstance(receipt, dict):
        raise ValueError("Expected the private upload tool's JSON receipt")
    key = receipt.get("storage_key", "")
    if not isinstance(key, str) or not re.fullmatch(
        r"[A-Za-z0-9-]+/release-packs/uploads/[a-f0-9-]{36}\.(mp3|wav|flac)", key
    ):
        raise ValueError("Invalid private audio storage key")
    limit = receipt.get("maximum_bytes")
    if type(limit) is not int or not 0 < limit <= MAX_BYTES:
        raise ValueError("Invalid private upload size limit")
    raw_url = receipt.get("signed_upload_url")
    if not isinstance(raw_url, str):
        raise ValueError("Missing signed upload capability")
    url = urlsplit(raw_url)
    if (
        url.scheme != "https"
        or not (url.hostname or "").endswith(".supabase.co")
        or url.username or url.password or url.port not in (None, 443)
        or url.fragment
        or url.path != "/storage/v1/object/upload/sign/user-files/" + key
        or not parse_qs(url.query).get("token")
    ):
        raise ValueError("Expected a signed Recoup private-storage upload destination")
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Select one regular audio file, not a directory or symlink")
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as source:
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit:
                raise ValueError("Audio file is empty or exceeds the upload size limit")
            audio = source.read(limit + 1)
        if not 0 < len(audio) <= limit:
            raise ValueError("Audio file is empty or exceeds the upload size limit")
    except OSError:
        raise ValueError("Could not read the selected audio file") from None
    suffix = path.suffix.lower()
    if suffix != "." + key.rsplit(".", 1)[-1]:
        raise ValueError("Upload receipt format does not match the selected file")
    if suffix == ".mp3" and (audio.startswith(b"ID3") or (len(audio) >= 2 and audio[0] == 255 and audio[1] & 224 == 224)):
        content_type = "audio/mpeg"
    elif suffix == ".wav" and audio.startswith(b"RIFF") and audio[8:12] == b"WAVE":
        content_type = "audio/wav"
    elif suffix == ".flac" and audio.startswith(b"fLaC"):
        content_type = "audio/flac"
    else:
        raise ValueError("Expected MP3, WAV, or FLAC audio bytes")
    request = Request(raw_url, data=audio, method="PUT", headers={
        "Content-Type": content_type, "Content-Length": str(len(audio)),
    })
    try:
        send(request)
    except Exception:
        # Transport exceptions may contain the signed URL. Never print them.
        raise ValueError("Private upload failed; request a fresh upload receipt before retrying") from None
    return {
        "uploaded": True,
        "storage_key": key,
        "content_type": content_type,
        "bytes": len(audio),
        "sha256": hashlib.sha256(audio).hexdigest(),
        "filename": "audio" + suffix,
        "next_action": "Call upload_release_pack_asset with mode=finalize, storage_key and content_type. Then analyze its verified URL.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Exact local audio path selected by the user")
    parser.add_argument("--receipt", help="Private JSON file containing the signed-upload tool result; defaults to stdin")
    args = parser.parse_args()
    try:
        if args.receipt:
            receipt = json.loads(Path(args.receipt).read_text())
        else:
            receipt = json.load(sys.stdin)
        print(json.dumps(upload_audio(args.file, receipt)))
    except (ValueError, OSError):
        # JSON/URL parser errors can include input containing the capability.
        print("Audio transfer failed. Check the selected file and request a fresh private upload receipt; no analysis has run.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
