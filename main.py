import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def get_audio_length(data, samplerate):
    """Return audio length in milliseconds."""
    return len(data) / samplerate * 1000

def downsample_for_plot(time, segment, quality="Medium", max_points=4000):
    if quality == "High":
        # Plot all points, no downsampling
        return time, segment
    if len(time) <= max_points:
        return time, segment
    idx = np.linspace(0, len(time) - 1, max_points, dtype=int)
    if len(segment.shape) == 1:
        return time[idx], segment[idx]
    else:
        return time[idx], segment[idx, :]

def open_segment_selector_and_plot(data, samplerate, root, file_path):
    total_ms = get_audio_length(data, samplerate)

    window = tk.Toplevel()
    window.title("Select Start/End (ms) and Plot Segment")
    window.geometry("1200x800")  # Initial size

    # Spinner overlay
    spinner_overlay = [None]

    def show_spinner():
        if spinner_overlay[0] is not None:
            return
        overlay = tk.Toplevel(window)
        overlay.transient(window)
        overlay.grab_set()
        overlay.geometry(f"{window.winfo_width()}x{window.winfo_height()}+{window.winfo_rootx()}+{window.winfo_rooty()}")
        overlay.overrideredirect(True)
        overlay.configure(bg='gray90')
        label = tk.Label(overlay, text="Loading...", font=("Arial", 20), bg='gray90')
        label.pack(expand=True)
        pb = ttk.Progressbar(overlay, mode='indeterminate')
        pb.pack(pady=10)
        pb.start()
        spinner_overlay[0] = overlay
        overlay.update()
        window.update_idletasks()  # Force update so spinner appears

    def hide_spinner():
        if spinner_overlay[0] is not None:
            spinner_overlay[0].destroy()
            spinner_overlay[0] = None

    # Top frame for controls
    top_frame = tk.Frame(window)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    # Audio info
    info = sf.info(file_path)
    bit_depth = info.subtype.split("_")[-1] if "_" in info.subtype else info.subtype
    if not bit_depth.isdigit():
        bit_depth = "unknown"
    info_text = (
        f"Duration: {int(total_ms)} ms | "
        f"Sampling rate: {info.samplerate} Hz | "
        f"Channels: {info.channels} | "
        f"Quantization: {bit_depth} bits"
    )
    tk.Label(top_frame, text=info_text).pack(side=tk.LEFT, padx=5)

    tk.Label(top_frame, text=f"Duration: {int(total_ms)} ms").pack(side=tk.LEFT, padx=5)

    tk.Label(top_frame, text="Start (ms):").pack(side=tk.LEFT)
    start_entry = tk.Entry(top_frame, width=8)
    start_entry.pack(side=tk.LEFT)
    start_entry.insert(0, "0")

    tk.Label(top_frame, text="End (ms):").pack(side=tk.LEFT)
    end_entry = tk.Entry(top_frame, width=8)
    end_entry.pack(side=tk.LEFT)
    end_entry.insert(0, str(int(total_ms)))

    separate_var = tk.BooleanVar(value=False)
    separate_check = tk.Checkbutton(top_frame, text="Separate channels", variable=separate_var)
    separate_check.pack(side=tk.LEFT, padx=5)

    # Quality selection
    default_quality = "High" if len(data) <= 50000 else "Low"
    quality_var = tk.StringVar(value=default_quality)
    quality_options = {"Low": 1000, "Medium": 4000, "High": 12000}
    tk.Label(top_frame, text="Quality:").pack(side=tk.LEFT, padx=(10,0))
    quality_menu = tk.OptionMenu(top_frame, quality_var, *quality_options.keys())
    quality_menu.pack(side=tk.LEFT)

    def reset_fields():
        start_entry.delete(0, tk.END)
        start_entry.insert(0, "0")
        end_entry.delete(0, tk.END)
        end_entry.insert(0, str(int(total_ms)))
        plot_segment()

    reset_btn = tk.Button(top_frame, text="Reset", command=reset_fields)
    reset_btn.pack(side=tk.LEFT, padx=5)

    # Save Segment button (initially disabled)
    save_btn = tk.Button(top_frame, text="Save Segment", state=tk.DISABLED)
    save_btn.pack(side=tk.LEFT, padx=5)

    # Frame for plot and toolbar
    plot_frame = tk.Frame(window)
    plot_frame.pack(fill=tk.BOTH, expand=True)

    # Matplotlib Figure
    fig, ax = plt.subplots(figsize=(8, 3))
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, plot_frame)
    toolbar.update()
    toolbar.pack(fill=tk.X)

    def get_current_segment():
        try:
            s_ms = float(start_entry.get())
        except ValueError:
            s_ms = 0
        try:
            e_ms = float(end_entry.get())
        except ValueError:
            e_ms = total_ms
        if e_ms > total_ms:
            e_ms = total_ms
        if s_ms < 0:
            s_ms = 0
        if e_ms < s_ms:
            e_ms = s_ms + 1

        start_sample = int(s_ms * samplerate / 1000)
        end_sample = int(e_ms * samplerate / 1000)
        return s_ms, e_ms, start_sample, end_sample

    def plot_segment():
        show_spinner()
        window.after(50, _plot_segment)  # Let spinner show before plotting

    def _plot_segment():
        s_ms, e_ms, start_sample, end_sample = get_current_segment()
        segment = data[start_sample:end_sample]
        time = np.arange(start_sample, end_sample) / samplerate * 1000

        quality = quality_var.get()
        max_points = quality_options[quality]
        plot_time, plot_data = downsample_for_plot(time, segment, quality=quality, max_points=max_points)

        fig.clf()
        if len(segment.shape) == 1:
            ax1 = fig.add_subplot(1, 1, 1)
            ax1.plot(plot_time, plot_data)
            ax1.set_title(f"Audio Segment: {s_ms} ms - {e_ms} ms")
            ax1.set_xlabel("Time (ms)")
            ax1.set_ylabel("Amplitude")
            ax1.grid(True)
        elif len(segment.shape) == 2:
            if separate_var.get():
                ax1 = fig.add_subplot(2, 1, 1)
                ax2 = fig.add_subplot(2, 1, 2)
                ax1.plot(plot_time, plot_data[:, 0], label="Left")
                ax1.set_title("Left Channel")
                ax1.set_xlabel("Time (ms)")
                ax1.set_ylabel("Amplitude")
                ax1.grid(True)
                ax2.plot(plot_time, plot_data[:, 1], label="Right", color="orange")
                ax2.set_title("Right Channel")
                ax2.set_xlabel("Time (ms)")
                ax2.set_ylabel("Amplitude")
                ax2.grid(True)
                fig.suptitle(f"Audio Segment: {s_ms} ms - {e_ms} ms")
                fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            else:
                ax1 = fig.add_subplot(1, 1, 1)
                ax1.plot(plot_time, plot_data[:, 0], label="Left")
                ax1.plot(plot_time, plot_data[:, 1], label="Right")
                ax1.set_title(f"Audio Segment: {s_ms} ms - {e_ms} ms")
                ax1.set_xlabel("Time (ms)")
                ax1.set_ylabel("Amplitude")
                ax1.legend()
                ax1.grid(True)
        canvas.draw()

        # Enable save button only if segment is not the full audio
        if start_sample > 0 or end_sample < len(data):
            save_btn.config(state=tk.NORMAL)
        else:
            save_btn.config(state=tk.DISABLED)
        hide_spinner()

    def save_segment():
        s_ms, e_ms, start_sample, end_sample = get_current_segment()
        if start_sample == 0 and end_sample == len(data):
            messagebox.showinfo("Info", "Segment is the full audio. Nothing to save.")
            return
        segment = data[start_sample:end_sample]
        save_path = filedialog.asksaveasfilename(
            title="Save Segment As",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        if save_path:
            try:
                sf.write(save_path, segment, samplerate)
                messagebox.showinfo("Success", f"Segment saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save segment:\n{e}")

    save_btn.config(command=save_segment)

    # Update plot when checkbox, quality, or entries are changed
    separate_var.trace_add("write", lambda *args: plot_segment())
    quality_var.trace_add("write", lambda *args: plot_segment())
    start_entry.bind("<KeyRelease>", lambda event: plot_segment())
    end_entry.bind("<KeyRelease>", lambda event: plot_segment())

    # Make plot resizable with window (debounced)
    resize_after_id = [None]
    last_size = [None, None]

    def do_resize():
        width = plot_frame.winfo_width()
        height = plot_frame.winfo_height()
        if (width, height) != tuple(last_size):
            dpi = fig.get_dpi()
            fig.set_size_inches(max(width / dpi, 2), max(height / dpi, 2))
            canvas.draw()
            last_size[0] = width
            last_size[1] = height

    def on_resize(event):
        if resize_after_id[0] is not None:
            window.after_cancel(resize_after_id[0])
        resize_after_id[0] = window.after(400, do_resize)

    plot_frame.bind("<Configure>", on_resize)

    plot_segment()

    def on_root_close():
        try:
            hide_spinner()
        except Exception:
            pass
        try:
            window.destroy()
        except Exception:
            pass
        try:
            root.quit()
            root.destroy()
        except Exception:
            pass

    window.protocol("WM_DELETE_WINDOW", on_root_close)
    root.protocol("WM_DELETE_WINDOW", on_root_close)

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select File", filetypes=(("Audio files", "*.wav"),)
    )
    if file_path:
        data, samplerate = sf.read(file_path)
        open_segment_selector_and_plot(data, samplerate, root, file_path)
        root.mainloop()
    else:
        print("No file selected.")

if __name__ == "__main__":
    main()