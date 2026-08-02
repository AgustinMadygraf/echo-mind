from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceNote:
    file_id: str
    file_bytes: bytes
    file_name: str = ""
    duration: int | None = None

    def __post_init__(self) -> None:
        if not self.file_bytes:
            raise ValueError("file_bytes no puede estar vacío")
