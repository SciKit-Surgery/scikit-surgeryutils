# -*- coding: utf-8 -*-
import os
import platform
import sys

import cv2
import pytest

import sksurgeryutils.common_overlay_apps as coa

## Shared skipif maker for all modules
skip_pytest_in_linux_and_none_ci = pytest.mark.skipif(
    platform.system() == 'Linux' and os.environ.get('CI') == None,
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'because of issues with VTK pipelines and pyside workflows with Class Inheritance'
)


@skip_pytest_in_linux_and_none_ci
def test_OverlayOnVideoFeedCropRecord_from_file(setup_qt, tmpdir):

    input_file = 'tests/data/100x50_100_frames.avi'

    out_file = os.path.join(tmpdir, 'overlay_test.avi')

    overlay_app = coa.OverlayOnVideoFeedCropRecord(input_file, out_file)

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

    # Check that 50 frames were actually written to the output file
    output_video = cv2.VideoCapture(out_file)

    for i in range(50):
        ret, _ = output_video.read()
    assert ret

    # Trying to read 51st frame should return False
    ret, _ = output_video.read()
    assert not ret

    output_video.release()


@skip_pytest_in_linux_and_none_ci
def test_OverlayOnVideoFeedCropRecord_from_webcam(setup_qt):
    """
    Test will only run if there is a camera avilable.
    """

    # Try to open a camera. If one isn't available, the rest of test
    # will be skipped.
    source = 0
    cam = cv2.VideoCapture(source)
    if not cam.isOpened():
        pytest.skip("No camera available")

    cam.release()

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


@skip_pytest_in_linux_and_none_ci
def test_OverlayBaseWidgetRaisesNotImplementedError(setup_qt):
    class ErrorApp(coa.OverlayBaseWidget):

        def something(self):
            pass

    with pytest.raises(NotImplementedError):
        input_file = 'tests/data/100x50_100_frames.avi'

        overlay_app = ErrorApp(input_file)
        overlay_app.update_view()


@skip_pytest_in_linux_and_none_ci
def test_OverlayOnVideoFeedCropRecord_set_roi(setup_qt):
    input_file = 'tests/data/100x50_100_frames.avi'
    overlay_app = coa.OverlayOnVideoFeedCropRecord(input_file)
    overlay_app.update_view()  # Get a frame so that we can crop it
    with pytest.raises(RuntimeError):
        overlay_app.set_roi()
