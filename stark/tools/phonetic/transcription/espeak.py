import ctypes
import os
import re
import sys
import threading
from typing import Generator, Optional, final
import ctypes.util


@final
class EspeakNG:
    espeakCHARS_AUTO = 0
    espeakSSML = 0x10
    espeakPHONEMES = 0x100
    espeakPHONEMES_IPA = 0x02
    AUDIO_OUTPUT_SYNCHRONOUS = 0x02
    EE_OK = 0

    def __init__(self, lib_path: Optional[str] = None, lang: str = "en-us"):
        self.voice = lang
        self.lib_espeak = self._load_espeak(lib_path)
        self._init_espeak()

    # Interface

    def set_lang(self, lang: str):
        if lang == self.voice:
            return  # early exit, lib_espeak.espeak_SetVoiceByName is a bit slow
        self.voice = lang
        res = self.lib_espeak.espeak_SetVoiceByName(self.voice.encode("utf-8"))
        if res != self.EE_OK:
            raise RuntimeError(f"Failed to set voice to '{self.voice}'")

    def text_to_ipa(
        self,
        text: str,
        phoneme_separator: Optional[str] = None,
        remove_stress: bool = False,
    ) -> str:
        """Return IPA phoneme string for the given text using espeak_TextToPhonemes."""
        phoneme_flags = self.espeakPHONEMES_IPA
        if phoneme_separator:
            phoneme_flags |= ord(phoneme_separator) << 8

        text_bytes = text.encode("utf-8")
        text_pointer = ctypes.c_char_p(text_bytes)
        text_flags = self.espeakCHARS_AUTO

        fcn_ttp = self.lib_espeak.espeak_TextToPhonemes
        fcn_ttp.restype = ctypes.c_char_p

        ipa_lines: list[str] = []
        while text_pointer:
            ipa_bytes = fcn_ttp(ctypes.pointer(text_pointer), text_flags, phoneme_flags)
            if isinstance(ipa_bytes, bytes):
                ipa_lines.append(ipa_bytes.decode("utf-8").strip())

        ipa_full = " ".join(ipa_lines)
        ipa_full = " ".join(ipa_full.splitlines())
        if remove_stress:
            ipa_full = re.sub(r"[ˈˌ]", "", ipa_full)
        return ipa_full

    # Private

    def _init_espeak(self):
        """Initialize and set voice."""
        sample_rate = self.lib_espeak.espeak_Initialize(
            self.AUDIO_OUTPUT_SYNCHRONOUS, 0, None, 0
        )
        if sample_rate <= 0:
            raise RuntimeError("Failed to initialize eSpeak NG")

        res = self.lib_espeak.espeak_SetVoiceByName(self.voice.encode("utf-8"))
        if res != self.EE_OK:
            raise RuntimeError(f"Failed to set voice: {self.voice}")

    def _load_espeak(self, lib_path: str | None) -> ctypes.CDLL:
        for path in ([lib_path] if lib_path else []) + list(self._find_library_path()):
            try:
                return ctypes.cdll.LoadLibrary(path)
            except OSError:
                pass
        raise FileNotFoundError(
            "libespeak-ng not found. Install eSpeak NG or set lib_path manually."
        )

    def _find_library_path(self) -> Generator[str, None, None]:
        if lib := ctypes.util.find_library("espeak-ng"):
            yield lib

        # Fallbacks
        yield "libespeak-ng.so.1"
        yield "libespeak-ng.so"

        candidates: list[str] = []
        if sys.platform.startswith("linux"):
            candidates = [
                "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1",  # Debian/Ubuntu x86_64
                "/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1",  # ARM Ubuntu / GH Actions
                "/usr/lib/libespeak-ng.so.1",  # fallback for other distros
                "/usr/lib64/libespeak-ng.so.1",  # RHEL/CentOS/Fedora
                "/usr/local/lib/libespeak-ng.so.1",  # manual compile installs
            ]
        elif sys.platform == "darwin":
            candidates = [
                "/opt/homebrew/lib/libespeak-ng.dylib",
                "/usr/local/lib/libespeak-ng.dylib",
            ]
        elif sys.platform.startswith("win"):
            candidates = [
                r"C:\Program Files\eSpeak NG\libespeak-ng.dll",
                r"C:\Program Files (x86)\eSpeak NG\libespeak-ng.dll",
            ]

        for path in candidates:
            if os.path.exists(path):
                yield path


"""
Underlying eSpeak NG library is global so there is no sense in multiple instances of EspeakNG. Using singleton approach instead.
"""
# lazy initialization to avoid raising an exception on import
espeak: EspeakNG | None = None
_espeak_lock = threading.Lock()


class EspeakIpaProvider:
    def __init__(self, check_chars: bool = True):
        self.check_chars = check_chars

    def to_ipa(self, string: str, language_code: str) -> str:
        with _espeak_lock:
            global espeak
            if espeak is None:
                espeak = EspeakNG(language_code)
            espeak.set_lang(language_code)
            ipa = espeak.text_to_ipa(string, remove_stress=True)
            if self.check_chars:
                for char in {"(", ")", "[", "]"}:
                    assert char not in ipa, (
                        f"Unexpected character '{char}' in IPA '{ipa}' with lang '{language_code}'. Check if the language is supported by eSpeak NG. You can disable this check by setting check_chars=False."
                    )
            return ipa
