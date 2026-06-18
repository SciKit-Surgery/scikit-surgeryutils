# coding=utf-8

"""
Stereo augmented reality renderer demo application.

Displays 3D models overlaid on stereo video feeds with interactive
manipulation. An interactive VTKOverlayWindow allows the user to
move models, and changes are propagated to a passive
VTKStackedStereoWindow for stereo output.
"""

import logging
import sys
import os

import cv2
import numpy as np
import vtk

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow

import sksurgerycore.configuration.configuration_manager as cm
import sksurgeryvtk.models.surface_model_loader as sml
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
from sksurgeryvtk.widgets.vtk_stacked_stereo_window import \
    VTKStackedStereoWindow
from sksurgeryvtk.widgets.vtk_interlaced_stereo_window import \
    VTKInterlacedStereoWindow


LOGGER = logging.getLogger(__name__)

# pylint: disable=too-many-instance-attributes, too-many-positional-arguments


class TrackballActorWithZoom(vtk.vtkInteractorStyleTrackballActor):
    """
    Custom VTK interactor style that derives from vtkInteractorStyleTrackballActor.

    Overrides the scroll/dolly behaviour: instead of scaling the actor,
    we translate the picked actor along the camera's view direction
    (towards/away from the camera).
    """

    def __init__(self):
        super().__init__()
        self.AddObserver("MouseWheelForwardEvent", self._on_scroll_forward)
        self.AddObserver("MouseWheelBackwardEvent", self._on_scroll_backward)

    def _on_scroll_forward(self, obj, event):
        """Move picked actor towards the camera."""
        del obj, event
        self._dolly_actor(-5.0)

    def _on_scroll_backward(self, obj, event):
        """Move picked actor away from the camera."""
        del obj, event
        self._dolly_actor(5.0)

    def _dolly_actor(self, distance):
        """
        Translate the currently picked actor along the camera
        view direction by the given distance.
        """
        interactor = self.GetInteractor()
        if interactor is None:
            return

        renderer = interactor.FindPokedRenderer(
            interactor.GetEventPosition()[0],
            interactor.GetEventPosition()[1])
        if renderer is None:
            return

        camera = renderer.GetActiveCamera()
        view_dir = np.array(camera.GetDirectionOfProjection())
        view_dir = view_dir / (np.linalg.norm(view_dir) + 1e-9)

        # Find the prop under the mouse, or use the last interaction prop
        prop = self.GetInteractionProp()
        if prop is None:
            return

        # Get current position and translate
        current_pos = np.array(prop.GetPosition())
        new_pos = current_pos + view_dir * distance
        prop.SetPosition(new_pos[0], new_pos[1], new_pos[2])

        interactor.Render()


class StereoRendererApp:
    """
    Main application class for the stereo AR renderer.

    Creates two windows:
    - An interactive VTKOverlayWindow (primary screen) for manipulating models.
    - A passive VTKStackedStereoWindow (secondary screen if available) for
      stereo output.

    Both windows share the same set of VTK models. Interactions on the
    primary window are propagated to the stereo window.

    :param left_intrinsics: 3x3 numpy array, left camera intrinsic matrix
    :param right_intrinsics: 3x3 numpy array, right camera intrinsic matrix
    :param left_to_right: 4x4 numpy array, stereo extrinsic (left to right)
    :param models_config: dict from ConfigurationManager
    :param clipping_range: tuple (near, far)
    :param left_video_source: str or int, left video source
    :param right_video_source: str or int, right video source
    :param model_to_world: 4x4 numpy array or None, initial model pose
    :param camera_to_world: 4x4 numpy array or None, initial camera pose
    :param stereo_mode: str, 'stacked' or 'interlaced'
    """

    def __init__(self,
                 left_intrinsics,
                 right_intrinsics,
                 left_to_right,
                 models_config,
                 clipping_range,
                 left_video_source,
                 right_video_source,
                 model_to_world=None,
                 camera_to_world=None,
                 stereo_mode='stacked'):

        self.left_intrinsics = left_intrinsics
        self.right_intrinsics = right_intrinsics
        self.left_to_right = left_to_right
        self.clipping_range = clipping_range

        # Determine if sources are static images or video
        self.left_is_static = self._is_static_image(left_video_source)
        self.right_is_static = self._is_static_image(right_video_source)

        # Open video sources
        self.left_image = None
        self.right_image = None
        self.left_capture = None
        self.right_capture = None

        if self.left_is_static:
            self.left_image = cv2.imread(left_video_source)
            if self.left_image is None:
                raise ValueError(
                    f"Cannot read left image: {left_video_source}")
        else:
            source = self._parse_video_source(left_video_source)
            self.left_capture = cv2.VideoCapture(source)
            if not self.left_capture.isOpened():
                raise ValueError(
                    f"Cannot open left video source: {left_video_source}")

        if self.right_is_static:
            self.right_image = cv2.imread(right_video_source)
            if self.right_image is None:
                raise ValueError(
                    f"Cannot read right image: {right_video_source}")
        else:
            source = self._parse_video_source(right_video_source)
            self.right_capture = cv2.VideoCapture(source)
            if not self.right_capture.isOpened():
                raise ValueError(
                    f"Cannot open right video source: {right_video_source}")

        # Load models
        loader = sml.SurfaceModelLoader(models_config)
        self.models = list(loader.get_surface_models())
        self.named_surfaces = loader.named_surfaces

        # Create the interactive overlay window (primary display)
        self.overlay_window = VTKOverlayWindow(
            offscreen=False,
            camera_matrix=self.left_intrinsics,
            clipping_range=self.clipping_range
        )
        self.overlay_window.add_vtk_models(self.models)

        # Create the stereo window (secondary display)
        if stereo_mode == 'interlaced':
            self.stereo_window = VTKInterlacedStereoWindow(
                offscreen=False,
                left_camera_matrix=self.left_intrinsics,
                right_camera_matrix=self.right_intrinsics,
                clipping_range=self.clipping_range
            )
        else:
            self.stereo_window = VTKStackedStereoWindow(
                offscreen=False,
                left_camera_matrix=self.left_intrinsics,
                right_camera_matrix=self.right_intrinsics,
                clipping_range=self.clipping_range
            )
        self.stereo_window.add_vtk_models(self.models)

        # Disable interactors on stereo window
        self.stereo_window.left_widget.GetInteractor().Disable()
        self.stereo_window.right_widget.GetInteractor().Disable()

        # Set up the custom interactor on the overlay window
        self.interactor_style = TrackballActorWithZoom()
        interactor = self.overlay_window.GetInteractor()
        interactor.SetInteractorStyle(self.interactor_style)

        # Connect interaction end to sync callback
        self.interactor_style.AddObserver(
            "EndInteractionEvent", self._on_interaction_end)
        self.interactor_style.AddObserver(
            "InteractionEvent", self._on_interaction)

        # Create main windows and handle screen placement
        self.primary_main_window = QMainWindow()
        self.primary_main_window.setCentralWidget(self.overlay_window)
        self.primary_main_window.setWindowTitle(
            "Stereo Renderer - Interactive")

        self.secondary_main_window = QMainWindow()
        self.secondary_main_window.setCentralWidget(self.stereo_window)
        self.secondary_main_window.setWindowTitle(
            "Stereo Renderer - Stereo Output")

        self._setup_screens()

        # Apply initial model-to-world if provided
        if model_to_world is not None:
            self.set_model_to_world(model_to_world)

        # Apply initial camera pose if provided
        if camera_to_world is not None:
            self.set_camera_to_world(camera_to_world)

        # Timer for update loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.update_rate = 30

    @staticmethod
    def _is_static_image(source):
        """Check if a video source string refers to a static image."""
        if isinstance(source, str):
            ext = os.path.splitext(source)[1].lower()
            return ext in ('.jpg', '.jpeg', '.png')
        return False

    @staticmethod
    def _parse_video_source(source):
        """
        Parse a video source string. If it looks like an integer,
        return it as int (device index), otherwise return as filename.
        """
        try:
            return int(source)
        except ValueError:
            return source

    def _setup_screens(self):
        """
        Position windows based on the number of available screens.
        If 2+ screens: overlay on primary (maximised), stereo on secondary
        (maximised). If 1 screen: show both on primary.
        """
        app = QApplication.instance()
        screens = app.screens()

        if len(screens) >= 2:
            primary_screen = screens[0]
            secondary_screen = screens[1]

            primary_geom = primary_screen.geometry()
            self.primary_main_window.setGeometry(primary_geom)
            self.primary_main_window.showMaximized()

            secondary_geom = secondary_screen.geometry()
            self.secondary_main_window.setGeometry(secondary_geom)
            self.secondary_main_window.showMaximized()
        else:
            self.primary_main_window.show()
            self.secondary_main_window.show()

    def start(self):
        """
        Start the update timer.
        """
        self.timer.start(int(1000.0 / self.update_rate))

    def stop(self):
        """
        Stop the update timer.
        """
        self.timer.stop()

    def update(self):
        """
        Timer callback. Reads the next frame from video sources,
        sets images on both windows, and renders.
        """
        left_frame = self._get_left_frame()
        right_frame = self._get_right_frame()

        if left_frame is None or right_frame is None:
            LOGGER.warning("Could not read frame from video source.")
            return

        # Set left image on the interactive overlay
        self.overlay_window.set_video_image(left_frame)
        self.overlay_window.Render()

        # Set stereo video images
        self.stereo_window.set_video_images(left_frame, right_frame)
        self.stereo_window.render()

    def _get_left_frame(self):
        """Get the current left frame (static or from capture)."""
        if self.left_is_static:
            return self.left_image.copy()
        ret, frame = self.left_capture.read()
        if not ret:
            # Loop video
            self.left_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.left_capture.read()
        return frame if ret else None

    def _get_right_frame(self):
        """Get the current right frame (static or from capture)."""
        if self.right_is_static:
            return self.right_image.copy()
        ret, frame = self.right_capture.read()
        if not ret:
            # Loop video
            self.right_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.right_capture.read()
        return frame if ret else None

    def _on_interaction(self, obj, event):
        """
        Called during an interaction. Syncs the pickable actor's
        model-to-world to all windows.
        """
        del obj, event
        self._sync_models_to_stereo()

    def _on_interaction_end(self, obj, event):
        """
        Called at the end of an interaction. Ensures all models
        have consistent model-to-world transforms across windows.
        """
        del obj, event
        self._sync_models_to_stereo()

    def _sync_models_to_stereo(self):
        """
        Find the pickable model (the one the user interacts with),
        read its current user matrix, and apply that same matrix
        to all other models. Since all windows share the same model
        actor references, this keeps everything in sync across
        all views.
        """
        # Find the pickable model and get its current user matrix
        pickable_model = None
        for model in self.models:
            if model.get_pickable():
                pickable_model = model
                break

        if pickable_model is None:
            return

        user_matrix = pickable_model.get_user_matrix()
        if user_matrix is None:
            return

        # Apply the same user matrix to all other models
        for model in self.models:
            if model is not pickable_model:
                model.set_user_matrix(user_matrix)

        self.overlay_window.Render()
        self.stereo_window.render()

    @staticmethod
    def _set_actor_matrix(actor, matrix_4x4):
        """
        Set a 4x4 numpy matrix as the user matrix on a VTK actor.
        """
        vtk_matrix = vtk.vtkMatrix4x4()
        for i in range(4):
            for j in range(4):
                vtk_matrix.SetElement(i, j, matrix_4x4[i, j])
        actor.SetUserMatrix(vtk_matrix)

    def set_camera_to_world(self, camera_to_world):
        """
        Set the camera pose for both the interactive overlay window
        and the stereo window. The overlay window uses the left camera
        pose directly. The stereo window uses the left pose and the
        left-to-right extrinsic to derive the right camera pose.

        :param camera_to_world: 4x4 numpy ndarray, left camera to world.
        """
        # Set left camera on overlay
        self.overlay_window.set_camera_pose(camera_to_world)

        # Set stereo cameras using the left-to-right extrinsic
        self.stereo_window.set_poses_from_left_camera(
            camera_to_world, self.left_to_right)

    def set_model_to_world(self, model_to_world):
        """
        Set the model-to-world matrix on all models in
        all windows. This moves all models to the specified pose.

        :param model_to_world: 4x4 numpy ndarray
        """
        vtk_matrix = vtk.vtkMatrix4x4()
        for i in range(4):
            for j in range(4):
                vtk_matrix.SetElement(i, j, model_to_world[i, j])

        for model in self.models:
            model.set_user_matrix(vtk_matrix)

        self.overlay_window.Render()
        self.stereo_window.render()

    def release(self):
        """
        Release video capture resources.
        """
        if self.left_capture is not None:
            self.left_capture.release()
        if self.right_capture is not None:
            self.right_capture.release()


def run_demo(left_intrinsics_file,
             right_intrinsics_file,
             left_to_right_file,
             models_file,
             clipping_range_str,
             left_video,
             right_video,
             model_to_world_file=None,
             camera_to_world_file=None,
             stereo_mode='stacked'):
    """
    Main entry point to run the stereo renderer demo.

    :param left_intrinsics_file: path to left 3x3 intrinsics
    :param right_intrinsics_file: path to right 3x3 intrinsics
    :param left_to_right_file: path to 4x4 left-to-right matrix
    :param models_file: path to models .json config
    :param clipping_range_str: 'near,far' string
    :param left_video: left video source (device int, file, or image)
    :param right_video: right video source (device int, file, or image)
    :param model_to_world_file: optional path to 4x4 model-to-world matrix
    :param camera_to_world_file: optional path to 4x4 camera-to-world matrix
    :param stereo_mode: 'stacked' or 'interlaced'
    """
    app = QApplication([])

    # Parse clipping range
    clip = clipping_range_str.split(',')
    if len(clip) != 2:
        raise ValueError(
            f"Clipping range must be 'near,far', got: {clipping_range_str}")
    clipping_range = (float(clip[0]), float(clip[1]))

    # Load calibration data
    left_intrinsics = np.loadtxt(left_intrinsics_file)
    right_intrinsics = np.loadtxt(right_intrinsics_file)
    left_to_right = np.loadtxt(left_to_right_file)

    # Load models config
    config_manager = cm.ConfigurationManager(models_file)
    models_config = config_manager.get_copy()

    # Load optional initial poses
    model_to_world = None
    if model_to_world_file is not None:
        model_to_world = np.loadtxt(model_to_world_file)

    camera_to_world = None
    if camera_to_world_file is not None:
        camera_to_world = np.loadtxt(camera_to_world_file)

    # Create and start the application
    stereo_app = StereoRendererApp(
        left_intrinsics=left_intrinsics,
        right_intrinsics=right_intrinsics,
        left_to_right=left_to_right,
        models_config=models_config,
        clipping_range=clipping_range,
        left_video_source=left_video,
        right_video_source=right_video,
        model_to_world=model_to_world,
        camera_to_world=camera_to_world,
        stereo_mode=stereo_mode
    )

    stereo_app.start()
    result = app.exec()
    stereo_app.stop()
    stereo_app.release()

    return result
