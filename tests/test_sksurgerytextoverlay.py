# coding=utf-8

"""sksurgerytextoverlay tests"""

import os
import platform

import pytest

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
    """ Basic test to run the widget and make sure everything loads OK."""

    # Use input video rather than camera to test
    input_file = 'tests/data/test_video.avi'

    gui = TextOverlayDemo(input_file)
    gui.start()
