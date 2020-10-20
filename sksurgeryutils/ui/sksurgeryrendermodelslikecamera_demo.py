# coding=utf-8

"""
App to render a set of models using a calibrated camera.
"""

import sys
import cv2
from PySide2 import QtWidgets
import sksurgeryvtk.widgets.vtk_rendering_generator as rg


def split_string(param_string):
    """
    Splits a comma separated list of rx,ry,rz,tx,ty,tz to a list of floats.
    :param param_string: string
    :return: list of float
    """
    result = [0, 0, 0, 0, 0, 0]
    if param_string is not None:
        split = param_string.split(',')
        if len(split) != 6:
            raise ValueError('List is wrong length:' + str(split))
        for i in range(6):
            result[i] = float(split[i])
    return result


def run_demo(models_file,
             background_image,
             intrinsic_file,
             model_to_world,
             camera_to_world,
             left_to_right,
             sigma,
             clippingrange,
             output_file):

    """ Demo app, to render a set of models using a calibrated camera. """
    app = QtWidgets.QApplication([])

    m2w = split_string(model_to_world)
    c2w = split_string(camera_to_world)
    l2r = split_string(left_to_right)
    clip = clippingrange.split(',')
    if len(clip) != 2:
        raise ValueError("Clipping range not valid:" + str(clip))

    gen = rg.VTKRenderingGenerator(models_file,
                                   background_image,
                                   intrinsic_file,
                                   c2w,
                                   l2r,
                                   sigma
                                   )

    gen.set_all_model_to_world(m2w)
    gen.set_clipping_range(float(clip[0]), float(clip[1]))
    gen.show()

    img = gen.get_image()
    if output_file:
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_file, bgr)
    else:
        sys.exit(app.exec_())

    return 0
