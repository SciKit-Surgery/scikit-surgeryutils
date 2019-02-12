# coding=utf-8

"""sksurgeryvideolag tests"""

from sksurgeryutils.ui.sksurgeryvideolag_demo import DemoGui
import pytest

def test_sksurgeryvideolag(qtbot):
    """ Basic test to run the widget and make sure everything loads OK."""
    camera = 0
    x = 640
    y = 480
    grab = 33
    milliseconds = 15
    
    gui = DemoGui(camera, x, y, grab, milliseconds)
    gui.show()
    qtbot.addWidget(gui)

