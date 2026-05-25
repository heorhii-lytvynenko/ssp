import tkinter as tk
from tkinter import filedialog, messagebox

import soundfile as sf

from audio_utils import get_audio_length, parse_segment_bounds
from enhancement_logic import EnhancementLogic
from frequency_domain_logic import FrequencyDomainLogic
from modeling_logic import ModelingLogic
from constants import (
    FILE_DIALOG_TITLE_SAVE,
    FILE_TYPE_WAV_LABEL,
    MSGBOX_ERROR_SAVE_PREFIX,
    MSGBOX_INFO_FULL_AUDIO,
    MSGBOX_SUCCESS_SAVED_PREFIX,
    MSGBOX_TITLE_ERROR,
    MSGBOX_TITLE_INFO,
    MSGBOX_TITLE_SUCCESS,
    QUALITY_DEFAULT_LONG_AUDIO,
    QUALITY_DEFAULT_SHORT_AUDIO,
    QUALITY_OPTIONS,
    SEGMENT_BOUNDS_MIN_MS,
)
from plot_view_logic import PlotViewLogic
from segment_plotter import SegmentPlotter
from segment_ui import SegmentSelectorUI
from time_domain_logic import TimeDomainLogic


class GraphicRepresentation:
    def __init__(self, data, samplerate, root, file_path):
        self.data = data
        self.samplerate = samplerate
        self.root = root
        self.file_path = file_path
        self.total_ms = get_audio_length(data, samplerate)
        self.quality_options = QUALITY_OPTIONS
        self.last_size = (None, None)
        self.ui = None
        self.plotter = None

        self._build_ui()
        self._bind_events()
        self.plot_segment()

    def _build_ui(self):
        default_quality = (
            QUALITY_DEFAULT_SHORT_AUDIO
            if len(self.data) <= 50000
            else QUALITY_DEFAULT_LONG_AUDIO
        )
        self.ui = SegmentSelectorUI(
            root=self.root,
            file_path=self.file_path,
            total_ms=self.total_ms,
            quality_options=self.quality_options,
            default_quality=default_quality,
        )
        self.ui.build(on_reset=self.reset_fields, on_save=self.save_segment, on_close=self.on_root_close)
        self.plotter = SegmentPlotter(self.ui.plot_frame)

    def _bind_events(self):
        self.ui.bind_plot_triggers(self.plot_segment)
        self.ui.plot_frame.bind("<Configure>", self.on_resize)

    def reset_fields(self):
        self.ui.start_entry.delete(0, tk.END)
        self.ui.start_entry.insert(0, "0")
        self.ui.end_entry.delete(0, tk.END)
        self.ui.end_entry.insert(0, str(int(self.total_ms)))
        self.plot_segment()

    def plot_segment(self):
        self._plot_segment()

    def _plot_segment(self):
        try:
            # Get the currently selected segment range from the UI.
            s_ms, e_ms, start_sample, end_sample = parse_segment_bounds(
                start_text=self.ui.start_entry.get(),
                end_text=self.ui.end_entry.get(),
                total_ms=self.total_ms,
                samplerate=self.samplerate,
            )
            segment = self.data[start_sample:end_sample]
            quality = self.ui.quality_var.get()
            max_points = self.quality_options[quality]

            logic_result = self._build_logic_result(
                selected_view=self.ui.view_var.get(),
                segment=segment,
                start_sample=start_sample,
                end_sample=end_sample,
                quality=quality,
                max_points=max_points,
            )

            self.plotter.draw(logic_result, start_ms=s_ms, end_ms=e_ms)

            if start_sample > 0 or end_sample < len(self.data):
                self.ui.save_btn.config(state=tk.NORMAL)
            else:
                self.ui.save_btn.config(state=tk.DISABLED)
        except Exception as exc:
            messagebox.showerror(MSGBOX_TITLE_ERROR, f"Plot failed:\n{exc}")

    def _build_logic_result(self, selected_view, segment, start_sample, end_sample, quality, max_points):
        if selected_view == "Time Domain":
            return TimeDomainLogic.build(
                segment=segment,
                samplerate=self.samplerate,
                quality=quality,
                max_points=max_points,
            )
        if selected_view == "Frequency Domain":
            return FrequencyDomainLogic.build(
                segment=segment,
                full_signal=self.data,
                samplerate=self.samplerate,
                quality=quality,
                max_points=max_points,
            )
        if selected_view == "Enhancement":
            return EnhancementLogic.build(
                full_signal=self.data,
                samplerate=self.samplerate,
                noise_start_sample=start_sample,
                noise_end_sample=end_sample,
            )
        if selected_view == "Modeling":
            return ModelingLogic.build(
                segment=segment,
                samplerate=self.samplerate,
            )
        if selected_view == "Plot":
            return PlotViewLogic.build(
                segment=segment,
                start_sample=start_sample,
                end_sample=end_sample,
                samplerate=self.samplerate,
                quality=quality,
                max_points=max_points,
                separate_channels=self.ui.separate_var.get(),
            )
        raise ValueError(f"Unknown view selected: {selected_view}")

    def save_segment(self):
        # Reuse the same helper to get exact segment boundaries for saving.
        _, _, start_sample, end_sample = parse_segment_bounds(
            start_text=self.ui.start_entry.get(),
            end_text=self.ui.end_entry.get(),
            total_ms=self.total_ms,
            samplerate=self.samplerate,
        )
        if start_sample == SEGMENT_BOUNDS_MIN_MS and end_sample == len(self.data):
            messagebox.showinfo(MSGBOX_TITLE_INFO, MSGBOX_INFO_FULL_AUDIO)
            return

        segment = self.data[start_sample:end_sample]
        save_path = filedialog.asksaveasfilename(
            title=FILE_DIALOG_TITLE_SAVE,
            defaultextension=".wav",
            filetypes=[(FILE_TYPE_WAV_LABEL, "*.wav")],
        )
        if save_path:
            try:
                sf.write(save_path, segment, self.samplerate)
                messagebox.showinfo(MSGBOX_TITLE_SUCCESS, f"{MSGBOX_SUCCESS_SAVED_PREFIX}{save_path}")
            except Exception as e:
                messagebox.showerror(MSGBOX_TITLE_ERROR, f"{MSGBOX_ERROR_SAVE_PREFIX}{e}")

    def do_resize(self):
        width = self.ui.plot_frame.winfo_width()
        height = self.ui.plot_frame.winfo_height()
        if (width, height) != self.last_size:
            self.plotter.resize_to(width, height)
            self.last_size = (width, height)

    def on_resize(self, _event):
        self.do_resize()

    def on_root_close(self):
        try:
            self.ui.window.destroy()
        except Exception:
            pass
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
