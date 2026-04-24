# coding=utf-8

"""
Command line entry point for sksurgeryrenderoverlay application.
"""

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgeryrenderoverlay_demo import run_demo


def main(args=None):
    """
    Entry point for sksurgeryrenderoverlay application.
    """
    parser = argparse.ArgumentParser(
        description='sksurgeryrenderoverlay')

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

    parser.add_argument("-c2w", "--camera_to_world_matrix",
                        required=False,
                        type=str,
                        help="File path to camera to world matrix. ")

    parser.add_argument("-w2c", "--world_to_camera_matrix",
                        required=False,
                        type=str,
                        help="File path to world to camera matrix. ")

    parser.add_argument("-r", "--clippingrange",
                        required=False,
                        default="1,1000",
                        type=str,
                        help="near,far")

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
        version='sksurgeryrenderoverlay version '
        + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.models,
             args.background,
             args.intrinsic_matrix,
             args.camera_to_world_matrix,
             args.world_to_camera_matrix,
             args.clippingrange,
             args.output_file)
