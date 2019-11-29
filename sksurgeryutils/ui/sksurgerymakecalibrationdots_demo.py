# -*- coding: utf-8 -*-

""" Function to implement the drawing of a calibration pattern of dots. """

import cv2
import numpy as np


def make_calibration_dots(width,
                          height,
                          radius,
                          spacing,
                          x_dots,
                          y_dots,
                          output_file
                          ):
    """
    Function that makes a calibration pattern of dots.

    :param width: horizontal size of output image in pixels
    :param height: vertical size of output image in pixels
    :param radius: radius of dots in pixels
    :param spacing: spacing of dots in pixels
    :param x_dots: number of dots in x
    :param y_dots: number of dots in y
    :param output_file: output file
    """

    centre_x = (width - 1)/2.0
    centre_y = (height - 1) / 2.0
    half_width = (spacing * (x_dots - 1))/2.0
    half_height = (spacing * (y_dots - 1))/2.0

    image = 255 * np.ones(shape=[height, width], dtype=np.uint8)

    one_third_x = (x_dots // 3) - 1
    one_third_y = (y_dots // 3) - 1
    two_third_x = (x_dots - 1) - one_third_x
    two_third_y = (y_dots - 1) - one_third_y

    for y_index in range(y_dots):
        for x_index in range(x_dots):
            dot_x = int(centre_x + (x_index * spacing) - half_width)
            dot_y = int(centre_y + (y_index * spacing) - half_height)

            rad = radius
            big = 2 * rad

            if x_index == one_third_x and y_index == one_third_y:
                rad = big
            if x_index == one_third_x and y_index == two_third_y:
                rad = big
            if x_index == two_third_x and y_index == two_third_y:
                rad = big
            if x_index == two_third_x and y_index == one_third_y:
                rad = big

            cv2.circle(image, (dot_x, dot_y), rad, (0, 0, 0), thickness=-1)

    cv2.imwrite(output_file, image)
