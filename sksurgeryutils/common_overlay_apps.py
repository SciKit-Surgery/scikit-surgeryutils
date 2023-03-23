# coding=utf-8

""" Common use cases for vtk_overlay_window """

import datetime
import logging
import platform

import cv2
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QHBoxLayout
from sksurgeryimage.acquire.video_source import TimestampedVideoSource
from sksurgeryimage.acquire.video_writer import TimestampedVideoWriter
from sksurgeryvtk.models.vtk_surface_model_directory_loader \
    import VTKSurfaceModelDirectoryLoader
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow


class OverlayBaseWidget(QWidget):
    """
    Base class for applications that use vtk_overlay_window.
    The update() method should be implemented in the child
    class.

    :param video_source: OpenCV compatible video source (int or filename)
    :param dims: size of video feed
    """

    def __init__(self, video_source, dims=None, init_vtk_widget=True):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        if platform.system() == 'Linux':
            init_vtk_widget = False
        else:
            init_vtk_widget = True

        self.vtk_overlay_window = VTKOverlayWindow(init_widget=init_vtk_widget)
        self.layout.addWidget(self.vtk_overlay_window)

        self.video_source = TimestampedVideoSource(video_source, dims)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_view)

        self.update_rate = 30
        self.img = None
        self.save_frame = None

    def start(self):
        """
        Starts the timer, which repeatedly triggers the update_view() method.
        """
        self.timer.start(1000.0 / self.update_rate)

    def stop(self):
        """
        Stops the timer.
        """
        self.timer.stop()

    def terminate(self):
        """
        Make sure that the VTK Interactor terminates nicely, otherwise
        it can throw some error messages, depending on the usage.
        """
        self.vtk_overlay_window._RenderWindow.Finalize()  # pylint: disable=protected-access
        self.vtk_overlay_window.TerminateApp()

    def add_vtk_models_from_dir(self, directory):
        """
        Add VTK models to the foreground.
        :param: directory, location of models
        """
        model_loader = VTKSurfaceModelDirectoryLoader(directory)
        self.vtk_overlay_window.add_vtk_models(model_loader.models)

    def update_view(self):
        """ Update the scene background and/or foreground.
            Should be implemented by sub class """

        raise NotImplementedError('Should have implemented this method.')


class OverlayOnVideoFeed(OverlayBaseWidget):
    """
    Uses the acquired video feed as the background image,
    with no additional processing.
    """

    def update_view(self):
        """
        Get the next frame of input and display it.
        """
        _bool_retrieve, self.img = self.video_source.read()
        self.vtk_overlay_window.set_video_image(self.img)
        self.vtk_overlay_window.Render()

        if platform.system() == 'Linux':
            self.vtk_overlay_window.Initialize()


class OverlayOnVideoFeedCropRecord(OverlayBaseWidget):
    """ Add cropping of the incoming video feed, and the ability to
        record the vtk_overlay_window.

       :param video_source: OpenCV compatible video source (int or filename)
       :param output_filename: Location of output video file when recording.
                               If none specified, the current date/time is
                               used as the filename.
    """

    def __init__(self, video_source, output_filename=None, dims=None):
        super().__init__(video_source, dims)
        self.output_filename = output_filename
        self.video_writer = None

    def update_view(self):
        """
        Get the next frame of input, crop and/or
        write to file (if either enabled).
        """
        _, self.img = self.video_source.read()

        self.vtk_overlay_window.set_video_image(self.img)
        self.vtk_overlay_window.Render()

        if self.save_frame:
            output_frame = self.get_output_frame()
            self.video_writer.write_frame(output_frame,
                                          self.video_source.timestamp)

    def set_roi(self):
        """
           Crop the incoming video stream using ImageCropper.
           Function is depreciated due to moving to opencv-headless
           in sksurgeryvtk. I've left it in for the minute in case
           any one is using it without my knowlegde
        """
        raise RuntimeError("Set Roi function is depreciated and",
                           " is not longer implemented in sksurgeryutils")

    def get_output_frame(self):
        """ Get the output frame to write in numpy format."""
        output_frame = \
            self.vtk_overlay_window.convert_scene_to_numpy_array()
        output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

        return output_frame

    def on_record_start(self):
        """ Start recording data on each frame update.
        It is expected that this will be triggered using a Qt signal e.g. from
        a button click. (see sksurgerydavinci.ui.Viewers for examples) """

        # Set the filename to current date/time if no name specified.
        if not self.output_filename:
            self.output_filename = 'outputs/' + \
                                   datetime.datetime.now().strftime( \
                                       "%Y-%m-%d.%H-%M-%S") + '.avi'

        output_frame = self.get_output_frame()
        height, width = output_frame.shape[:2]
        self.video_writer = TimestampedVideoWriter(self.output_filename,
                                                   self.update_rate, width,
                                                   height)
        self.save_frame = True
        logging.debug("Recording started.")

    def on_record_stop(self):
        """ Stop recording data. """
        self.save_frame = False
        self.video_writer.close()
        logging.debug("Recording stopped.")
