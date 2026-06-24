import os
from enum import StrEnum


class FeatureFlag(StrEnum):
    ENABLE_VOICE_CLI = "STARK_ENABLE_VOICE_CLI"
    ENABLE_MULTILANG_MATRIX = "STARK_ENABLE_MULTILANG_MATRIX"


_DEFAULTS: dict[FeatureFlag, str] = {
    FeatureFlag.ENABLE_VOICE_CLI: "0",
    FeatureFlag.ENABLE_MULTILANG_MATRIX: "1",
}


def get_flag(flag: FeatureFlag) -> bool:
    return os.getenv(flag.value, _DEFAULTS.get(flag, "0")) == "1"
