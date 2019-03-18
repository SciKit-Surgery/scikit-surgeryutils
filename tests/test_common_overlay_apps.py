# -*- coding: utf-8 -*-
import cv2
import pytest
import sksurgeryutils.common_overlay_apps as coa

def test_OverlayOnVideoFeed(setup_qt):
    """
    Test will only run if there is a camera avilable.
    """

    # Try to open a camera. If one isn't available, the rest of test
    # will be skipped.
    camera_source = 0
    x = cv2.VideoCapture(camera_source)
    if x.isOpened():
        x.release()

        overlay_app = coa.OverlayOnVideoFeed(camera_source)
        overlay_app.start()
        overlay_app.update()
        overlay_app.stop()

    else:
        pytest.skip("No camera available, skipping.")


def test_OverlayBaseAppRaisesNotImplementedError(setup_qt):
    """
    Test will only run if there is a camera avilable
    """
    class ErrorApp(coa.OverlayBaseApp):

        def something(self):
            pass

    with pytest.raises(NotImplementedError):
        overlay_app = ErrorApp(0)
        overlay_app.update()

