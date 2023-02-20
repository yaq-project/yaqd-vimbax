import time
import pathlib
import numpy as np
import toml  # type: ignore
import yaqc  # type: ignore

import matplotlib.pyplot as plt  # type: ignore
import matplotlib.animation as animation  # type: ignore
import matplotlib.gridspec as gridspec  # type: ignore

from mpl_toolkits.axes_grid1 import make_axes_locatable  # type: ignore
from matplotlib.colors import Normalize  # type: ignore
from matplotlib.widgets import Slider  # type: ignore

here = pathlib.Path(__file__).resolve().parent
plt.style.use("dark_background")
config = toml.load(here / "triggered_gui.toml")

cam = yaqc.Client(config["yaq"]["cam_port"])
cam.set_nframes(config["yaq"].pop("nframes", 3))
cam.measure(False)

while cam.busy():
    time.sleep(0.1)

meas0 = cam.get_measured()["mean"]

fig = plt.figure("Vimba X")
gs = gridspec.GridSpec(2, 1, height_ratios=[10, 1])

ax = plt.subplot(gs[0], aspect=408 / 608)
im = plt.imshow(meas0, vmax=255, vmin=0)
ax.grid()

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(im, cax=cax)
cbar.set_ticks(np.linspace(meas0.min(), meas0.max(), 6))
for axes in [ax.axes, cax.axes]:
    axes.tick_params(labelsize=16)


def update_im(y):
    im.set(data=y)
    im.set_norm(Normalize(y.min(), y.max()))
    cbar_ticks = np.linspace(y.min(), y.max(), num=6, endpoint=True)
    cbar.set_ticks(cbar_ticks)
    cbar.draw_all()
    plt.draw()


def data_gen():
    index = 0
    start = time.time()
    while True:
        m_id = cam.get_measurement_id()
        if index < m_id:
            measured = cam.get_measured()
            index = measured["measurement_id"]
            t_measure = time.time()
            ax.set_title(f"{index}")
            start = time.time()
            cam.measure(False)
            yield measured["mean"]
        else:
            time.sleep(0.1)


ax = plt.subplot(gs[1])
slider = Slider(ax, "exposure time (ms)", 0.1, 5e3, valinit=cam.get_exposure_time())
slider.on_changed(cam.set_exposure_time)

# run animation
ani = animation.FuncAnimation(fig, update_im, data_gen, interval=100)
plt.show()
