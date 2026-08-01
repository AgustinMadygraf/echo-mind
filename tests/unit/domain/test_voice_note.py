import unittest

from src.domain.entities.voice_note import VoiceNote


class VoiceNoteTest(unittest.TestCase):
    def test_rejects_empty_file_bytes(self) -> None:
        with self.assertRaises(ValueError):
            VoiceNote(file_id="f1", file_bytes=b"")

    def test_returns_expected_attributes(self) -> None:
        note = VoiceNote(
            file_id="f1",
            file_bytes=b"\x00\x01audio",
            file_name="f1.ogg",
            duration=5,
        )
        self.assertEqual(note.file_id, "f1")
        self.assertEqual(note.file_bytes, b"\x00\x01audio")
        self.assertEqual(note.file_name, "f1.ogg")
        self.assertEqual(note.duration, 5)

    def test_immutable(self) -> None:
        note = VoiceNote(file_id="f1", file_bytes=b"audio")
        with self.assertRaises(AttributeError):
            note.file_id = "changed"  # type: ignore[misc]

    def test_defaults(self) -> None:
        note = VoiceNote(file_id="f1", file_bytes=b"audio")
        self.assertEqual(note.file_name, "")
        self.assertIsNone(note.duration)


if __name__ == "__main__":
    unittest.main()
