import soundfile as sf

from constants import (
    AUDIO_INFO_TEMPLATE,
    AUDIO_INFO_UNKNOWN_BIT_DEPTH,
    SEGMENT_BOUNDS_MIN_MS,
    SEGMENT_BOUNDS_MIN_RANGE_MS,
)


def get_audio_length(data, samplerate):
    """Return audio length in milliseconds."""
    return len(data) / samplerate * 1000


def build_audio_info_text(file_path, total_ms):
    info = sf.info(file_path)
    bit_depth = info.subtype.split("_")[-1] if "_" in info.subtype else info.subtype
    if not bit_depth.isdigit():
        bit_depth = AUDIO_INFO_UNKNOWN_BIT_DEPTH

    return AUDIO_INFO_TEMPLATE.format(
        duration_ms=int(total_ms),
        samplerate=info.samplerate,
        channels=info.channels,
        bit_depth=bit_depth,
    )


def parse_segment_bounds(start_text, end_text, total_ms, samplerate):
    """
    Convert start/end text values into validated ms/sample segment bounds.

    Returns:
        tuple: (start_ms, end_ms, start_sample, end_sample)
    """
    try:
        s_ms = float(start_text)
    except ValueError:
        s_ms = SEGMENT_BOUNDS_MIN_MS

    try:
        e_ms = float(end_text)
    except ValueError:
        e_ms = total_ms

    if e_ms > total_ms:
        e_ms = total_ms
    if s_ms < SEGMENT_BOUNDS_MIN_MS:
        s_ms = SEGMENT_BOUNDS_MIN_MS
    if e_ms < s_ms:
        e_ms = s_ms + SEGMENT_BOUNDS_MIN_RANGE_MS
    if e_ms > total_ms:
        e_ms = total_ms
    if s_ms > total_ms:
        s_ms = total_ms

    start_sample = int(s_ms * samplerate / 1000)
    end_sample = int(e_ms * samplerate / 1000)
    end_sample = min(end_sample, int(round(total_ms * samplerate / 1000)))
    if end_sample < start_sample:
        end_sample = start_sample
    return s_ms, e_ms, start_sample, end_sample
