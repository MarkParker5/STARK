import ctypes
import os
import sys
import re
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
        self._load_libs(lib_path)
        self._init_espeak()

    # Interface

    def set_lang(self, lang: str):
        if lang == self.voice:
            return  # early exit, lib_espeak.espeak_SetVoiceByName is a bit slow
        self.voice = lang
        res = self.lib_espeak.espeak_SetVoiceByName(self.voice.encode("utf-8"))
        if res != self.EE_OK:
            raise RuntimeError(f"Failed to set voice: {self.voice}")

    def text_to_ipa(
        self,
        text: str,
        phoneme_separator: Optional[str] = None,
        remove_stress: bool = False,
    ) -> str:
        """Return IPA phoneme string for the given text."""
        if sys.platform == "darwin":
            phonemes_file = self.libc.tmpfile()
            if not phonemes_file:
                raise RuntimeError("Failed to create temporary file")
            try:
                phoneme_flags = self.espeakPHONEMES_IPA
                if phoneme_separator:
                    phoneme_flags |= ord(phoneme_separator) << 8

                self.lib_espeak.espeak_SetPhonemeTrace(phoneme_flags, phonemes_file)

                text_bytes = text.encode("utf-8")
                synth_flags = self.espeakCHARS_AUTO | self.espeakPHONEMES

                res = self.lib_espeak.espeak_Synth(
                    text_bytes,
                    ctypes.c_size_t(0),
                    ctypes.c_uint(0),
                    ctypes.c_uint(0),
                    ctypes.c_uint(0),
                    ctypes.c_uint(synth_flags),
                    None,
                    None,
                )
                if res != self.EE_OK:
                    raise RuntimeError("espeak_Synth failed")

                self.lib_espeak.espeak_Synchronize()
                self.libc.fflush(phonemes_file)
                self.libc.rewind(phonemes_file)

                # Read file contents
                ipa_bytes = b""
                bufsize = 4096
                buf = ctypes.create_string_buffer(bufsize)
                fread = self.libc.fread
                fread.argtypes = [
                    ctypes.c_void_p,
                    ctypes.c_size_t,
                    ctypes.c_size_t,
                    ctypes.c_void_p,
                ]
                fread.restype = ctypes.c_size_t
                while True:
                    n = fread(buf, 1, bufsize, phonemes_file)
                    if n == 0:
                        break
                    ipa_bytes += buf.raw[:n]
                ipa = ipa_bytes.decode("utf-8")
            finally:
                self.libc.fclose(phonemes_file)
        else:
            phonemes_buffer = ctypes.c_char_p()
            phonemes_size = ctypes.c_size_t()
            phonemes_file = self.libc.open_memstream(
                ctypes.byref(phonemes_buffer), ctypes.byref(phonemes_size)
            )
            if not phonemes_file:
                raise RuntimeError("Failed to create memory stream")

            try:
                phoneme_flags = self.espeakPHONEMES_IPA
                if phoneme_separator:
                    phoneme_flags |= ord(phoneme_separator) << 8

                self.lib_espeak.espeak_SetPhonemeTrace(phoneme_flags, phonemes_file)

                text_bytes = text.encode("utf-8")
                synth_flags = self.espeakCHARS_AUTO | self.espeakPHONEMES

                res = self.lib_espeak.espeak_Synth(
                    text_bytes,
                    ctypes.c_size_t(0),
                    ctypes.c_uint(0),
                    ctypes.c_uint(0),
                    ctypes.c_uint(0),
                    ctypes.c_uint(synth_flags),
                    None,
                    None,
                )
                if res != self.EE_OK:
                    raise RuntimeError("espeak_Synth failed")

                self.lib_espeak.espeak_Synchronize()  # Wait for synthesis to finish
                self.libc.fflush(phonemes_file)

                ipa = ctypes.string_at(phonemes_buffer).decode("utf-8")
            finally:
                self.libc.fclose(phonemes_file)

        ipa = ipa.strip()
        if remove_stress:
            ipa = re.sub(r"[ˈˌ]", "", ipa)

        ipa = " ".join(ipa.splitlines())

        return ipa

    # Private

    def _init_espeak(self):
        """Initialize and set voice."""
        self.lib_espeak.espeak_Initialize.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        self.lib_espeak.espeak_Initialize.restype = ctypes.c_int

        sample_rate = self.lib_espeak.espeak_Initialize(
            self.AUDIO_OUTPUT_SYNCHRONOUS, 0, None, 0
        )
        if sample_rate <= 0:
            raise RuntimeError("Failed to initialize eSpeak NG")

        self.lib_espeak.espeak_SetVoiceByName.argtypes = [ctypes.c_char_p]
        self.lib_espeak.espeak_SetVoiceByName.restype = ctypes.c_int

        res = self.lib_espeak.espeak_SetVoiceByName(self.voice.encode("utf-8"))
        if res != self.EE_OK:
            raise RuntimeError(f"Failed to set voice: {self.voice}")

        # Define espeak_Synth signature
        self.lib_espeak.espeak_Synth.argtypes = [
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.lib_espeak.espeak_Synth.restype = ctypes.c_int

        # Synchronize to make sure synthesis finishes
        self.lib_espeak.espeak_Synchronize.argtypes = []
        self.lib_espeak.espeak_Synchronize.restype = None

        # Define SetPhonemeTrace
        self.lib_espeak.espeak_SetPhonemeTrace.argtypes = [
            ctypes.c_int,
            ctypes.c_void_p,
        ]
        self.lib_espeak.espeak_SetPhonemeTrace.restype = None

    def _load_libs(self, lib_path: str | None):
        self.lib_espeak = self._load_espeak(lib_path)

        # libc for open_memstream
        if sys.platform.startswith("linux"):
            self.libc = ctypes.cdll.LoadLibrary("libc.so.6")
            self.libc.open_memstream.argtypes = [
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_size_t),
            ]
            self.libc.open_memstream.restype = ctypes.c_void_p
        elif sys.platform == "darwin":
            self.libc = ctypes.cdll.LoadLibrary("libSystem.B.dylib")
            self.libc.tmpfile.restype = ctypes.c_void_p
            self.libc.fflush.argtypes = [ctypes.c_void_p]
            self.libc.fflush.restype = ctypes.c_int
            self.libc.fclose.argtypes = [ctypes.c_void_p]
            self.libc.fclose.restype = ctypes.c_int
            self.libc.rewind.argtypes = [ctypes.c_void_p]
            self.libc.rewind.restype = None
        else:
            raise RuntimeError("This example currently supports Linux/macOS")

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


def text_to_ipa(text: str, lang: str, remove_stress: bool = True) -> str:
    with _espeak_lock:
        global espeak
        if espeak is None:
            espeak = EspeakNG()
        espeak.set_lang(lang)
        return espeak.text_to_ipa(text, remove_stress=remove_stress)


if __name__ == "__main__":
    data = [
        ("en", "Hello, World"),
        ("uk", "Привіт світ"),
        ("fr", "Bonjour le monde"),
        ("ru", "Привет мир"),
        ("en", "Hello, World"),
        ("en", "Hello, World"),
        ("ru", "Привет мир"),
        ("ru", "Привет мир"),
        ("en", "Hello, World"),
        ("uk", "Привіт світ"),
        ("uk", "Привіт світ"),
        ("uk", "Привіт світ"),
        ("uk", "Привіт світ"),
        ("uk", "Привіт світ"),
    ]
    for lang, text in data:
        print(f"{lang.upper()}: {text_to_ipa(text, lang)}")
