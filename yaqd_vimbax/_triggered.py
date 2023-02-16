__all__ = ["Triggered"]

import asyncio
import numpy as np
import time    

from typing import Dict, Any, List, Optional
from yaqd_core import HasMeasureTrigger


class Triggered(HasMeasureTrigger):
    _kind = "vimbax-triggered"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._channel_names = ["mean", "stdev"]
        self._channel_shapes = {k: (608, 808) for k in self._channel_names}
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
        x1 = np.zeros(self._channel_shapes["mean"], dtype="uint")
        x2 = x1.copy()
        N = self._state["nframes"]
        time1 = time.time()
        for frame in self.cam.get_frame_generator(limit=N, timeout_ms=3000):
            arr = frame.as_numpy_ndarray()[:, :, 0].astype("uint16")
            x1 += arr
            x2 += arr**2
        time4 = time.time()
        self.logger.info(f"loop {time4-time1:0.2f}")
        if N < 2:
            x2.fill(np.nan)
            stdev = x2
        else:
            stdev = x2 - x1**2 / N
            stdev /= N - 1
            stdev **= 0.5
        return {"mean": x1 / N, "stdev": stdev}

    def set_exposure_time(self, time: float):
        self.cam.get_feature_by_name("ExposureTime").set(time * 1e3)

    def get_exposure_time(self) -> float:
        return self.cam.get_feature_by_name("ExposureTime").get() / 1e3

    def get_exposure_units(self):
        return "ms"

    def set_nframes(self, nframes: int):
        self._state["nframes"] = nframes

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
