# coding=utf-8

"""Command line processing"""

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgeryrendermodelslikecamera_demo import run_demo


def main(args=None):
    """Entry point for rendermodelslikecamera application"""

    parser = argparse.ArgumentParser(
        description='scikit-surgeryrendermodelslikecamera')

    parser.add_argument("-f", "--image_file",
                        required=True,
                        default=None,
                        type=str,
                        help="Background image")

    parser.add_argument("-m", "--models",
                        required=False,
                        default=None,
                        type=str,
                        help='Models Directory')

    parser.add_argument("-e", "--extrinsic_matrix",
                        required=False,
                        default=None,
                        type=str,
                        help="Camera to world 4x4 matrix file")

    parser.add_argument("-i", "--intrinsic_matrix",
                        required=False,
                        default=None,
                        type=str,
                        help="Intrinsic 3x3 matrix file")

    parser.add_argument("-p", "--points_file",
                        required=False,
                        default=None,
                        type=str,
                        help="File of points to render")

    parser.add_argument("-o", "--output_file",
                        required=False,
                        default=None,
                        type=str,
                        help="Output file name to save image to")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgeryrendermodelslikecamera version '
        + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.image_file,
             args.models,
             args.extrinsic_matrix,
             args.intrinsic_matrix,
             args.points_file,
             args.output_file)
