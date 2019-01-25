# coding=utf-8

import pytest
import numpy as np
import sksurgeryutils.utils.image_utils as iu


def test_image_to_pixel_invalid_because_input_is_none():
    with pytest.raises(TypeError):
        iu.image_to_pixmap(None)


def test_image_to_pixel_invalid_because_input_is_not_numpy():
    with pytest.raises(TypeError):
        iu.image_to_pixmap(1)


def test_image_to_pixel_invalid_because_input_is_greyscale():
    with pytest.raises(ValueError):
        iu.image_to_pixmap(np.zeros((100, 50, 1), dtype=np.uint8))


def test_image_to_pixel_valid_rgb_example(setup_qt):
    app = setup_qt
    blank_image = np.zeros((50, 100, 3), dtype=np.uint8)
    pixmap = iu.image_to_pixmap(blank_image)
    assert pixmap.width() == blank_image.shape[1]
    assert pixmap.height() == blank_image.shape[0]
