# coding=utf-8

"""
Command line entry point for sksurgerytransformpolydata application.
"""

import argparse
from sksurgeryutils import __version__
from sksurgeryutils.ui.sksurgerytransformpolydata_demo import run_demo


def main(args=None):
    """
    Entry point for sksurgerytransformpolydata application.
    """
    parser = argparse.ArgumentParser(
        description='sksurgerytransformpolydata')

    parser.add_argument("-i", "--input",
                        required=True,
                        type=str,
                        help='Input polydata file [*.vtk,*.vtp,*.stl,*.ply]')

    parser.add_argument("-o", "--output",
                        required=True,
                        type=str,
                        help="Output polydata file [*.vtk]")

    parser.add_argument("-t", "--transform",
                        required=True,
                        type=str,
                        help="4x4 matrix in numpy format.")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='sksurgerytransformpolydata version '
        + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.input,
             args.output,
             args.transform)
