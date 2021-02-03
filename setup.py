# coding=utf-8
"""
Setup for scikit-surgeryutils
"""

from setuptools import setup, find_packages
import versioneer

# Get the long description
with open('README.rst') as f:
    long_description = f.read()

setup(
    name='scikit-surgeryutils',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='scikit-surgeryutils - Tests/demos utilities, based around opencv-contrib and PySide2',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/UCL/scikit-surgeryutils',
    author='Matt Clarkson',
    author_email='m.clarkson@ucl.ac.uk',
    license='BSD-3 license',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',


        'License :: OSI Approved :: BSD License',


        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',

        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    keywords='medical imaging',

    packages=find_packages(
        exclude=[
            'doc',
            'tests',
        ]
    ),

    install_requires=[
        'six>=1.10',
        'numpy>=1.11',
        'opencv-contrib-python>=4.1.1.26',
        'PySide2<5.15.0',
        'scikit-surgerycore>=0.1.7',
        'scikit-surgeryimage>=0.2.0',
        'scikit-surgeryvtk>=0.19.1',
        'scikit-surgeryarucotracker>=0.0.4'

    ],

    entry_points={
        'console_scripts': [
            'sksurgeryvideolag=sksurgeryutils.ui.sksurgeryvideolag_command_line:main',
            'sksurgerycharucotest=sksurgeryutils.ui.sksurgerycharucotest_command_line:main',
            'sksurgeryrendermodelslikecamera=sksurgeryutils.ui.sksurgeryrendermodelslikecamera_command_line:main',
            'sksurgerymakecalibrationdots=sksurgeryutils.ui.sksurgerymakecalibrationdots_command_line:main',
            'sksurgeryreslice=sksurgeryutils.ui.sksurgeryreslice_command_line:main',
            'sksurgerytextoverlay=sksurgeryutils.ui.sksurgerytextoverlay_command_line:main',
            'sksurgerytransformpolydata=sksurgeryutils.ui.sksurgeryrendermodelslikecamera_command_line:main',
        ],
    },
)
