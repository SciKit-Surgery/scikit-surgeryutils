# coding=utf-8

""" Demo app, to show text overlay"""

import logging
import sys

from PySide6.QtWidgets import QApplication, QInputDialog
from sksurgeryvtk.text import text_overlay

from sksurgeryutils import common_overlay_apps

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class TextOverlayDemo(common_overlay_apps.OverlayOnVideoFeed):
    """ Demo app, to show text overlay"""

    def __init__(self, video_source):
        super().__init__(video_source)

        self.vtk_overlay_window.GetRenderWindow().SetWindowName(
            "Click on image to add text")
        self.overlay_layer = 2

        # Add annotations to each corner
        corner_annotation = text_overlay.VTKCornerAnnotation()
        corner_annotation.set_text(["1", "2", "3", "4"])
        self.vtk_overlay_window.add_vtk_actor(corner_annotation.text_actor, 2)

        # Add large text in centre of screen
        # (need to stretch them vertically more)
        large_text = \
            text_overlay.VTKLargeTextCentreOfScreen("Click to add text")
        large_text.set_parent_window(self.vtk_overlay_window)
        self.vtk_overlay_window.add_vtk_actor(large_text.text_actor, 2)

        # Add text in response to left mouse click
        self.vtk_overlay_window.AddObserver('LeftButtonPressEvent',
                                            self.mouse_click_callback)

    def mouse_click_callback(self, obj, _ev):
        """ Callback to create text at left mouse click position. """

        # Open a dialog box to get the input text
        text, _ = QInputDialog.getText(None, "Create text overlay", "Text:")

        # Get the mouse click position
        x_position, y_position = obj.GetEventPosition()

        # Create a text actor and add it to the VTK scene
        vtk_text = text_overlay.VTKText(text, x_position, y_position)
        vtk_text.set_parent_window(self.vtk_overlay_window)
        self.vtk_overlay_window.add_vtk_actor(vtk_text.text_actor, 2)


def run_demo():
    """ Run demo """
    app = QApplication([])

    video_source = 0
    demo = TextOverlayDemo(video_source)
    demo.start()
    demo.show()

    return sys.exit(app.exec())
