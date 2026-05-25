QUALITY_OPTIONS = {"Low": 1000, "Medium": 4000, "High": 12000}
QUALITY_DEFAULT_SHORT_AUDIO = "High"
QUALITY_DEFAULT_LONG_AUDIO = "Low"

SEGMENT_WINDOW_TITLE = "Select Start/End (ms) and Plot Segment"

LAUNCHER_WINDOW_TITLE = "Audio Tools"
LAUNCHER_LABEL_TEXT = "Choose a function to open:"
LAUNCHER_BUTTON_GRAPHIC_TEXT = "Graphic representation"
LAUNCHER_BUTTON_TIME_DOMAIN_TEXT = "Analysis in the Time Domain"
LAUNCHER_BUTTON_EXIT_TEXT = "Exit"

FILE_DIALOG_TITLE_SELECT = "Select File"
FILE_DIALOG_TITLE_SAVE = "Save Segment As"
FILE_TYPE_WAV_LABEL = "WAV files"
FILE_TYPE_AUDIO_LABEL = "Audio files"

SEGMENT_LABEL_START_MS = "Start (ms):"
SEGMENT_LABEL_END_MS = "End (ms):"
SEGMENT_LABEL_QUALITY = "Quality:"
SEGMENT_CHECKBOX_SEPARATE_CHANNELS = "Separate channels"
SEGMENT_BUTTON_RESET_TEXT = "Reset"
SEGMENT_BUTTON_SAVE_TEXT = "Save Segment"

MSGBOX_TITLE_INFO = "Info"
MSGBOX_TITLE_SUCCESS = "Success"
MSGBOX_TITLE_ERROR = "Error"
MSGBOX_INFO_FULL_AUDIO = "Segment is the full audio. Nothing to save."
MSGBOX_SUCCESS_SAVED_PREFIX = "Segment saved to:\n"
MSGBOX_ERROR_SAVE_PREFIX = "Failed to save segment:\n"

PLOT_TITLE_SEGMENT_TEMPLATE = "Audio Segment: {start_ms} ms - {end_ms} ms"
PLOT_XLABEL_TIME_MS = "Time (ms)"
PLOT_YLABEL_AMPLITUDE = "Amplitude"
PLOT_CHANNEL_LEFT_LABEL = "Left"
PLOT_CHANNEL_RIGHT_LABEL = "Right"
PLOT_CHANNEL_LEFT_TITLE = "Left Channel"
PLOT_CHANNEL_RIGHT_TITLE = "Right Channel"
PLOT_MIN_FIG_SIZE_INCH = 2

AUDIO_INFO_UNKNOWN_BIT_DEPTH = "unknown"
AUDIO_INFO_TEMPLATE = (
    "Duration: {duration_ms} ms | "
    "Sampling rate: {samplerate} Hz | "
    "Channels: {channels} | "
    "Quantization: {bit_depth} bits"
)

SEGMENT_BOUNDS_MIN_MS = 0
SEGMENT_BOUNDS_MIN_RANGE_MS = 1

FRAMES_DEFAULT_MS = 15
FRAMES_ERROR_ZERO_LEN = "frame_ms is too small; computed frame length is 0 samples."

TIME_DOMAIN_WINDOW_TITLE = "Time Domain Analysis"
TIME_DOMAIN_WINDOW_SIZE = "1200x800"
TIME_DOMAIN_WAVEFORM_TITLE = "Waveform With Frame Boundaries"
TIME_DOMAIN_ENERGY_TITLE = "Frame Energy"
TIME_DOMAIN_ENERGY_XLABEL = "Frame Index"
TIME_DOMAIN_ENERGY_YLABEL = "Energy"
