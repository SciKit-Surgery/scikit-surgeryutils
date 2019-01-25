# coding=utf-8

""" Command line processing for charucotest app. """

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgerycharucotest_demo import run_demo


def main(args=None):
    """Entry point for sksurgerycharucotest application"""

    parser = argparse.ArgumentParser(description='sksurgerycharucotest')

    parser.add_argument("-c", "--camera",
                        required=False,
                        default=0,
                        type=int,
                        help="Camera index.")

    parser.add_argument("-x", "--x_size",
                        required=False,
                        default=640,
                        type=int,
                        help="Image width")

    parser.add_argument("-y", "--y_size",
                        required=False,
                        default=480,
                        type=int,
                        help="Image height")

    parser.add_argument("-i", "--horizontal",
                        required=False,
                        default=10,
                        type=int,
                        help="Number of squares horizontally.")

    parser.add_argument("-j", "--vertical",
                        required=False,
                        default=13,
                        type=int,
                        help="Number of squares vertically.")

    parser.add_argument("-d", "--dictionary",
                        required=False,
                        default=2,
                        type=int,
                        help="ArUco dictionary enum. (see online)")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgerycharucotest version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.camera,
             args.x_size,
             args.y_size,
             args.horizontal,
             args.vertical,
             args.dictionary
             )
