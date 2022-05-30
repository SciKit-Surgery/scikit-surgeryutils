# coding=utf-8

""" CLI for sksurgeryvideocalibrationchecker app. """
import argparse
from sksurgerycore.configuration.configuration_manager import \
    ConfigurationManager
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgeryvideocalibrationchecker_app import \
    run_video_calibration_checker


def main(args=None):
    """ Entry point for sksurgeryvideocalibrationchecker. """

    parser = argparse.ArgumentParser(
        description='sksurgeryvideocalibrationchecker')

    parser.add_argument("-c", "--config",
                        required=True,
                        type=str,
                        help="Configuration file containing the parameters "
                             "(see config/video_chessboard_conf.json "
                             "for example).")

    parser.add_argument("-s", "--source",
                        required=False,
                        type=str,
                        default="0",
                        help="OpenCV source. (USB camera number, or filename).")

    parser.add_argument("-d", "--calib_dir",
                        required=True,
                        type=str,
                        help="Directory containing calibration data.")

    parser.add_argument("-p", "--prefix",
                        required=False,
                        type=str,
                        help="Prefix for calibration data.")

    parser.add_argument("-ni", "--noninteractive",
                        required=False,
                        action='store_true',
                        help="If specified, runs noninteractive mode.")

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

    run_video_calibration_checker(configuration,
                                  args.source,
                                  args.calib_dir,
                                  args.prefix,
                                  args.noninteractive
                                  )
