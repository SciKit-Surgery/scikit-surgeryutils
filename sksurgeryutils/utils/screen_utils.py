# coding=utf-8
""" Any useful utilities relating to displays/screens. """
# pylint:disable=no-name-in-module

from PySide6.QtGui import QGuiApplication


# pylint: disable=useless-object-inheritance
# pylint: disable=too-few-public-methods


class ScreenController(object):
    """ This class detects the connected screens/monitors, and
    returns the primary screen and a list of any secondary screens.
    """

    def __init__(self):
        self.screens = QGuiApplication.screens()
        self.primary = QGuiApplication.primaryScreen()

        if self.primary in self.screens:
            self.screens.remove(self.primary)

    def list_of_screens(self):
        """Return the primary screen and list of other available screens"""

        return self.primary, self.screens
