__all__ = ["Triggered"]

import asyncio
import numpy as np
import time
import threading
import logging

from typing import Dict, Any, List, Optional, Tuple
from yaqd_core import HasMeasureTrigger


class Triggered(HasMeasureTrigger):
    _kind = "vimbax-triggered"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._channel_names = ["mean", "stdev"]
        self._channel_units = {k: None for k in self._channel_names}

    async def update_state(self):
        import vmbpy  # type: ignore

        with vmbpy.VmbSystem.get_instance() as vmb:
            if self._config["serial"]:
                camera_id = self._config["serial"]
            else:
                cams = vmb.get_all_cameras()
                camera_id = cams[0].get_id()
            self.logger.info(camera_id)
            with vmb.get_camera_by_id(camera_id) as cam:
                self.cam = cam
                self.make = self.cam.get_name()
                self.model = self.cam.get_model()
                self.serial = self.cam.get_serial()
                for feature in self.cam.get_all_features():
                    self.logger.debug(feature.get_name())
                while True:
                    await asyncio.sleep(1)

    async def _measure(self):
        N = self._state["nframes"]
        start = time.time()
        if N == 1:
            try:
                mean = self.cam.get_frame().as_numpy_ndarray()[:, :, 0]
                stdev = np.empty(mean.shape)
                stdev.fill(np.nan)
            except Exception as e:
                self.logger.error(str(e))
                raise e
        else:
            handler = self.Handler(N, self.get_channel_shapes()["mean"], "uint16")
            try:
                self.cam.start_streaming(handler=handler, buffer_count=10)
                await asyncio.wait_for(handler.ashutdown_event.wait(), 5)
            except Exception as e:
                self.logger.error(str(e))
                raise e
            finally:
                self.cam.stop_streaming()
            mean = (handler.x1 / N).astype(np.float32)
            stdev = handler.x2 - handler.x1**2 / N
            stdev /= N - 1
            stdev = (stdev**0.5).astype(np.float32)
        finish = time.time()
        self.logger.info(f"took {(finish-start):0.3f} sec")
        return {"mean": mean, "stdev": stdev}

    def set_exposure_time(self, time: float):
        self.cam.get_feature_by_name("ExposureTime").set(time)

    def get_exposure_time(self) -> float:
        return self.cam.get_feature_by_name("ExposureTime").get()

    def get_exposure_units(self) -> str:
        return "µs"

    def get_exposure_limits(self) -> Tuple[float, float]:
        return self.cam.get_feature_by_name("ExposureTime").get_range()

    def set_nframes(self, nframes: int):
        self._state["nframes"] = max(nframes, 1)

    def get_nframes(self) -> float:
        return self._state["nframes"]

    def get_temperature(self) -> float:
        return self.cam.get_feature_by_name("DeviceTemperature").get()

    def get_led_brightness(self) -> int:
        return self.cam.get_feature_by_name("DeviceIndicatorLuminance").get()

    def set_led_brightness(self, val: int):
        self.cam.get_feature_by_name("DeviceIndicatorLuminance").set(val)

    def get_gain(self) -> float:
        return self.cam.get_feature_by_name("Gain").get()

    def set_gain(self, gain: float):
        self.cam.get_feature_by_name("Gain").set(gain)

    class Handler:
        def __init__(self, nframes, shape, arrtype):
            self.ashutdown_event = asyncio.Event()
            self.frames_remaining = nframes
            self.x1 = np.zeros(shape, dtype="f8")
            self.x2 = self.x1.copy()
            self.arrtype = arrtype

        def __call__(self, cam, stream, frame):
            if not self.frames_remaining:
                self.ashutdown_event.set()
                return
            arr = frame.as_numpy_ndarray()[:, :, 0].astype(self.arrtype)
            self.x1 += arr
            self.x2 += arr**2
            self.frames_remaining -= 1
            cam.queue_frame(frame)

    def get_channel_shapes(self):
        height = self.cam.get_feature_by_name("Height").get()
        width = self.cam.get_feature_by_name("Width").get()
        return {k: (height, width) for k in self._channel_names}
