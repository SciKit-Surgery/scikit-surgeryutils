# coding=utf-8

""" Demo app, to demo charuco markers."""
import sys
import six
import cv2
from cv2 import aruco
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Slot
import sksurgeryvideoutils.utils.image_utils as iu
import sksurgeryimage.calibration.aruco as ar

# pylint: disable=too-many-instance-attributes


class CharucoDemoGui(QtWidgets.QWidget):
    """ Demo GUI, with 2 QLabel side by side."""
    def __init__(self, camera, x_squares, y_squares, dictionary):
        super().__init__()

        if camera < 0:
            raise ValueError('The camera number should be >= 0')

        if not isinstance(dictionary, int):
            raise TypeError('dictionary should be an int >= 0')

        if dictionary < 0:
            raise ValueError('dictionary should be an ArUco enum.')

        self.cap = cv2.VideoCapture(camera)  # pylint: disable=no-member

        if not self.cap.isOpened():
            raise ValueError("Unable to open camera:" + str(camera))

        grabbed, self.frame = self.cap.read()
        if not grabbed:
            raise RuntimeError("Failed to grab first frame.")

        self.dictionary = aruco.Dictionary_get(dictionary)
        self.board = aruco.CharucoBoard_create(x_squares,
                                               y_squares,
                                               2,
                                               1,
                                               self.dictionary)

        self.layout = QtWidgets.QHBoxLayout()

        self.image_label = QtWidgets.QLabel("Image")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.setLayout(self.layout)

        self.grab = QtCore.QTimer()
        self.grab.setInterval(50)

        # pylint: disable=maybe-no-member
        self.grab.timeout.connect(self.update_image)
        self.grab.start()

    @Slot()
    def update_image(self):

        """ Updates the image. """

        # Then grab image
        grabbed = self.cap.grab()
        if not grabbed:
            raise RuntimeError("Failed to grab frame number:"
                               + str(self.number_frames))
        # Then decode image
        self.cap.retrieve(self.frame)

        # OpenCV does BGR, Qt wants RGB
        # pylint: disable=no-member
        rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        greyscale_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # Run aruco to detect markers
        number_of_markers, marker_corners, marker_ids, \
            chessboard_corners, chessboard_ids \
            = ar.detect_charuco_points(self.dictionary,
                                       greyscale_frame,
                                       self.board
                                       )

        # Draw detected corners back on RGB image.
        if chessboard_corners is not None \
            and chessboard_ids is not None \
                and len(chessboard_corners) \
                and len(chessboard_ids):
            annotated_frame = ar.draw_charuco_corners(rgb_frame,
                                                      chessboard_corners,
                                                      chessboard_ids
                                                      )
        else:
            annotated_frame = rgb_frame

        # Display annotated RGB image.
        pixmap = iu.image_to_pixmap(annotated_frame)
        self.image_label.setPixmap(pixmap)


def run_charucotest_demo(camera, width, height, dictionary):

    """ Prints command line args, and launches main screen."""
    six.print_("Camera:" + str(camera))
    six.print_("  Width:" + str(width))
    six.print_("  Height:" + str(height))
    six.print_("Dictionary:" + str(dictionary))

    app = QtWidgets.QApplication([])

    widget = CharucoDemoGui(camera, width, height, dictionary)
    widget.show()

    return sys.exit(app.exec_())
