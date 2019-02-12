# coding=utf-8

"""sksurgeryarucotest tests"""

from sksurgeryutils.ui.sksurgerycharucotest_demo import CharucoDemoGui
import pytest

def test_sksurgeryarucotest(qtbot):
    """ Basic test to run the widget and make sure everything loads OK."""

    # Use input video rather than camera to test
    input_file = 'tests/data/test_video.avi'
    x = 640
    y = 480
    rows = 10
    columns = 13
    dictionary = 2

    widget = CharucoDemoGui(input_file, x, y, rows, columns, dictionary)
    widget.show()

    qtbot.addWidget(widget)
