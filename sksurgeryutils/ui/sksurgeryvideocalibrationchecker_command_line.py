# coding=utf-8

""" CLI for sksurgeryvideocalibrationchecker. """

import argparse

from sksurgerycore.configuration.configuration_manager import \
        ConfigurationManager
from sksurgerycalibration import __version__
from sksurgeryutils.ui.sksurgeryvideocalibrationchecker_app \
    import run_video_calibration_checker


def main(args=None):

    """ Entry point for sksurgeryvideocalibrationchecker application. """

    parser = argparse.ArgumentParser(
        description='sksurgeryvideocalibrationchecker')

    parser.add_argument("-c", "--config",
                        required=True,
                        type=str,
                        help="Configuration file containing the parameters.")

    parser.add_argument("-d", "--calib_dir",
                        required=True,
                        type=str,
                        help="Directory containing calibration data.")

    parser.add_argument("-p", "--prefix",
                        required=True,
                        type=str,
                        help="Prefix for calibration data.")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "--version",
        action='version',
        version='scikit-sksurgeryvideocalibrationchecker version '
                + friendly_version_string)

    args = parser.parse_args(args)

    configurer = ConfigurationManager(args.config)
    configuration = configurer.get_copy()

    run_video_calibration_checker(configuration, args.calib_dir, args.prefix)
