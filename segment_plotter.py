import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from constants import (
    PLOT_CHANNEL_LEFT_LABEL,
    PLOT_CHANNEL_LEFT_TITLE,
    PLOT_CHANNEL_RIGHT_LABEL,
    PLOT_CHANNEL_RIGHT_TITLE,
    PLOT_MIN_FIG_SIZE_INCH,
    PLOT_TITLE_SEGMENT_TEMPLATE,
    PLOT_XLABEL_TIME_MS,
    PLOT_YLABEL_AMPLITUDE,
)


class SegmentPlotter:
    def __init__(self, master):
        self.fig, _ = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, master)
        self.toolbar.update()
        self.toolbar.pack(fill="x")

    def draw(self, result, start_ms, end_ms):
        if result["mode"] == "plot":
            self._draw_plot(result, start_ms, end_ms)
        elif result["mode"] == "time_domain":
            self._draw_time_domain(result)
        elif result["mode"] == "frequency_domain":
            self._draw_frequency_domain(result)
        elif result["mode"] == "enhancement":
            self._draw_enhancement(result)
        elif result["mode"] == "modeling":
            self._draw_modeling(result)

    def _draw_plot(self, result, start_ms, end_ms):
        plot_time = result["plot_time"]
        plot_data = result["plot_data"]
        segment = result["segment"]
        separate_channels = result["separate_channels"]
        self.fig.clf()

        if len(segment.shape) == 1:
            ax1 = self.fig.add_subplot(1, 1, 1)
            ax1.plot(plot_time, plot_data)
            ax1.set_title(PLOT_TITLE_SEGMENT_TEMPLATE.format(start_ms=start_ms, end_ms=end_ms))
            ax1.set_xlabel(PLOT_XLABEL_TIME_MS)
            ax1.set_ylabel(PLOT_YLABEL_AMPLITUDE)
            ax1.grid(True)
        elif len(segment.shape) == 2:
            if separate_channels:
                ax1 = self.fig.add_subplot(2, 1, 1)
                ax2 = self.fig.add_subplot(2, 1, 2)
                ax1.plot(plot_time, plot_data[:, 0], label=PLOT_CHANNEL_LEFT_LABEL)
                ax1.set_title(PLOT_CHANNEL_LEFT_TITLE)
                ax1.set_xlabel(PLOT_XLABEL_TIME_MS)
                ax1.set_ylabel(PLOT_YLABEL_AMPLITUDE)
                ax1.grid(True)
                ax2.plot(plot_time, plot_data[:, 1], label=PLOT_CHANNEL_RIGHT_LABEL, color="orange")
                ax2.set_title(PLOT_CHANNEL_RIGHT_TITLE)
                ax2.set_xlabel(PLOT_XLABEL_TIME_MS)
                ax2.set_ylabel(PLOT_YLABEL_AMPLITUDE)
                ax2.grid(True)
                self.fig.suptitle(PLOT_TITLE_SEGMENT_TEMPLATE.format(start_ms=start_ms, end_ms=end_ms))
                self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            else:
                ax1 = self.fig.add_subplot(1, 1, 1)
                ax1.plot(plot_time, plot_data[:, 0], label=PLOT_CHANNEL_LEFT_LABEL)
                ax1.plot(plot_time, plot_data[:, 1], label=PLOT_CHANNEL_RIGHT_LABEL)
                ax1.set_title(PLOT_TITLE_SEGMENT_TEMPLATE.format(start_ms=start_ms, end_ms=end_ms))
                ax1.set_xlabel(PLOT_XLABEL_TIME_MS)
                ax1.set_ylabel(PLOT_YLABEL_AMPLITUDE)
                ax1.legend()
                ax1.grid(True)

        self.canvas.draw()

    def _draw_time_domain(self, result):
        signal = result["signal"]
        signal_time_ms = result["signal_time_ms"]
        frame_times_ms = result["frame_times_ms"]
        frame_energy = result["frame_energy"]
        frame_zcr = result["frame_zcr"]
        autocorr_lags_ms = result["autocorr_lags_ms"]
        autocorr_values = result["autocorr_values"]
        f0_hz = result["f0_hz"]
        f0_lag_ms = result["f0_lag_ms"]
        f0_peak = result["f0_peak"]
        self.fig.clf()
        ax_wave = self.fig.add_subplot(4, 1, 1)
        ax_energy = self.fig.add_subplot(4, 1, 2)
        ax_zcr = self.fig.add_subplot(4, 1, 3)
        ax_ac = self.fig.add_subplot(4, 1, 4)

        ax_wave.plot(signal_time_ms, signal, color="steelblue")
        ax_wave.set_title("Waveform (Time Domain)")
        ax_wave.set_xlabel("Time (ms)")
        ax_wave.set_ylabel("Amplitude")
        ax_wave.grid(True)

        ax_energy.plot(frame_times_ms, frame_energy, color="slategray")
        ax_energy.set_title("Frame Energy")
        ax_energy.set_xlabel("Time (ms)")
        ax_energy.set_ylabel("Energy")
        ax_energy.grid(True)

        ax_zcr.plot(frame_times_ms, frame_zcr, color="darkgreen")
        ax_zcr.set_title("Zero-Crossing Rate (ZCR)")
        ax_zcr.set_xlabel("Time (ms)")
        ax_zcr.set_ylabel("ZCR")
        ax_zcr.grid(True)

        ax_ac.plot(autocorr_lags_ms, autocorr_values, color="purple")
        if f0_hz is not None and f0_lag_ms is not None:
            ax_ac.scatter([f0_lag_ms], [f0_peak], color="crimson", s=18)
            ax_ac.set_title(f"Normalized Autocorrelation | Estimated F0: {f0_hz:.2f} Hz")
        else:
            ax_ac.set_title("Normalized Autocorrelation | Estimated F0: N/A")
        ax_ac.set_xlabel("Lag (ms)")
        ax_ac.set_ylabel("Rxx (norm)")
        ax_ac.grid(True)

        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_frequency_domain(self, result):
        if "error" in result:
            self._draw_message(result["error"])
            return

        self.fig.clf()
        ax_time = self.fig.add_subplot(4, 1, 1)
        ax_spec = self.fig.add_subplot(4, 1, 2)
        ax_cep = self.fig.add_subplot(4, 1, 3)
        ax_spg = self.fig.add_subplot(4, 1, 4)

        ax_time.plot(result["segment_time_ms"], result["segment_signal"], color="steelblue")
        ax_time.set_title("Segment Waveform")
        ax_time.set_xlabel("Time (ms)")
        ax_time.set_ylabel("Amplitude")
        ax_time.grid(True)

        ax_spec.plot(result["spectrum_freq_khz"], result["spectrum_db"], color="darkorange")
        ax_spec.set_title("Spectrum (kHz)")
        ax_spec.set_xlabel("Frequency (kHz)")
        ax_spec.set_ylabel("Magnitude (dB)")
        ax_spec.grid(True)

        ax_cep.plot(result["cepstrum_quef_ms"], result["cepstrum_values"], color="purple")
        title = f"Cepstrum | F0(cep): {result['f0_cep_hz']:.2f} Hz" if result["f0_cep_hz"] is not None else "Cepstrum | F0(cep): N/A"
        if result["f0_ac_hz"] is not None:
            title += f" | F0(ac): {result['f0_ac_hz']:.2f} Hz"
        if result["f0_cep_hz"] is not None and result["f0_cep_ms"] is not None:
            ax_cep.scatter([result["f0_cep_ms"]], [result["f0_cep_peak"]], color="crimson", s=20)
        ax_cep.set_title(title)
        ax_cep.set_xlabel("Quefrency (ms)")
        ax_cep.set_ylabel("Cepstrum")
        ax_cep.grid(True)

        sp_err = result.get("spectrogram_error")
        sp_t = result["spectrogram_time_ms"]
        sp_f = result["spectrogram_freq_khz"]
        sp_db = result["spectrogram_db"]
        if sp_err is not None or len(sp_t) == 0 or len(sp_f) == 0 or sp_db.size == 0:
            ax_spg.text(0.05, 0.5, f"Spectrogram unavailable:\n{sp_err or 'no data'}", fontsize=10)
            ax_spg.set_title("Spectrogram (Full Signal)")
            ax_spg.set_xlabel("Time (ms)")
            ax_spg.set_ylabel("Frequency (kHz)")
            ax_spg.grid(True)
        else:
            im = ax_spg.imshow(
                sp_db,
                aspect="auto",
                origin="lower",
                cmap="magma",
                extent=[
                    float(sp_t[0]),
                    float(sp_t[-1]),
                    float(sp_f[0]),
                    float(sp_f[-1]),
                ],
            )
            ax_spg.set_title("Spectrogram (Full Signal)")
            ax_spg.set_xlabel("Time (ms)")
            ax_spg.set_ylabel("Frequency (kHz)")
            self.fig.colorbar(im, ax=ax_spg, orientation="vertical", pad=0.01)

        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_enhancement(self, result):
        self.fig.clf()
        ax1 = self.fig.add_subplot(2, 1, 1)
        ax2 = self.fig.add_subplot(2, 1, 2)

        ax1.plot(result["time_ms"], result["noisy_signal"], color="gray")
        ax1.set_title(f"Noisy Signal | Frame: {result['frame_ms']:.0f} ms")
        ax1.set_xlabel("Time (ms)")
        ax1.set_ylabel("Amplitude")
        ax1.grid(True)

        ax2.plot(result["time_ms"], result["enhanced_signal"], color="teal")
        ax2.set_title(f"Enhanced Signal | SNR before: {result['snr_before_db']:.2f} dB | SNR after: {result['snr_after_db']:.2f} dB")
        ax2.set_xlabel("Time (ms)")
        ax2.set_ylabel("Amplitude")
        ax2.grid(True)

        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_modeling(self, result):
        if "error" in result:
            self._draw_message(result["error"])
            return
        self.fig.clf()

        ax1 = self.fig.add_subplot(3, 1, 1)
        ax2 = self.fig.add_subplot(3, 1, 2)
        ax3 = self.fig.add_subplot(3, 1, 3)

        t = result["time_ms"]
        ax1.plot(t, result["actual"], label="Actual", color="black", linewidth=1)
        ax1.plot(t, result["pred_linear"], label="Linear", color="royalblue", alpha=0.8)
        ax1.plot(t, result["pred_nonlinear"], label="Nonlinear", color="darkorange", alpha=0.8)
        ax1.set_title(
            f"Prediction | order={result['order']} hidden={result['hidden']} "
            f"| MSE lin={result['mse_linear']:.6f}, MSE nonlin={result['mse_nonlinear']:.6f}"
        )
        ax1.set_xlabel("Time (ms)")
        ax1.set_ylabel("Amplitude")
        ax1.legend()
        ax1.grid(True)

        ax2.plot(t, result["err_linear"], color="royalblue")
        ax2.set_title("Linear Prediction Error")
        ax2.set_xlabel("Time (ms)")
        ax2.set_ylabel("Error")
        ax2.grid(True)

        ax3.plot(t, result["err_nonlinear"], color="darkorange")
        ax3.set_title("Nonlinear Prediction Error")
        ax3.set_xlabel("Time (ms)")
        ax3.set_ylabel("Error")
        ax3.grid(True)

        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_message(self, text):
        self.fig.clf()
        ax = self.fig.add_subplot(1, 1, 1)
        ax.text(0.05, 0.5, text, fontsize=12)
        ax.axis("off")
        self.canvas.draw()

    def resize_to(self, width, height):
        dpi = self.fig.get_dpi()
        self.fig.set_size_inches(max(width / dpi, PLOT_MIN_FIG_SIZE_INCH), max(height / dpi, PLOT_MIN_FIG_SIZE_INCH))
        self.canvas.draw()
