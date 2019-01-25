# coding=utf-8

"""
Various image utilities that might be useful in this package.
"""

import numpy as np
from PySide2 import QtGui


def image_to_pixmap(rgb_image):
    """
    Converts an OpenCV image to a Qt pixmap.

    :param rgb_image: OpenCV image, 3 channel, RGB.
    :return: QPixmap
    """
    if not isinstance(rgb_image, np.ndarray):
        raise TypeError('Input should be a numpy nd.array')
    if rgb_image.shape[2] != 3:
        raise ValueError('Input should be 3 channel RGB')

    # If you see a memory leak.
    # See: https://bugreports.qt.io/browse/PYSIDE-140
    # Should be fixed properly in PySide 5.11.3.
    # As of this commit, we should be on 5.12.0.
    # You could double check your environment.
    q_image = QtGui.QImage(rgb_image.data,
                           rgb_image.shape[1],
                           rgb_image.shape[0],
                           rgb_image.shape[1] * 3,
                           QtGui.QImage.Format_RGB888)

    pix = QtGui.QPixmap(q_image)
    return pix
