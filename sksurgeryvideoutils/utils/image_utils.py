# coding=utf-8

import sys
import numpy as np
import ctypes
from PySide2 import QtCore, QtWidgets, QtGui


def image_to_pixmap(image):
    """
    Converts an OpenCV image to a Qt pixmap.

    :param image: OpenCV image, 3 channel, RGB.
    :return: QPixmap
    """
    if not isinstance(image, np.ndarray):
        raise TypeError('Input should be a numpy nd.array')
    if image.shape[2] != 3:
        raise ValueError('Input should be 3 channel RGB')

    # Workaround for memory leak.
    # See: https://bugreports.qt.io/browse/PYSIDE-140
    # Should be fixed properly in PySide 5.11.3
    # Once we upgrade to 5.11.3, take out the hack on
    # the ch and rcount variables, and just create qimage
    # and then instantiate pixmap from qimage.
    pointer_to_buffer = ctypes.c_char.from_buffer(image, 0)
    rcount = ctypes.c_long.from_address(id(pointer_to_buffer)).value
    qimage = QtGui.QImage(pointer_to_buffer,
                          image.shape[1],
                          image.shape[0],
                          QtGui.QImage.Format_RGB888)
    if sys.version[0] == '3':
        ctypes.c_long.from_address(id(pointer_to_buffer)).value = rcount
    pixmap = QtGui.QPixmap.fromImage(qimage)
    return pixmap
