# coding=utf-8

"""
Command line entry point for sksurgerystereorenderer application.
"""

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgerystereorenderer_demo import run_demo


def main(args=None):
    """
    Entry point for sksurgerystereorenderer application.
    """
    parser = argparse.ArgumentParser(
        description='sksurgerystereorenderer - Stereo augmented reality '
                    'renderer with interactive model manipulation.')

    parser.add_argument("-li", "--left_intrinsics",
                        required=True,
                        type=str,
                        help="File path to left camera 3x3 intrinsics matrix.")

    parser.add_argument("-ri", "--right_intrinsics",
                        required=True,
                        type=str,
                        help="File path to right camera 3x3 intrinsics matrix.")

    parser.add_argument("-l2r", "--left_to_right",
                        required=True,
                        type=str,
                        help="File path to 4x4 stereo left-to-right "
                             "extrinsic matrix.")

    parser.add_argument("-m", "--models",
                        required=True,
                        type=str,
                        help="Path to models .json configuration file.")

    parser.add_argument("-r", "--clipping_range",
                        required=True,
                        type=str,
                        help="Near,far clipping range (e.g. '1,1000').")

    parser.add_argument("-lv", "--left_video",
                        required=True,
                        type=str,
                        help="Left video source: integer device index, "
                             "video file path, or static image (.png/.jpg).")

    parser.add_argument("-rv", "--right_video",
                        required=True,
                        type=str,
                        help="Right video source: integer device index, "
                             "video file path, or static image (.png/.jpg).")

    parser.add_argument("-m2w", "--model_to_world",
                        required=False,
                        default=None,
                        type=str,
                        help="File path to a 4x4 model-to-world matrix "
                             "applied to all models on startup.")

    parser.add_argument("-c2w", "--camera_to_world",
                        required=False,
                        default=None,
                        type=str,
                        help="File path to a 4x4 camera-to-world matrix "
                             "for the initial camera pose.")

    parser.add_argument("-s", "--stereo_mode",
                        required=False,
                        default="stacked",
                        type=str,
                        choices=["stacked", "interlaced"],
                        help="Stereo display mode: 'stacked' (left=top, "
                             "right=bottom) or 'interlaced'. "
                             "Default: stacked.")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgerystereorenderer version '
        + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.left_intrinsics,
             args.right_intrinsics,
             args.left_to_right,
             args.models,
             args.clipping_range,
             args.left_video,
             args.right_video,
             args.model_to_world,
             args.camera_to_world,
             args.stereo_mode)
