# coding=utf-8

"""
Command line entry point for sksurgeryrendermodleslikecamera application.
"""

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgeryrendermodelslikecamera_demo import run_demo


def main(args=None):
    """
    Entry point for sksurgeryrendermodleslikecamera application.
    """
    parser = argparse.ArgumentParser(
        description='sksurgeryrendermodleslikecamera')

    parser.add_argument("-m", "--models",
                        required=True,
                        type=str,
                        help='Models .json file.')

    parser.add_argument("-b", "--background",
                        required=True,
                        type=str,
                        help="Background image file name.")

    parser.add_argument("-i", "--intrinsic_matrix",
                        required=True,
                        type=str,
                        help="Intrinsic 3x3 matrix file.")

    parser.add_argument("-w", "--model_to_world",
                        required=False,
                        default="0,0,0,0,0,0",
                        type=str,
                        help="rx,ry,rz,tx,ty,tz in degrees, mm")

    parser.add_argument("-c", "--camera_to_world",
                        required=False,
                        default="0,0,0,0,0,0",
                        type=str,
                        help="rx,ry,rz,tx,ty,tz in degrees, mm")

    parser.add_argument("-l", "--left_to_right",
                        required=False,
                        default="0,0,0,0,0,0",
                        type=str,
                        help="rx,ry,rz,tx,ty,tz in degrees, mm")

    parser.add_argument("-r", "--clippingrange",
                        required=False,
                        default="1,1000",
                        type=str,
                        help="near,far")

    parser.add_argument("-s", "--sigma",
                        required=False,
                        default=0.0,
                        type=float,
                        help="Sigma for Gaussian Blur.")

    parser.add_argument("-o", "--output_file",
                        required=False,
                        default=None,
                        type=str,
                        help="Output file to save image to.")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgeryrendermodleslikecamera version '
        + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.models,
             args.background,
             args.intrinsic_matrix,
             args.model_to_world,
             args.camera_to_world,
             args.left_to_right,
             args.sigma,
             args.clippingrange,
             args.output_file)
