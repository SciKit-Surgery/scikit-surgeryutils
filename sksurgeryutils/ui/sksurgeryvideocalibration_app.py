# coding=utf-8

""" Functions to run video calibration, in interactive or non-interactive mode. """

import os
import sys
import cv2
import time
from datetime import datetime
from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QHBoxLayout, QApplication
from PySide2.QtCore import QTimer
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
import sksurgeryimage.calibration.chessboard_point_detector as cpd
import sksurgerycalibration.video.video_calibration_driver_mono as mc

# pylint:disable=too-many-nested-blocks,too-many-branches


class CalibrationDriver:
    """
    Main calibration logic in a separate class, so it can be
    used either in interactive (widget) mode, or not.
    """
    def __init__(self,
                 configuration=None,
                 save_dir=None,
                 prefix=None
                 ):
        """
        Constructor must throw if anything at all wrong.
        """
        self.save_dir = save_dir
        self.prefix = prefix

        if self.prefix is not None and self.save_dir is None:
            self.save_dir = "./"

        if configuration is None:
            configuration = {}

        # For now just doing chessboards.
        # The underlying framework works for several point detectors,
        # but each would have their own parameters etc.
        method = configuration.get("method", "chessboard")
        if method != "chessboard":
            raise ValueError("Only chessboard calibration is currently supported")

        source = configuration.get("source", 0)
        window_size = configuration.get("window size", None)
        size = configuration.get("square size in mm", 3)

        corners = configuration.get("corners", [14, 10])
        self.corners = (corners[0], corners[1])
        self.min_num_views = configuration.get("minimum number of views", 5)

        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera.")

        if window_size is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_size[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, window_size[1])
            print("Video feed set to ("
                  + str(window_size[0]) + " x " + str(window_size[1]) + ")")
        else:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print("Video feed defaults to ("
                  + str(width) + " x " + str(height) + ")")

        self.detector = cpd.ChessboardPointDetector(corners, size)
        self.calibrator = mc.MonoVideoCalibrationDriver(self.detector,
                                                        corners[0] * corners[1])

        self.frame_ok = False
        self.frame = None

        print("Minimum number of views to calibrate:" + str(self.min_num_views))

    def shutdown(self):
        """
        Try to do any cleanup properly. Releases video source.
        """
        self.cap.release()

    def grab_frame(self):
        """
        Captures image.

        :return: frame_ok, frame
        :rtype: bool, numpy.ndarray
        """
        self.frame_ok, self.frame = self.cap.read()

        if not self.frame_ok:
            print("Reached end of video source or read failure.")

        return self.frame_ok, self.frame

    def extract_points(self):
        """
        Extracts the points from the image.

        :return: number_points, annotated
        :rtype: int, numpy.ndarray
        """
        annotated = None
        number_points = self.calibrator.grab_data(self.frame)

        if number_points > 0:
            img_pts = self.calibrator.video_data.image_points_arrays[-1]
            annotated = cv2.drawChessboardCorners(self.frame,
                                                  self.corners,
                                                  img_pts,
                                                  number_points)
            number_of_views = self.calibrator.get_number_of_views()
            print("Number of frames = " + str(number_of_views))

            if number_of_views >= self.min_num_views:

                proj_err, params = self.calibrator.calibrate()
                print("Reprojection (2D) error is:" + str(proj_err))
                print("Intrinsics are:")
                print(params.camera_matrix)
                print("Distortion matrix is:")
                print(params.dist_coeffs)

                if self.save_dir is not None:

                    if not os.path.isdir(self.save_dir):
                        os.makedirs(self.save_dir)

                    self.calibrator.save_data(self.save_dir,
                                              self.prefix)
                    self.calibrator.save_params(self.save_dir,
                                                self.prefix)
        else:
            print("Failed to detect points")

        return number_points, annotated


class CalibrationWidget(QWidget):
    """
    Widget to provide calibration in interactive mode.
    """
    def __init__(self,
                 configuration=None,
                 save_dir=None,
                 prefix=None):
        """
        Constructor creates the internal CalibrationDriver.
        """
        super().__init__()
        self.driver = CalibrationDriver(configuration,
                                        save_dir,
                                        prefix)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.vtk_overlay_window = VTKOverlayWindow()
        self.layout.addWidget(self.vtk_overlay_window)

        self.keypress_delay_in_milliseconds = configuration.get("keypress delay", 1000)

        self.vtk_overlay_window.AddObserver("KeyPressEvent",
                                            self.on_key_press_event)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_view)

        self.update_rate = 30
        self.do_capture = False
        self.annotation_time = None
        self.show_annotation = False

        print("Press 'q' to quit and 'c' to capture an image.")

    def start(self):
        """
        Starts the timer, which repeatedly triggers the update_view() method.
        """
        self.timer.start(int(1000.0 / self.update_rate))

    def stop(self):
        """
        Stops the timer.
        """
        self.timer.stop()

    def finalize(self):
        """
        Make sure that the VTK Interactor terminates nicely, otherwise
        it can throw some error messages, depending on the usage.
        """
        self.vtk_overlay_window._RenderWindow.Finalize()

    def on_key_press_event(self, obj, event):
        """
        Called when a key is pressed, if 'q', exit the app, if 'c' capture image.
        """
        if self.vtk_overlay_window.GetKeySym() == 'q':
            print("Detected 'q' key press, exiting.")
            self.on_exit_selected()
        elif self.vtk_overlay_window.GetKeySym() == 'c':
            print("Detected 'c' key press, capturing image.")
            self.do_capture = True

    def on_exit_selected(self):
        """
        Opportunity to do any clear up, before exiting app.

        Stops timer, shutsdown camera feed, and asks VTK to kill window/app.
        """
        self.stop()
        self.driver.shutdown()
        self.finalize()
        QApplication.quit()

    def update_view(self):
        """
        Called by base class, to do the main UI window update.
        """
        frame_ok, frame = self.driver.grab_frame()

        if not frame_ok:
            print("Failed to read frame")
            return

        time_now = datetime.now()

        if self.annotation_time is not None:
            time_diff = time_now - self.annotation_time
            seconds = time_diff.total_seconds()
            if seconds > self.keypress_delay_in_milliseconds / 1000.0:
                self.show_annotation = False

        if not self.show_annotation:
            self.vtk_overlay_window.set_video_image(frame)

        if self.do_capture:

            number_of_points, annotated_image = self.driver.extract_points()
            self.do_capture = False

            if number_of_points < 1:
                print("Failed to detect points")
                return

            self.vtk_overlay_window.set_video_image(annotated_image)
            self.vtk_overlay_window.Render()
            self.repaint()

            self.annotation_time = datetime.now()
            self.show_annotation = True

        else:
            self.vtk_overlay_window.Render()
            self.repaint()


class CalibrationManager:
    """
    For non-interactive mode. Just reads from video source
    in a loop, and extracts points every few frames (see config file).
    """
    def __init__(self,
                 configuration=None,
                 save_dir=None,
                 prefix=None
                 ):
        """
        Constructor creates the internal CalibrationDriver.
        """
        self.driver = CalibrationDriver(configuration,
                                        save_dir,
                                        prefix)

        self.sample_frequency = configuration.get("sample frequency", 1)
        self.frames_sampled = 0

    def run(self):
        """
        Main loop that will process frames from the video source, until no frames.
        """
        while True:

            frame_ok, frame = self.driver.grab_frame()

            if not frame_ok:
                print("Reached end of video source or read failure.")
                break

            self.frames_sampled += 1

            if self.frames_sampled % self.sample_frequency == 0:

                number_of_points, _ = self.driver.extract_points()

                if number_of_points < 1:
                    print("Failed to detect points")


def run_video_calibration(configuration=None,
                          save_dir=None,
                          prefix=None):
    """
    Performs Video Calibration using OpenCV
    source and scikit-surgerycalibration.
    Currently only chessboards are supported

    :param configuration: dictionary of configuration data.
    :param save_dir: optional directory name to dump calibrations to.
    :param prefix: file name prefix when saving

    :raises ValueError: if method is not supported
    """
    interactive = configuration.get("interactive", True)

    if interactive:

        app = QtWidgets.QApplication([])

        widget = CalibrationWidget(configuration,
                                   save_dir,
                                   prefix)
        widget.show()
        widget.start()
        sys.exit(app.exec_())

    else:

        manager = CalibrationManager(configuration,
                                     save_dir,
                                     prefix)
        manager.run()
