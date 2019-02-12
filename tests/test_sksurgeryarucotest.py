# coding=utf-8

"""sksurgeryarucotest tests"""

from sksurgeryutils.ui.sksurgerycharucotest_demo import CharucoDemoGui
import pytest

def test_sksurgeryarucotest(qtbot):
    """ Basic test to run the widget and make sure everything loads OK."""

    camera = 0
    x = 640
    y = 480
    rows = 10
    columns = 13
    dictionary = 2

    widget = CharucoDemoGui(camera, x, y, rows, columns, dictionary)
    widget.show()

    qtbot.addWidget(widget)
