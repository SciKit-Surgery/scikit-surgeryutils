"""Common use cases for vtk_overlay_window"""

#pylint: disable=no-member, no-name-in-module, protected-access
# coding=utf-8
import datetime
import logging
import cv2

from PySide2.QtCore import QTimer
from sksurgeryimage.acquire.video_source import TimestampedVideoSource
from sksurgeryimage.acquire.video_writer import TimestampedVideoWriter
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
from sksurgeryvtk.models.vtk_surface_model_directory_loader \
    import VTKSurfaceModelDirectoryLoader

class OverlayBaseApp():
    """
    Base class for applications that use vtk_overlay_window.
    The update() method should be implemented in the child
    class.

    :param video_source: OpenCV compatible video source (int or filename)
    """
    def __init__(self, video_source):
        self.vtk_overlay_window = VTKOverlayWindow()
        self.video_source = TimestampedVideoSource(video_source)
        self.update_rate = 30
        self.img = None
        self.timer = None
        self.save_frame = None

    def start(self):
        """Show the overlay widget and
        set a timer running"""
        self.vtk_overlay_window.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000.0 / self.update_rate)

    def add_vtk_models_from_dir(self, directory):
        """
        Add VTK models to the foreground.
        :param: directory, location of models
        """
        model_loader = VTKSurfaceModelDirectoryLoader(directory)
        self.vtk_overlay_window.add_vtk_models(model_loader.models)

    def update(self):
        """ Update the scene background and/or foreground.
            Should be implemented by sub class """

        raise NotImplementedError('Should have implemented this method.')

    def stop(self):
        """
        Make sure that the VTK Interactor terminates nicely, otherwise
        it can throw some error messages, depending on the usage.
        """
        self.vtk_overlay_window._RenderWindow.Finalize()
        self.vtk_overlay_window.TerminateApp()

class OverlayOnVideoFeed(OverlayBaseApp):
    """
    Uses the acquired video feed as the background image,
    with no additional processing. Can also record a video of the scene.
    """

    def __init__(self, video_source, output_filename=None):
        super().__init__(video_source)
        self.output_filename = output_filename
        self.video_writer = None

    def update(self):
        """ Get the next frame of input and write to file (if enabled). """
        _, self.img = self.video_source.read()
        self.vtk_overlay_window.set_video_image(self.img)
        self.vtk_overlay_window._RenderWindow.Render()

        if self.save_frame:
            output_frame = self.get_output_frame()
            self.video_writer.write_frame(output_frame,
                                          self.video_source.timestamp)

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
                datetime.datetime.now().strftime("%Y-%m-%d.%H-%M-%S") + '.avi'

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
