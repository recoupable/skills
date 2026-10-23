import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from upload_chat_audio import upload_audio

KEY = "owner/release-packs/uploads/12345678-1234-1234-1234-123456789abc.mp3"
URL = "https://example.supabase.co/storage/v1/object/upload/sign/user-files/" + KEY + "?token=secret"


class UploadChatAudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.audio = Path(self.temp.name) / "song.mp3"
        self.audio.write_bytes(b"ID3" + bytes(100))
        self.receipt = {"storage_key": KEY, "signed_upload_url": URL, "maximum_bytes": 50 * 1024 * 1024}

    def test_transfers_exact_file_and_returns_only_safe_finalize_fields(self):
        seen = []
        def send(request):
            seen.append(request)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = upload_audio(self.audio, self.receipt, send=send)
        self.assertEqual(seen[0].method, "PUT")
        self.assertEqual(seen[0].data, self.audio.read_bytes())
        self.assertEqual(seen[0].get_header("Content-type"), "audio/mpeg")
        self.assertEqual(result["storage_key"], KEY)
        self.assertEqual(result["bytes"], self.audio.stat().st_size)
        self.assertNotIn("secret", json.dumps(result) + output.getvalue())
        self.assertNotIn("Authorization", seen[0].headers)

    def test_refuses_arbitrary_upload_destinations(self):
        for url in ["http://example.supabase.co/", "https://attacker.example/", URL.replace(KEY, "other/file.mp3"), URL.replace("user-files", "public-uploads"), URL.replace("example.supabase.co", "example.supabase.co.attacker.test")]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                upload_audio(self.audio, {**self.receipt, "signed_upload_url": url}, send=lambda _: self.fail("must not send"))

    def test_rejects_oversized_audio_before_network(self):
        with self.assertRaises(ValueError):
            upload_audio(self.audio, {**self.receipt, "maximum_bytes": 10}, send=lambda _: self.fail("must not send"))

    def test_rejects_non_audio_even_if_named_mp3(self):
        self.audio.write_bytes(b"<html>not audio</html>")
        with self.assertRaises(ValueError):
            upload_audio(self.audio, self.receipt, send=lambda _: self.fail("must not send"))

    def test_rejects_directory_and_symlink_sources(self):
        link = self.audio.with_name("alias.mp3")
        link.symlink_to(self.audio)
        for path in (self.audio.parent, link):
            with self.subTest(path=path), self.assertRaises(ValueError):
                upload_audio(path, self.receipt, send=lambda _: self.fail("must not send"))

    def test_rejects_invalid_receipts(self):
        for receipt in ({}, {**self.receipt, "maximum_bytes": -1}, {**self.receipt, "storage_key": "../private.mp3"}):
            with self.subTest(receipt=receipt), self.assertRaises(ValueError):
                upload_audio(self.audio, receipt, send=lambda _: self.fail("must not send"))

    def test_sanitizes_transport_failure(self):
        def send(_):
            raise RuntimeError("failed " + URL)
        with self.assertRaisesRegex(ValueError, "Private upload failed") as error:
            upload_audio(self.audio, self.receipt, send=send)
        self.assertNotIn("secret", str(error.exception))

    def test_wav_and_flac_signatures(self):
        for suffix, audio, mime in [("wav", b"RIFF" + bytes(4) + b"WAVE" + bytes(32), "audio/wav"), ("flac", b"fLaC" + bytes(32), "audio/flac")]:
            with self.subTest(suffix=suffix):
                path = self.audio.with_suffix("." + suffix)
                path.write_bytes(audio)
                receipt = {**self.receipt, "storage_key": KEY[:-3] + suffix, "signed_upload_url": URL.replace(".mp3?", "." + suffix + "?")}
                result = upload_audio(path, receipt, send=lambda _: None)
                self.assertEqual(result["content_type"], mime)

    def test_does_not_follow_redirects(self):
        from upload_chat_audio import NoRedirect
        self.assertIsNone(NoRedirect().redirect_request(None, None, 307, "redirect", {}, "https://attacker.example"))


if __name__ == "__main__":
    unittest.main()
