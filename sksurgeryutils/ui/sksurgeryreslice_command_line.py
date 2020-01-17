# coding=utf-8

""" Command line processing for charucotest app. """

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgeryreslice_demo import run_demo

def main(args=None):
    """Entry point for sksurgerytextoverlay application"""

    parser = argparse.ArgumentParser(description='sksurgerytextoverlay')

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgerytextoverlay version ' + friendly_version_string)

    parser.add_argument(
        "-t", "--tracked",
        required=False,
        action="store_true",
        help="Enable tracked demo")

    parser.add_argument(
        "-d", "--dicom_dir",
        required=False,
        default='tests/data/dicom/LegoPhantom_10slices',
        type=str,
        help="DICOM Directory")

    args = parser.parse_args(args)

    run_demo(args.tracked,
             args.dicom_dir)
