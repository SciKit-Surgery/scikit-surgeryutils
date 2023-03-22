# -*- coding: utf-8 -*-
import os
import platform

import cv2
import pytest

import sksurgeryutils.common_overlay_apps as coa
from PySide6.QtWidgets import QApplication

## Shared skipif maker for all modules
skip_pytest_in_linux_and_none_ci = pytest.mark.skipif(
    platform.system() == 'Linux' and os.environ.get('CI') == None,
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'because of issues with VTK pipelines and pyside workflows with Class Inheritance'
)

## Shared skipif maker for all modules
skip_pytest_in_linux = pytest.mark.skipif(
    platform.system() == 'Linux',
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'because of issues with VTK pipelines and pyside workflows with Class Inheritance'
)


@skip_pytest_in_linux
def test_OverlayOnVideoFeedCropRecord_from_file(tmpdir):
    """

    NOTES:
        * Not really a unit test as it does not assert anything.
        But at least it might throw an error if something else changes.

        * For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """

    # Check if already an instance of QApplication is present or not
    if not QApplication.instance():
        _pyside_qt_app = QApplication([])
    else:
        _pyside_qt_app = QApplication.instance()

    input_file = 'tests/data/100x50_100_frames.avi'
    out_file = os.path.join(tmpdir, 'overlay_test.avi')
    overlay_app = coa.OverlayOnVideoFeedCropRecord(input_file, out_file)

    # Start app and get a frame from input, so that
    # the window is showing something, before we start
    # recording.
    overlay_app.start()
    overlay_app.show()
    overlay_app.update_view()

    overlay_app.on_record_start()

    for i in range(50):
        overlay_app.update_view()

    overlay_app.on_record_stop()
    overlay_app.stop()
    # Check that 50 frames were actually written to the output file
    output_video = cv2.VideoCapture(out_file)

    for i in range(50):
        ret, _ = output_video.read()
    assert ret

    # Trying to read 51st frame should return False
    ret, _ = output_video.read()
    assert not ret

    output_video.release()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    # overlay_app.stop()
    # overlay_app.terminate()


@skip_pytest_in_linux_and_none_ci
def test_OverlayOnVideoFeedCropRecord_from_webcam():
    """
    Test will only run if there is a camera available.

    NOTES:
        * Not really a unit test as it does not assert anything.
        But at least it might throw an error if something else changes.

        * For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """

    # Check if already an instance of QApplication is present or not
    if not QApplication.instance():
        _pyside_qt_app = QApplication([])
    else:
        _pyside_qt_app = QApplication.instance()

    # Try to open a camera. If one isn't available, the rest of test
    # will be skipped.
    source = 0
    cam = cv2.VideoCapture(source)
    if not cam.isOpened():
        pytest.skip("No camera available")

    cam.release()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()

    # Don't pass an output filename as a parameter, so that
    # the code to generate a filename from current date/time is executed.
    overlay_app = coa.OverlayOnVideoFeedCropRecord(0)

    # Start app and get a frame from input, so that
    # the window is showing something, before we start
    # recording.
    overlay_app.start()
    overlay_app.update_view()
    overlay_app.on_record_start()

    for i in range(50):
        overlay_app.update_view()

    overlay_app.on_record_stop()
    overlay_app.stop()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()


@skip_pytest_in_linux_and_none_ci
def test_OverlayBaseWidgetRaisesNotImplementedError():
    """

    NOTES:
        * Not really a unit test as it does not assert anything.
        But at least it might throw an error if something else changes.

        * For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    # Check if already an instance of QApplication is present or not
    if not QApplication.instance():
        _pyside_qt_app = QApplication([])
    else:
        _pyside_qt_app = QApplication.instance()

    class ErrorApp(coa.OverlayBaseWidget):

        def something(self):
            pass

    with pytest.raises(NotImplementedError):
        input_file = 'tests/data/100x50_100_frames.avi'

        overlay_app = ErrorApp(input_file)
        overlay_app.update_view()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()


@skip_pytest_in_linux_and_none_ci
def test_OverlayOnVideoFeedCropRecord_set_roi():
    """

    NOTES:
        * Not really a unit test as it does not assert anything.
        But at least it might throw an error if something else changes.

        * For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """

    # Check if already an instance of QApplication is present or not
    if not QApplication.instance():
        _pyside_qt_app = QApplication([])
    else:
        _pyside_qt_app = QApplication.instance()

    input_file = 'tests/data/100x50_100_frames.avi'
    overlay_app = coa.OverlayOnVideoFeedCropRecord(input_file)
    overlay_app.update_view()  # Get a frame so that we can crop it
    with pytest.raises(RuntimeError):
        overlay_app.set_roi()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()