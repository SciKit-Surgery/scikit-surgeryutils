# -*- coding: utf-8 -*-

""" Command line processing for sksurgerymakecalibrationdots app. """

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgerymakecalibrationdots_demo \
    import make_calibration_dots


def main(args=None):

    """ Entry point for sksurgerymakecalibrationdots application"""

    parser = argparse.ArgumentParser(description='sksurgerymakecalibrationdots')

    parser.add_argument("-xs", "--x_size",
                        required=False,
                        default=2600,
                        type=int,
                        help="Image width in pixels.")

    parser.add_argument("-ys", "--y_size",
                        required=False,
                        default=1900,
                        type=int,
                        help="Image height in pixels.")

    parser.add_argument("-r", "--radius",
                        required=False,
                        default=25,
                        type=int,
                        help="Radius of dots in pixels.")

    parser.add_argument("-sp", "--spacing",
                        required=False,
                        default=100,
                        type=int,
                        help="Spacing of dots in pixels.")

    parser.add_argument("-sc", "--scaling",
                        required=False,
                        default=2,
                        type=int,
                        help="Scale factor for larger dots.")

    parser.add_argument("-f", "--fraction",
                        required=False,
                        default=0.375,
                        type=int,
                        help="Fraction of image to left/top of first big dot.")

    parser.add_argument("-xd", "--x_dots",
                        required=False,
                        default=25,
                        type=int,
                        help="Number of dots in x directio.")

    parser.add_argument("-yd", "--y_dots",
                        required=False,
                        default=18,
                        type=int,
                        help="Number of dots in y direction.")

    parser.add_argument("-o", "--output_file",
                        required=True,
                        default=None,
                        type=str,
                        help="Output file to save image to.")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgerymakecalibrationdots version ' \
                + friendly_version_string)

    args = parser.parse_args(args)

    make_calibration_dots(args.x_size,
                          args.y_size,
                          args.radius,
                          args.spacing,
                          args.scaling,
                          args.fraction,
                          args.x_dots,
                          args.y_dots,
                          args.output_file
                          )
