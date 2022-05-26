# coding=utf-8

""" CLI for sksurgeryvideocalibration app. """

import argparse
from sksurgerycore.configuration.configuration_manager import \
    ConfigurationManager
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgeryvideocalibration_app import \
    run_video_calibration


def main(args=None):
    """Entry point for sksurgeryvideocalibration. """

    parser = argparse.ArgumentParser(description='sksurgeryvideocalibration')

    parser.add_argument("-c", "--config",
                        required=True,
                        type=str,
                        help="Configuration file containing the parameters "
                             "(see config/video_chessboard_conf.json "
                             "for example).")

    parser.add_argument("-s", "--save",
                        required=False,
                        type=str,
                        help="Directory to save to.")

    parser.add_argument("-p", "--prefix",
                        required=False,
                        type=str,
                        help="Filename prefix to save to.")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgeryvideocalibration version ' + friendly_version_string)

    args = parser.parse_args(args)

    configurer = ConfigurationManager(args.config)
    configuration = configurer.get_copy()

    run_video_calibration(configuration, args.save, args.prefix)
