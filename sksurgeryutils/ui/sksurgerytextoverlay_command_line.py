# coding=utf-8

""" Command line processing for charucotest app. """

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgerytextoverlay_demo import run_demo

def main(args=None):
    """Entry point for sksurgerytextoverlay application"""

    parser = argparse.ArgumentParser(description='sksurgerytextoverlay')


    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgerytextoverlay version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_demo()
