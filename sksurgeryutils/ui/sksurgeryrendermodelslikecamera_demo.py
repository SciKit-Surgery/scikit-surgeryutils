# coding=utf-8

""" Demo app, to render a model from a particular perspective"""
import sys
import cv2

# pylint: disable=import-error

import numpy as np
from PySide2 import QtWidgets
from sksurgeryvtk.widgets import vtk_overlay_window
from sksurgeryvtk.models import vtk_surface_model_directory_loader
from sksurgeryvtk.models import vtk_point_model


def run_demo(image_file, model_dir, extrinsics_file,
             intrinsics_file, points_file, output_file):
    """ Demo app, to render an image using a calibrated camera. """
    app = QtWidgets.QApplication([])

    vtk_widget = vtk_overlay_window.VTKOverlayWindow()

    # Set the video image on the widget.
    img = cv2.imread(image_file)
    vtk_widget.set_video_image(img)

    layout = QtWidgets.QVBoxLayout()
    layout.setSpacing(0)
    layout.setMargin(0)
    layout.addWidget(vtk_widget)

    window = QtWidgets.QWidget()
    window.resize(img.shape[1], img.shape[0])
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

        intrinsics = np.loadtxt(intrinsics_file, dtype=np.float)
        extrinsics = np.loadtxt(extrinsics_file)

        vtk_widget.set_camera_matrix(intrinsics)
        vtk_widget.set_camera_pose(extrinsics)

    if output_file:
        vtk_widget.save_scene_to_file(output_file)
        return 0

    return sys.exit(app.exec_())
