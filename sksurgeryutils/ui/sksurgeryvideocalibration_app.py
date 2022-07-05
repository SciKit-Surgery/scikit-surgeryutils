# coding=utf-8

""" Functions to run video calibration, in a VTKOverlayWindow (i.e. Qt). """

import os
import sys
from datetime import datetime
import cv2
from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QHBoxLayout, QApplication
from PySide2.QtCore import QTimer
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
import sksurgeryimage.calibration.chessboard_point_detector as cpd
import sksurgerycalibration.video.video_calibration_driver_mono as mc
import sksurgeryutils.utils.opencv_video_capture_utils as vcu

# pylint: disable=protected-access,unused-argument,unused-variable


class BaseDriver:
    """
    Base class for both CalibrationDriver and CalibrationCheckerDriver.
    Separate from Qt stuff, so it can be used in interactive mode or not.
    """
    def __init__(self,
                 configuration,
                 source):
        """
        Constructor must throw if anything at all wrong.

        :raises ValueError, RuntimeError.
        """
        if configuration is None:
            raise ValueError(
                "You must provide a configuration file. "
                "(see config/video_chessboard_conf.json for example).")

        # Throws RuntimeError if anything wrong.
        source = vcu.validate_camera_source(source)

        # For now just doing chessboards.
        # The underlying framework works for several point detectors,
        # but each would have their own parameters etc.
        method = configuration.get("method", "chessboard")
        if method != "chessboard":
            raise ValueError("Only chessboard calibration"
                             " is currently supported")

        # The video source either defaults to whatever size OpenCV
        # gives, or you can specify the size in the config file.
        window_size = configuration.get("window size", None)
        self.cap = vcu.open_video_source(source, window_size)

        # These are the key parameters for the chessboard.
        size = configuration.get("square size in mm", 3)
        corners = configuration.get("corners", [14, 10])
        self.corners = (corners[0], corners[1])

        # .. and hence we can now create a chessboard point detector.
        self.detector = cpd.ChessboardPointDetector(corners, size)

        self.frame_ok = False
        self.frame = None

        self.key_pressed = None

    def set_key_pressed(self, key_pressed):
        """
        Set's member variable key_pressed.
        """
        self.key_pressed = key_pressed

    def get_key_pressed(self):
        """
        Get's member variable key_pressed.
        """
        return self.key_pressed

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

    def process_frame(self):
        """
        Derived classes must implement this.
        """
        raise NotImplementedError("Derived classes must implement "
                                  "process_frame()")


class CalibrationDriver(BaseDriver):
    """
    Main calibration logic in a separate class, so it can be
    used either in interactive mode, or not.
    """
    def __init__(self,
                 configuration,
                 source,
                 output_dir=None,
                 file_prefix=None
                 ):
        """
        Constructor must throw if anything at all wrong.
        """
        super().__init__(configuration=configuration,
                         source=source)

        # These two are optional, so can be None.
        self.output_dir = output_dir
        self.file_prefix = file_prefix

        if self.file_prefix is not None and self.output_dir is None:
            self.output_dir = os.getcwd()

        # Parameters specific to calibration.
        self.calibrator = mc.MonoVideoCalibrationDriver(self.detector,
                                                        self.corners[0] *
                                                        self.corners[1])

        self.min_num_views = configuration.get("minimum number of views", 5)

        print("Minimum number of views to calibrate:" + str(self.min_num_views))

    def process_frame(self):
        """
        Extracts the points from the image, and if we have enough frames,
        will automatically recalibrate.

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

                if self.output_dir is not None:

                    if not os.path.isdir(self.output_dir):
                        os.makedirs(self.output_dir)

                    self.calibrator.save_data(self.output_dir,
                                              self.file_prefix)
                    self.calibrator.save_params(self.output_dir,
                                                self.file_prefix)
        else:
            print("Failed to detect points")

        return number_points, annotated


class BaseCalibrationWidget(QWidget):
    """
    Base class Widget to provide calibration methods in interactive mode.
    """
    def __init__(self, configuration, driver):
        """
        Constructor must throw if any issues.

        :param configuration: Dictionary of configuration data.
        :param driver: class derived from BaseDriver
        """
        super().__init__()

        if configuration is None:
            raise ValueError("Configuration data is None")

        if driver is None:
            raise ValueError("Driver is None")

        self.driver = driver

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.vtk_overlay_window = VTKOverlayWindow()
        self.layout.addWidget(self.vtk_overlay_window)

        self.keypress_delay_in_milliseconds \
            = configuration.get("keypress delay in ms", 1000)

        self.vtk_overlay_window.AddObserver("KeyPressEvent",
                                            self.on_key_press_event)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_view)

        self.update_rate = 30
        self.annotation_time = None
        self.show_annotation = False

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
        Called by QTimer, to do the main UI window update.
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

        if self.driver.get_key_pressed() is not None:

            number_of_points, annotated_image = self.driver.process_frame()
            self.driver.set_key_pressed(None)

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


class CalibrationWidget(BaseCalibrationWidget):
    """
    Widget to provide calibration logic in interactive mode.
    """
    def __init__(self,
                 configuration,
                 driver):
        """
        Widget class to provide GUI event handling for the Calibration process.
        """
        super().__init__(configuration, driver)

        print("Press 'q' to quit and 'c' to capture an image.")

    def on_key_press_event(self, obj, event):
        """
        Called when a key is pressed, if 'q', exit, if 'c' capture image.
        """
        if self.vtk_overlay_window.GetKeySym() == 'q':
            print("Detected 'q' key press, exiting.")
            self.on_exit_selected()
        elif self.vtk_overlay_window.GetKeySym() == 'c':
            print("Detected 'c' key press, capturing data.")
            self.driver.set_key_pressed('c')


class CalibrationManager:
    """
    For non-interactive mode, reads from an OpenCV VideoCapture, and
    samples every few frames, as determined by "sample frequency" in config.
    """
    def __init__(self,
                 configuration,
                 driver
                 ):
        """
        General manager class that will repeatedly call driver.grab_frame()
        and then trigger driver.extract_points() every few frames.

        :param configuration: Dictionary of configuration parameters.
        :param driver: Class derived from BaseDriver.
        """
        if driver is None:
            raise ValueError("Driver is None")
        if configuration is None:
            raise ValueError("Configuration is None")

        self.driver = driver

        self.sample_frequency = configuration.get("sample frequency", 1)

    def run(self):
        """
        Process frames from the video source, until no frames.
        """
        frames_sampled = 0

        while True:

            frame_ok, _ = self.driver.grab_frame()

            if not frame_ok:
                print("Reached end of video source or read failure.")
                break

            frames_sampled += 1

            if frames_sampled % self.sample_frequency == 0:

                number_of_points, _ = self.driver.process_frame()

                if number_of_points < 1:
                    print("Failed to detect points")


def run_video_calibration(configuration,
                          source,
                          output_dir=None,
                          file_prefix=None,
                          noninteractive=None
                          ):
    """
    Performs Video Calibration using OpenCV
    source and scikit-surgerycalibration.

    It's a demo app, so currently, only chessboards are supported.

    :param configuration: dictionary of configuration data.
    :param source: OpenCV video source, either webcam number or file name.
    :param output_dir: optional directory name to dump calibrations to.
    :param file_prefix: optional file name prefix when saving.
    :param noninteractive: If True we run without GUI.
    """
    driver = CalibrationDriver(configuration,
                               source,
                               output_dir,
                               file_prefix)

    if noninteractive:

        manager = CalibrationManager(configuration=configuration,
                                     driver=driver)
        manager.run()

    else:

        app = QtWidgets.QApplication([])

        widget = CalibrationWidget(configuration=configuration,
                                   driver=driver)
        widget.show()
        widget.start()
        sys.exit(app.exec_())
