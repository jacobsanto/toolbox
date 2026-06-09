"""Voice I/O — wrappers γύρω από ΠΡΑΓΜΑΤΙΚΑ CLIs (όχι mocks).

STT: whisper (local, καταλαβαίνει Ελληνικά) — `pip install openai-whisper`
TTS: edge-tts (δωρεάν ελληνικές φωνές Microsoft) — `pip install edge-tts`

Αν λείπουν, καθαρό ελληνικό μήνυμα με οδηγία εγκατάστασης.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

DEFAULT_VOICE = "el-GR-NestorasNeural"  # ή el-GR-AthinaNeural (γυναικεία)


class VoiceError(RuntimeError):
    pass


def _require(binary: str, install_hint: str) -> None:
    if shutil.which(binary) is None:
        raise VoiceError(
            f"Το CLI '{binary}' δεν είναι εγκατεστημένο. Εγκατάσταση: {install_hint}"
        )


def speak(text: str, out_path: Path, voice: str = DEFAULT_VOICE) -> Path:
    """Παράγει αρχείο ήχου (mp3) από κείμενο με ελληνική φωνή."""
    _require("edge-tts", "uv tool install edge-tts")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(out_path)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise VoiceError(f"Αποτυχία TTS: {proc.stderr.strip()[:300]}")
    return out_path


def transcribe(audio_path: Path, language: str = "Greek") -> str:
    """Μετατρέπει ηχητικό αρχείο σε κείμενο (τοπικά, μέσω whisper CLI)."""
    _require("whisper", "uv tool install openai-whisper")
    if not audio_path.exists():
        raise VoiceError(f"Δεν βρέθηκε το αρχείο: {audio_path}")
    proc = subprocess.run(
        ["whisper", str(audio_path), "--language", language, "--task", "transcribe",
         "--output_format", "txt", "--output_dir", str(audio_path.parent)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise VoiceError(f"Αποτυχία STT: {proc.stderr.strip()[:300]}")
    txt_path = audio_path.with_suffix(".txt")
    if not txt_path.exists():
        raise VoiceError("Το whisper δεν παρήγαγε κείμενο")
    return txt_path.read_text(encoding="utf-8").strip()
