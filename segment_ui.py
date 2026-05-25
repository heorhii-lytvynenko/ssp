import tkinter as tk

from audio_utils import build_audio_info_text
from constants import (
    SEGMENT_BUTTON_RESET_TEXT,
    SEGMENT_BUTTON_SAVE_TEXT,
    SEGMENT_CHECKBOX_SEPARATE_CHANNELS,
    SEGMENT_LABEL_END_MS,
    SEGMENT_LABEL_QUALITY,
    SEGMENT_LABEL_START_MS,
    SEGMENT_WINDOW_TITLE,
)


class SegmentSelectorUI:
    def __init__(self, root, file_path, total_ms, quality_options, default_quality):
        self.root = root
        self.file_path = file_path
        self.total_ms = total_ms
        self.quality_options = quality_options
        self.default_quality = default_quality

        self.window = None
        self.start_entry = None
        self.end_entry = None
        self.separate_var = None
        self.quality_var = None
        self.view_var = None
        self.save_btn = None
        self.plot_frame = None

    def build(self, on_reset, on_save, on_close):
        self.window = tk.Toplevel()
        self.window.title(SEGMENT_WINDOW_TITLE)
        self.window.geometry("1200x800")

        top_frame = tk.Frame(self.window)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        row_1 = tk.Frame(top_frame)
        row_1.pack(side=tk.TOP, fill=tk.X)
        row_2 = tk.Frame(top_frame)
        row_2.pack(side=tk.TOP, fill=tk.X, pady=(4, 0))

        info_group = tk.LabelFrame(row_1, text="Audio Info")
        info_group.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.Y)
        self._pack_label(info_group, build_audio_info_text(self.file_path, self.total_ms), padx=5)

        segment_group = tk.LabelFrame(row_1, text="Segment")
        segment_group.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.Y)
        self.start_entry = self._create_labeled_entry(segment_group, SEGMENT_LABEL_START_MS, "0")
        self.end_entry = self._create_labeled_entry(segment_group, SEGMENT_LABEL_END_MS, str(int(self.total_ms)))

        self.separate_var = tk.BooleanVar(value=False)
        display_group = tk.LabelFrame(row_2, text="Display")
        display_group.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.Y)
        tk.Checkbutton(display_group, text=SEGMENT_CHECKBOX_SEPARATE_CHANNELS, variable=self.separate_var).pack(side=tk.LEFT, padx=5)

        self.quality_var = tk.StringVar(value=self.default_quality)
        self._pack_label(display_group, SEGMENT_LABEL_QUALITY, padx=(10, 0))
        tk.OptionMenu(display_group, self.quality_var, *self.quality_options.keys()).pack(side=tk.LEFT)

        self.view_var = tk.StringVar(value="Plot")
        self._pack_label(display_group, "View:", padx=(10, 0))
        tk.OptionMenu(
            display_group,
            self.view_var,
            "Plot",
            "Time Domain",
            "Frequency Domain",
            "Enhancement",
            "Modeling",
        ).pack(side=tk.LEFT)

        actions_group = tk.LabelFrame(row_2, text="Actions")
        actions_group.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.Y)
        self._pack_button(actions_group, SEGMENT_BUTTON_RESET_TEXT, on_reset, padx=5)
        self.save_btn = tk.Button(actions_group, text=SEGMENT_BUTTON_SAVE_TEXT, state=tk.DISABLED, command=on_save)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.plot_frame = tk.Frame(self.window)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        self.window.protocol("WM_DELETE_WINDOW", on_close)
        self.root.protocol("WM_DELETE_WINDOW", on_close)

    @staticmethod
    def _pack_label(parent, text, padx=0):
        tk.Label(parent, text=text).pack(side=tk.LEFT, padx=padx)

    @staticmethod
    def _pack_button(parent, text, command, padx=0):
        tk.Button(parent, text=text, command=command).pack(side=tk.LEFT, padx=padx)

    def _create_labeled_entry(self, parent, label_text, value, width=8):
        self._pack_label(parent, label_text)
        entry = tk.Entry(parent, width=width)
        entry.pack(side=tk.LEFT)
        entry.insert(0, value)
        return entry

    def bind_plot_triggers(self, callback):
        self.separate_var.trace_add("write", lambda *args: callback())
        self.quality_var.trace_add("write", lambda *args: callback())
        self.view_var.trace_add("write", lambda *args: callback())
        self.start_entry.bind("<KeyRelease>", lambda event: callback())
        self.end_entry.bind("<KeyRelease>", lambda event: callback())
