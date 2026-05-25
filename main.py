import tkinter as tk
from tkinter import filedialog

import soundfile as sf

from constants import FILE_DIALOG_TITLE_SELECT, FILE_TYPE_AUDIO_LABEL
from segment_selector_app import GraphicRepresentation


def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title=FILE_DIALOG_TITLE_SELECT,
        filetypes=((FILE_TYPE_AUDIO_LABEL, "*.wav"),),
    )

    if file_path:
        data, samplerate = sf.read(file_path)
        GraphicRepresentation(data, samplerate, root, file_path)
        root.mainloop()
    else:
        root.destroy()


if __name__ == "__main__":
    main()
	