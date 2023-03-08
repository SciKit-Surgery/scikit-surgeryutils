# -*- coding: utf-8 -*-

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def setup_qt():
    """ Create the QT application. """
    app = QApplication([])
    return app
