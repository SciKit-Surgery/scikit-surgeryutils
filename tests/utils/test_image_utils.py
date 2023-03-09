# coding=utf-8
import os
import platform

import numpy as np
import pytest

import sksurgeryutils.utils.image_utils as iu

## Shared skipif maker for all modules
skip_pytest_in_linux_and_none_ci = pytest.mark.skipif(
    platform.system() == 'Linux' and os.environ.get('CI') == None,
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'because of issues with VTK pipelines and pyside workflows with Class Inheritance'
)


def test_image_to_pixel_invalid_because_input_is_none():
    with pytest.raises(TypeError):
        iu.image_to_pixmap(None)


def test_image_to_pixel_invalid_because_input_is_not_numpy():
    with pytest.raises(TypeError):
        iu.image_to_pixmap(1)


def test_image_to_pixel_invalid_because_input_is_greyscale():
    with pytest.raises(ValueError):
        iu.image_to_pixmap(np.zeros((100, 50, 1), dtype=np.uint8))


@skip_pytest_in_linux_and_none_ci
def test_image_to_pixel_valid_rgb_example():
    blank_image = np.zeros((50, 100, 3), dtype=np.uint8)
    pixmap = iu.image_to_pixmap(blank_image)
    assert pixmap.width() == blank_image.shape[1]
    assert pixmap.height() == blank_image.shape[0]
