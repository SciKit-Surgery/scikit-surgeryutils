# coding=utf-8

""" Small utilities to do with opening an OpenCV video camera. """

import os
import cv2


def validate_camera_source(source):
    """
    Checks the source parameters is not None, is either
    an int or a string, and if it's a string, then it should be a filename,
    or if it's an int, it should be non-negative.

    :raises: RuntimeError on all errors.
    """
    if source is None:
        raise RuntimeError("OpenCV source is None. "
                           "Should be a device number or filename.")

    if not isinstance(source, str) and not isinstance(source, int):
        raise RuntimeError("OpenCV source is neither str nor int.")

    result = source

    if isinstance(source, str):

        if source.isdigit():
            source_as_int = int(source)
            if source_as_int < 0:
                raise RuntimeError("OpenCV source is an int, but negative.")

            result = source_as_int
        else:
            if not os.path.isfile(source):
                raise RuntimeError("OpenCV source is a string, but not a file.")

    return result


def open_video_source(source, window_size=None):
    """
    Function to open the source, and if provided, set window size.

    :param source: OpenCV video source specifier (file, or int).
    :param window_size: 2-tuple, (width, height)
    :return cv2.VideoCapture that is open (ready).
    :raises RuntimeError: if the source fails to open.
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera "
                           "from source:" + str(source))

    if window_size is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, window_size[1])
        print("Video feed set to ("
              + str(window_size[0]) + " x " + str(window_size[1]) + ")")
    else:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("Video feed defaults to ("
              + str(width) + " x " + str(height) + ")")

    return cap
