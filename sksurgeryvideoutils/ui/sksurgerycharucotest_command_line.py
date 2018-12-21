# coding=utf-8

""" Command line processing for charucotest app. """

import argparse
from sksurgeryvideoutils import __version__
from sksurgeryvideoutils.ui.sksurgerycharucotest_demo import run_charucotest_demo


def main(args=None):
    """Entry point for sksurgerycharucotest application"""

    parser = argparse.ArgumentParser(description='sksurgerycharucotest')

    parser.add_argument("-c", "--camera",
                        required=False,
                        default=0,
                        type=int,
                        help="Camera index.")

    parser.add_argument("-x", "--x_squares",
                        required=False,
                        default=13,
                        type=int,
                        help="Number of squares in X direction.")

    parser.add_argument("-y", "--y_squares",
                        required=False,
                        default=10,
                        type=int,
                        help="Number of squares in Y direction.")

    parser.add_argument("-d", "--dictionary",
                        required=True,
                        type=str,
                        help="String describing aruco dictionary.")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgerycharucotest version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_charucotest_demo(args.camera,
                         args.x_squares,
                         args.y_squares,
                         args.dictionary
                         )
