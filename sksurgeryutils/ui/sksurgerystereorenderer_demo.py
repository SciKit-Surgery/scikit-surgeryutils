# coding=utf-8

"""
Stereo augmented reality renderer demo application.

Displays 3D models overlaid on stereo video feeds with interactive
manipulation. An interactive VTKOverlayWindow allows the user to
move models, and changes are propagated to a passive
VTKStackedStereoWindow for stereo output.
"""

import logging
import os

import cv2
import numpy as np
import vtk

from PySide6.QtCore import QTimer, Qt
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

    Also overrides left-button-down to find the nearest actor when
    the user clicks on empty space, so that interaction always targets
    the closest visible actor regardless of where the click lands.
    """
    def __init__(self, stereo_render_app):
        super().__init__()

        if stereo_render_app is None:
            raise ValueError("stereo_render_app is None - programming bug.")
        self.stereo_render_app = stereo_render_app

        self.Picker = vtk.vtkCellPicker()
        self.interaction_prop = None

        self.AddObserver("RightButtonPressEvent", self.right_button_press_event)
        self.AddObserver("RightButtonReleaseEvent", self.right_button_release_event)
        self.AddObserver("MouseWheelForwardEvent", self.mouse_wheel_forward_event)
        self.AddObserver("MouseWheelBackwardEvent", self.mouse_wheel_backward_event)
        self.AddObserver("KeyPressEvent", self.key_press_event)

    def OnLeftButtonDown(self):
        """
        Override left-button-down to find the nearest actor when the
        user clicks on empty space. This provides more forgiving
        interaction — wherever you click, the closest actor is selected.
        """
        click_x, click_y = self.GetInteractor().GetEventPosition()
        renderer = self.GetInteractor().FindPokedRenderer(click_x, click_y)
        if not renderer:
            return

        # Try the standard pick first (did they click directly on something?)
        self.Picker.Pick(click_x, click_y, 0, renderer)
        picked_actor = self.Picker.GetActor()

        # If they clicked empty space, find the nearest actor manually
        if not picked_actor:
            picked_actor = self._find_nearest_actor(click_x, click_y, renderer)

        if picked_actor:
            # Track which actor we're interacting with.
            self.interaction_prop = picked_actor

        # Forward the event to the parent class for actual moving/dragging
        super().OnLeftButtonDown()

    def _find_nearest_actor(self, click_x, click_y, renderer):
        """
        Convert click position to world coordinates, evaluate proximity
        to all visible pickable actors, and return the closest one.

        Only actors whose corresponding model is marked pickable in the
        config are considered candidates.

        :param click_x: pixel x coordinate of click
        :param click_y: pixel y coordinate of click
        :param renderer: the vtkRenderer for the clicked viewport
        :returns: the nearest pickable vtkActor, or None
        """
        # Convert pixel coordinates to world coordinates
        renderer.SetDisplayPoint(click_x, click_y, 0)
        renderer.DisplayToWorld()
        world_point = renderer.GetWorldPoint()
        # Strip the homogeneous 'w' coordinate
        click_world = world_point[:3]

        # Build set of actors that are pickable according to the config
        pickable_actors = {
            model.actor for model in self.stereo_render_app.models
            if model.get_pickable()
        }

        actors = renderer.GetActors()
        actors.InitTraversal()

        closest_actor = None
        min_distance = float('inf')

        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if not actor or not actor.GetVisibility():
                continue
            if actor not in pickable_actors:
                continue

            # Calculate distance from click to the centre of the actor's
            # bounding box in world space.
            bounds = actor.GetBounds()
            center_x = (bounds[0] + bounds[1]) / 2.0
            center_y = (bounds[2] + bounds[3]) / 2.0
            center_z = (bounds[4] + bounds[5]) / 2.0
            actor_center = (center_x, center_y, center_z)

            distance = vtk.vtkMath.Distance2BetweenPoints(
                click_world, actor_center)

            if distance < min_distance:
                min_distance = distance
                closest_actor = actor

        return closest_actor

    def right_button_press_event(self, obj, event):
        """
        Process mouse right button press event.

        We do NOT want default scaling behaviour of
        vtkInteractorStyleTrackballActor, so we override it to look
        like a left button press with the control key down (spin).
        """
        del obj, event
        interactor = self.GetInteractor()
        interactor.SetControlKey(True)
        self.OnLeftButtonDown()

    def right_button_release_event(self, obj, event):
        """
        Process mouse right button release event.
        """
        del obj, event
        self.OnLeftButtonUp()
        interactor = self.GetInteractor()
        interactor.SetControlKey(False)

    def mouse_wheel_forward_event(self, obj, event):
        """Move picked actor towards the camera."""
        del obj, event
        self._dolly_actor(-2.0)

    def mouse_wheel_backward_event(self, obj, event):
        """Move picked actor away from the camera."""
        del obj, event
        self._dolly_actor(2.0)

    def key_press_event(self, obj, event):
        """
        Handle key presses. Pressing 't' toggles visibility of all
        models marked as toggleable in the config.
        """
        del obj, event
        key = self.GetInteractor().GetKeySym()
        if key == 't':
            self.stereo_render_app.toggle_toggleable_models()

    def _dolly_actor(self, distance):
        """
        Translate the currently interacted-with actor along the camera
        view direction by the given distance, then sync all models.
        """
        interactor = self.GetInteractor()
        if interactor is None:
            return

        renderer = interactor.FindPokedRenderer(
            interactor.GetEventPosition()[0],
            interactor.GetEventPosition()[1])
        if renderer is None:
            return

        # Use whichever actor is currently being interacted with
        actor = self.interaction_prop
        if actor is None:
            return
        current_m2w = actor.GetMatrix()

        camera = renderer.GetActiveCamera()
        position = camera.GetPosition()
        focal_point = camera.GetFocalPoint()
        diff = np.zeros((3, 1))
        diff[0][0] = focal_point[0] - position[0]
        diff[1][0] = focal_point[1] - position[1]
        diff[2][0] = focal_point[2] - position[2]
        normalised = diff / np.linalg.norm(diff)
        vector_to_move = distance * normalised
        new_m2w = vtk.vtkMatrix4x4()
        new_m2w.DeepCopy(current_m2w)
        new_m2w.SetElement(0, 3, new_m2w.GetElement(0, 3) + vector_to_move[0][0])
        new_m2w.SetElement(1, 3, new_m2w.GetElement(1, 3) + vector_to_move[1][0])
        new_m2w.SetElement(2, 3, new_m2w.GetElement(2, 3) + vector_to_move[2][0])

        actor.PokeMatrix(new_m2w)

        # Sync all models to the new transform
        self.stereo_render_app.sync_all_models_to_actor(actor)


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

    # pylint:disable=too-many-arguments, too-many-branches
    def __init__(self,
                 left_intrinsics,
                 right_intrinsics,
                 left_to_right,
                 models_config,
                 models_dir,
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
        loader = sml.SurfaceModelLoader(models_config, models_dir)
        self.models = list(loader.get_surface_models())
        if len(self.models) == 0:
            raise ValueError("No models found")

        # Determine which models are toggleable from config
        self.toggleable_models = []
        surfaces = models_config.get('surfaces', {})
        for model, (_, surface_cfg) in zip(
                self.models, surfaces.items()):
            if surface_cfg.get('toggleable', False):
                self.toggleable_models.append(model)

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
                clipping_range=self.clipping_range,
            )
        else:
            self.stereo_window = VTKStackedStereoWindow(
                offscreen=False,
                left_camera_matrix=self.left_intrinsics,
                right_camera_matrix=self.right_intrinsics,
                clipping_range=self.clipping_range
            )
        self.stereo_window.add_vtk_models(self.models)

       # Set up the custom interactor on the overlay window
        self.interactor_style = TrackballActorWithZoom(self)
        interactor = self.overlay_window.GetRenderWindow().GetInteractor()
        interactor.SetInteractorStyle(self.interactor_style)

        # Connect interaction end to sync callback
        self.interactor_style.AddObserver(
            "EndInteractionEvent", self._on_interaction_end)
        self.interactor_style.AddObserver(
            "InteractionEvent", self._on_interaction)

        # Create main windows and handle screen placement
        self.primary_main_window = QMainWindow()
        self.primary_main_window.setCentralWidget(self.overlay_window)
        self.primary_main_window.setContentsMargins(0, 0, 0, 0)
        self.primary_main_window.setWindowTitle(
            "Stereo Renderer - Interactive")

        self.secondary_main_window = QMainWindow()
        self.secondary_main_window.setCentralWidget(self.stereo_window)
        self.secondary_main_window.setContentsMargins(0, 0, 0, 0)
        self.secondary_main_window.setWindowTitle(
            "Stereo Renderer - Stereo Output")

        self._setup_screens()

        # Apply initial model-to-world if provided
        if model_to_world is not None:
            self.set_model_to_world(model_to_world)

        # Apply initial camera pose if provided
        self.camera_to_world = None
        if camera_to_world is not None:
            self.set_camera_to_world(camera_to_world)
        else:
            # Or put camera at the origin, looking along z-axis.
            self.set_camera_to_world(np.eye(4))

            # Which means we need to put model in front of camera.
            centroid = self.get_all_pickable_models_centroid()
            m2w = np.eye(4)
            m2w[0][3] = -centroid[0]
            m2w[1][3] = -centroid[1]
            m2w[2][3] = -centroid[2] + 250
            self.set_model_to_world(m2w)

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
            self.primary_main_window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.primary_main_window.showMaximized()
            secondary_geom = secondary_screen.geometry()
            self.secondary_main_window.setGeometry(secondary_geom)
            self.secondary_main_window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
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

        # For now, the camera is at the origin, and we move the model.
        # So, we can also defend against the user interacting with the 3D window.
        self.set_camera_to_world(np.eye(4))

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
        Called during an interaction. Syncs the currently interacted
        actor's model-to-world to all other models.
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
        Read the current transform from whichever actor the user is
        interacting with (interaction_prop), and sync all models.
        """
        interacted_actor = self.interactor_style.interaction_prop
        if interacted_actor is None:
            return
        self.sync_all_models_to_actor(interacted_actor)

    def sync_all_models_to_actor(self, actor):
        """
        Apply the given actor's current matrix to all other models,
        then render both windows.

        :param actor: the vtkActor whose matrix should be propagated
        """
        user_matrix = actor.GetMatrix()
        if user_matrix is None:
            return

        for model in self.models:
            if model.actor is not actor:
                model.actor.PokeMatrix(user_matrix)

        self.overlay_window.Render()
        self.stereo_window.render()

    def toggle_toggleable_models(self):
        """
        Toggle the visibility of all models marked as toggleable
        in the config, then re-render both windows.
        """
        for model in self.toggleable_models:
            model.toggle_visibility()

        self.overlay_window.Render()
        self.stereo_window.render()

    def get_all_pickable_models_centroid(self):
        """
        Returns the average centroid of all pickable models. Used for
        initial camera/model positioning so the whole group is at a
        reasonable distance from the camera.
        """
        centroids = []
        for model in self.models:
            if model.get_pickable():
                centroids.append(model.actor.GetCenter())

        if not centroids:
            raise ValueError("No pickable model. Please edit .json file")

        centroid = np.mean(centroids, axis=0)
        LOGGER.info("Combined centroid is %s", centroid)
        return centroid

    def set_camera_to_world(self, camera_to_world):
        """
        Set the camera pose for both the interactive overlay window
        and the stereo window. The overlay window uses the left camera
        pose directly. The stereo window uses the left pose and the
        left-to-right extrinsic to derive the right camera pose.

        :param camera_to_world: 4x4 numpy ndarray, left camera to world.
        """
        # Set left camera on overlay
        self.camera_to_world = camera_to_world
        self.overlay_window.set_camera_pose(camera_to_world)

        # Set stereo cameras using the left-to-right extrinsic
        self.stereo_window.set_poses_from_left_camera(
            self.camera_to_world, self.left_to_right)

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
            model.actor.PokeMatrix(vtk_matrix)

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
    models_dir = os.path.dirname(models_file)

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
        models_dir=models_dir,
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
