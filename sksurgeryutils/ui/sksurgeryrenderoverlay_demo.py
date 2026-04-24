# coding=utf-8

"""
App to render a set of models using a calibrated camera.
"""

import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication

import sksurgerycore.configuration.configuration_manager as cm
import sksurgeryvtk.widgets.vtk_overlay_window as ovw
import sksurgeryvtk.models.surface_model_loader as sml

# pylint: disable=too-many-positional-arguments, invalid-name

def orthogonalize_4x4(matrix):
    """
    Orthogonalizes the upper-left 3x3 rotation component of a 4x4 matrix
    using Singular Value Decomposition (SVD).
    """
    # 1. Extract the 3x3 rotation submatrix
    r = matrix[:3, :3]

    # 2. Perform Singular Value Decomposition
    # R = U * np.diag(S) * Vt
    u, _, vt = np.linalg.svd(r)

    # 3. Compute the nearest orthogonal matrix
    # The 'closest' rotation matrix is simply U * Vt
    r_ortho = np.dot(u, vt)

    # 4. Handle the "Reflection" case
    # If the determinant is -1, we have a reflection.
    # We force a pure rotation by flipping the sign of the last column of U.
    if np.linalg.det(r_ortho) < 0:
        u[:, -1] *= -1
        r_ortho = np.dot(u, vt)

    # 5. Reassemble the 4x4 matrix
    new_matrix = matrix.copy()
    new_matrix[:3, :3] = r_ortho

    return new_matrix


def run_demo(models_file,
             background_image,
             intrinsic_file,
             camera_to_world_matrix,
             world_to_camera_matrix,
             clippingrange,
             output_file):

    """ Demo app, to render a set of models using a calibrated camera. """
    app = QApplication([])

    clip = clippingrange.split(',')
    if len(clip) != 2:
        raise ValueError("Clipping range not valid:" + str(clip))

    c2w = np.eye(4)
    if camera_to_world_matrix and len(camera_to_world_matrix) > 0:
        c2w = np.loadtxt(camera_to_world_matrix)
    if world_to_camera_matrix and len(world_to_camera_matrix) > 0:
        w2c = np.loadtxt(world_to_camera_matrix)
        c2w = np.linalg.inv(w2c)
    c2w = orthogonalize_4x4(c2w)

    # Loading reference data.
    intrinsic_matrix = np.loadtxt(intrinsic_file)
    bg_image = cv2.imread(background_image)

    # Use a SurfaceModelLoader. This means we can give a
    # .json config file of lots of models, all with different colours.
    config_manager = cm.ConfigurationManager(models_file)
    config = config_manager.get_copy()
    loader = sml.SurfaceModelLoader(config)
    models = loader.get_surface_models()

    # Using VTKOverlayWindow directly, so we can just set matrix.
    widget = ovw.VTKOverlayWindow(offscreen=False,
                                  camera_matrix=intrinsic_matrix,
                                  clipping_range=(float(clip[0]),
                                                  float(clip[1])),
                                  )
    widget.show()
    widget.resize(bg_image.shape[1], bg_image.shape[0])
    widget.add_vtk_models(models)
    widget.set_video_image(bg_image)
    widget.set_camera_matrix(intrinsic_matrix)
    widget.set_camera_pose(c2w)
    widget.repaint()
    img = widget.convert_scene_to_numpy_array()

    if output_file:
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_file, bgr)
    else:
        sys.exit(app.exec_())

    return 0
