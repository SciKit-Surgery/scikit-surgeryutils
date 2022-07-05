# coding=utf-8

""" Functions to assess calibration accuracy, in a VTKOverlayWindow. """

import os
import sys
import numpy as np
import cv2
from PySide2 import QtWidgets
from sksurgerycalibration.video.video_calibration_params import \
                MonoCalibrationParams
import sksurgeryutils.ui.sksurgeryvideocalibration_app as vca

# pylint: disable=unused-argument


class CalibrationCheckerDriver(vca.BaseDriver):
    """
    Main app logic to check the accuracy of a calibration.
    """
    def __init__(self,
                 configuration,
                 source,
                 calibration_dir=None,
                 file_prefix=None
                 ):
        """
        Constructor must throw if anything at all wrong.
        """
        super().__init__(configuration=configuration,
                         source=source)

        if calibration_dir is None:
            raise ValueError("Calibration dir must not be None")
        if not isinstance(calibration_dir, str):
            raise ValueError("Calibration dir should be a string")
        if len(calibration_dir) == 0:
            raise ValueError("Calibration dir is an empty string")
        if not os.path.isdir(calibration_dir):
            raise ValueError("Calibration dir is not a dir")

        # Parameters specific to calibration checking, as base class
        # has all the stuff for video capture etc.
        existing_calibration = MonoCalibrationParams()
        existing_calibration.load_data(calibration_dir,
                                       file_prefix,
                                       halt_on_ioerror=False)
        self.intrinsics = existing_calibration.camera_matrix
        self.distortion = existing_calibration.dist_coeffs

        self.captured_positions = np.zeros((0, 3))

        print("Loaded calibration from:" + str(calibration_dir))

    def process_frame(self):
        """
        Main logic for what to extract and what to measure.

        :return: number_points, annotated
        :rtype: int, numpy.ndarray
        """
        number_points = 0
        annotated = None

        undistorted = cv2.undistort(self.frame,
                                    self.intrinsics, self.distortion)

        _, object_points, image_points = \
            self.detector.get_points(undistorted)

        if image_points.shape[0] > 0:

            number_points = self.corners[0] * self.corners[1]

            annotated = cv2.drawChessboardCorners(undistorted,
                                                  self.corners,
                                                  image_points,
                                                  number_points)

            pnp_ok, _, tvec = cv2.solvePnP(object_points,
                                           image_points,
                                           self.intrinsics,
                                           None)

            if pnp_ok:

                self.captured_positions = np.append(self.captured_positions,
                                                    np.transpose(tvec),
                                                    axis=0)

                if self.captured_positions.shape[0] > 1:

                    if self.key_pressed == 't':
                        print("Translation: "
                              + str(self.captured_positions[-1][0]
                                  - self.captured_positions[-2][0]) + " "
                              + str(self.captured_positions[-1][1]
                                  - self.captured_positions[-2][1]) + " "
                              + str(self.captured_positions[-1][2]
                                  - self.captured_positions[-2][2]) + " ")

                    if self.key_pressed == 'm':
                        print("Mean:"
                              + str(np.mean(self.captured_positions, axis=0)))
                        print("StdDev:"
                              + str(np.std(self.captured_positions, axis=0)))

                if self.key_pressed == 'c':
                    print("Pose" + str(tvec[0][0]) + " "
                          + str(tvec[1][0]) + " "
                          + str(tvec[2][0]))
            else:
                print("Failed to solve PnP.")
        else:
            print("Failed to detect points.")

        return number_points, annotated


class CalibrationCheckerWidget(vca.BaseCalibrationWidget):
    """
    Widget to provide calibration checking logic in interactive mode.
    """
    def __init__(self,
                 configuration,
                 driver):
        """
        Widget class to provide GUI event handling for the Checking process.
        """
        super().__init__(configuration, driver)

        print("Press 'q' to quit.")
        print("Press 'c' to capture an image.")
        print("Press 't' to measure translation.")
        print("Press 'm' to measure the mean/std-dev of a fixed position.")

    def on_key_press_event(self, obj, event):
        """
        Called when a key is pressed.
        """
        if self.vtk_overlay_window.GetKeySym() == 'q':
            print("Detected 'q' key press, exiting.")
            self.on_exit_selected()
        elif self.vtk_overlay_window.GetKeySym() == 'c':
            print("Detected 'c' key press, capturing data.")
            self.driver.set_key_pressed('c')
        elif self.vtk_overlay_window.GetKeySym() == 't':
            print("Detected 't' key press, measuring translation.")
            self.driver.set_key_pressed('t')
        elif self.vtk_overlay_window.GetKeySym() == 'm':
            print("Detected 'm' key press, measuring mean/std-dev.")
            self.driver.set_key_pressed('m')


def run_video_calibration_checker(configuration,
                                  source,
                                  calib_dir,
                                  file_prefix,
                                  noninteractive
                                  ):
    """
    Checks how accurate an OpenCV calibration is. Essentially,
    you move a chessboard by a known amount, e.g. 5mm, and
    we use PnP to work out how far the camera has moved relative
    to the chessboard.

    It's a demo app, so currently, only chessboards are supported.

    :param configuration: dictionary of configuration data.
    :param source: OpenCV video source, either webcam number or file name.
    :param calib_dir: Directory containing a calibration.
    :param file_prefix: optional file name prefix when loading.
    :param noninteractive: If True we run without GUI.
    """
    driver = CalibrationCheckerDriver(configuration,
                                      source,
                                      calib_dir,
                                      file_prefix
                                      )
    if noninteractive:

        manager = vca.CalibrationManager(configuration=configuration,
                                         driver=driver)
        manager.run()

    else:

        app = QtWidgets.QApplication([])

        widget = CalibrationCheckerWidget(configuration=configuration,
                                          driver=driver)
        widget.show()
        widget.start()
        sys.exit(app.exec_())
