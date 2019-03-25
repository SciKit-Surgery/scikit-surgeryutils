# -*- coding: utf-8 -*-
import cv2
import pytest
import numpy as np
import sksurgeryutils.common_overlay_apps as coa

def test_OverlayOnVideoFeed_from_file(setup_qt):

    # Try to open a camera. If one isn't available, the rest of test
    # will be skipped.
    input_file = 'tests/data/100x50_100_frames.avi'

    out_file = 'tests/output/overlay_test.avi'
    overlay_app = coa.OverlayOnVideoFeed(input_file, out_file)

    # Start app and get a frame from input, so that
    # the window is showing something, before we start
    # recording.
    overlay_app.start()
    overlay_app.update()
    overlay_app.on_record_start()

    for i in range(50):
        overlay_app.update()

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

def test_OverlayOnVideoFeed_from_webcam(setup_qt):
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
    
    out_file = 'tests/output/overlay_on_webcam_test.avi'
    overlay_app = coa.OverlayOnVideoFeed(0, out_file)

    # Start app and get a frame from input, so that
    # the window is showing something, before we start
    # recording.
    overlay_app.start()
    overlay_app.update()
    overlay_app.on_record_start()

    for i in range(50):
        overlay_app.update()

    overlay_app.on_record_stop()
    overlay_app.stop()

def test_OverlayBaseAppRaisesNotImplementedError(setup_qt):

    class ErrorApp(coa.OverlayBaseApp):

        def something(self):
            pass

    with pytest.raises(NotImplementedError):
        input_file = 'tests/data/100x50_100_frames.avi'

        overlay_app = ErrorApp(input_file)
        overlay_app.update()

