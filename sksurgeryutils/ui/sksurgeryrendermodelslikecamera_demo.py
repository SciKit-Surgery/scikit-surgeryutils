# coding=utf-8

""" Demo app, to render a model from a particular perspective"""
import sys
import cv2

# pylint: disable=import-error

import numpy as np
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from sksurgeryvtk.widgets import vtk_overlay_window
from sksurgeryvtk.models import vtk_surface_model_directory_loader
from sksurgeryvtk.models import vtk_point_model
import sksurgeryvtk.camera.vtk_camera_model as cam


def run_demo(image_file, model_dir, extrinsics_file,
             intrinsics_file, points_file):
    """ Demo app, to render an image using a calibrated camera. """
    app = QtWidgets.QApplication([])

    img = cv2.imread(image_file)
    vtk_widget = vtk_overlay_window.VTKOverlayWindow()
    vtk_widget.set_video_image(img)

    # Use a QLayout to maintain corret aspect ratio of the vtk widget
    # Important: the '0, Qt.AlignCenter' arguments in addWidget are
    #  needed for correct scaling.
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(vtk_widget, 0, Qt.AlignCenter)

    window = QtWidgets.QWidget()
    window.setLayout(layout)
    window.show()

    if points_file:
        points = np.loadtxt(points_file)
        vtk_points = vtk_point_model.VTKPointModel(points.astype(np.float),
                                                   points.astype(np.byte))
        vtk_widget.add_vtk_actor(vtk_points.actor)

    if model_dir:
        model_loader = vtk_surface_model_directory_loader. \
            VTKSurfaceModelDirectoryLoader(model_dir)
        vtk_widget.add_vtk_models(model_loader.models)

    if extrinsics_file and intrinsics_file:

        # Load intrinsics for projection matrix.
        intrinsics = np.loadtxt(intrinsics_file, dtype=np.float)

        # Load extrinsics for camera pose (position, orientation).
        extrinsics = np.loadtxt(extrinsics_file)
        model_to_camera = cam.create_vtk_matrix_from_numpy(extrinsics)

        # OpenCV maps from model to camera.
        # Assume model == world, so the input matrix is world_to_camera.
        # We need camera_to_world to position the camera in world coordinates.
        # So, invert it.
        model_to_camera.Invert()

        height, width = img.shape[:2]
        projection_matrix = cam.compute_projection_matrix(width, height,
                                                          intrinsics[0][0],
                                                          intrinsics[1][1],
                                                          intrinsics[0][2],
                                                          intrinsics[1][2],
                                                          0.01, 1000,
                                                          1
                                                          )
        camera = vtk_widget.get_foreground_camera()
        cam.set_camera_pose(camera, model_to_camera)
        cam.set_projection_matrix(camera, projection_matrix)

    return sys.exit(app.exec_())
