# coding=utf-8

""" Command line processing for videolag app. """

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgeryvideolag_demo import run_demo


def main(args=None):
    """Entry point for sksurgeryvideolag application"""

    default_camera_interval = 33
    default_screen_interval = 15

    parser = argparse.ArgumentParser(description='sksurgeryvideolag')

    parser.add_argument("-c", "--camera",
                        required=False,
                        default=0,
                        type=int,
                        help="Camera index")

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

    parser.add_argument("-g", "--grab",
                        required=False,
                        default=default_camera_interval,
                        type=int,
                        help="Time interval for camera grab (ms) ["
                        + str(default_camera_interval) + " ms]")

    parser.add_argument("-m", "--milliseconds",
                        required=False,
                        default=default_screen_interval,
                        type=int,
                        help="Time interval for screen update (ms) ["
                        + str(default_screen_interval) + " ms]")

    parser.add_argument("-f", "--fullscreen",
                        required=False,
                        default=False,
                        type=bool,
                        help="Full screen")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgeryvideolag version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.camera,
             args.x_size,
             args.y_size,
             args.grab,
             args.milliseconds,
             args.fullscreen)
