# coding=utf-8

"""sksurgeryvideolag tests"""

from sksurgeryutils.ui.sksurgeryvideolag_demo import DemoGui
import pytest
import sys

def test_sksurgeryvideolag(qtbot):
    """ Basic test to run the widget and make sure everything loads OK."""

    # Use input video rather than camera to test
    input_file = 'tests/data/test_video.avi'
    x = 640
    y = 480
    grab = 33
    milliseconds = 15
    
    gui = DemoGui(input_file, x, y, grab, milliseconds)
    gui.show()
    qtbot.addWidget(gui)

