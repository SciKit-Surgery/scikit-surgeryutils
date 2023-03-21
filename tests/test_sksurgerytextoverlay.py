# coding=utf-8

"""sksurgerytextoverlay tests"""

import os
import platform

import pytest
from PySide6.QtWidgets import QApplication

from sksurgeryutils.ui.sksurgerytextoverlay_demo import TextOverlayDemo

## Shared skipif maker for all modules
skip_pytest_in_linux_and_none_ci = pytest.mark.skipif(
    platform.system() == 'Linux' and os.environ.get('CI') == None,
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'because of issues with VTK pipelines and pyside workflows with Class Inheritance'
)


@skip_pytest_in_linux_and_none_ci
def test_sksurgerytextoverlay():
    """
    Basic test to run the widget and make sure everything loads OK.

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

    # _pyside_qt_app = setup_pyside_qt_app

    # Use input video rather than camera to test
    input_file = 'tests/data/test_video.avi'

    gui_widget = TextOverlayDemo(input_file)
    gui_widget.start()
    gui_widget.show()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    gui_widget.stop()
    gui_widget.terminate()
