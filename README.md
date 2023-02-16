# yaqd-vimbax

[![PyPI](https://img.shields.io/pypi/v/yaqd-vimbax)](https://pypi.org/project/yaqd-vimbax)
[![Conda](https://img.shields.io/conda/vn/conda-forge/yaqd-vimbax)](https://anaconda.org/conda-forge/yaqd-vimbax)
[![yaq](https://img.shields.io/badge/framework-yaq-orange)](https://yaq.fyi/)
[![black](https://img.shields.io/badge/code--style-black-black)](https://black.readthedocs.io/)
[![ver](https://img.shields.io/badge/calver-YYYY.M.MICRO-blue)](https://calver.org/)
[![log](https://img.shields.io/badge/change-log-informational)](https://github.com/yaq-project/yaqd-vimbax/-/blob/main/CHANGELOG.md)

Daemons wrapping the [Vimba X SDK](https://www.alliedvision.com/en/products/software/vimba-x-sdk/). Vimba X is fully ([GenICam](https://www.baslerweb.com/en/vision-campus/interfaces-and-standards/genicam-standard/)) compliant.

This package contains the following daemon(s):

- https://yaq.fyi/daemons/vimbax-triggered


## Installation Notes
1. Download and install the [Vimba X SDK](https://www.alliedvision.com/en/products/software/vimba-x-sdk/) from the Allied Vision web page.
2. Install the `vmbpy` package (not to be confused with [VimbaPython](https://github.com/alliedvision/VimbaPython), which is an older API). At the time of this writing, vmbpy was not available on Github, conda, or pip (though documentation suggests Allied Vision intends to host it on Github).  The package wheel can be found in the Vimba X program directory. 
3. Install `yaqd-vimbax`.
