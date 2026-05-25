import numpy as np

from quality_logic import downsample_time_and_segment


class PlotViewLogic:
    @staticmethod
    def build(segment, start_sample, end_sample, samplerate, quality, max_points, separate_channels):
        del start_sample, end_sample
        # Lab requirement: selected segment time axis starts at 0 ms.
        time = np.arange(len(segment), dtype=float) / samplerate * 1000.0
        plot_time, plot_data = downsample_time_and_segment(
            time,
            segment,
            quality=quality,
            max_points=max_points,
        )
        return {
            "mode": "plot",
            "plot_time": plot_time,
            "plot_data": plot_data,
            "segment": segment,
            "separate_channels": separate_channels,
        }
