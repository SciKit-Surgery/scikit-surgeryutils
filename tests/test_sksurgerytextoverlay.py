# coding=utf-8

"""sksurgerytextoverlay tests"""

from sksurgeryutils.ui.sksurgerytextoverlay_demo import TextOverlayDemo
import pytest
import sys

def test_sksurgerytextoverlay():
    """ Basic test to run the widget and make sure everything loads OK."""

    if sys.platform == "darwin":
        pytest.skip("Test not working on Mac runner")
        
    # Use input video rather than camera to test
    input_file = 'tests/data/test_video.avi'

    gui = TextOverlayDemo(input_file)
    gui.start()
