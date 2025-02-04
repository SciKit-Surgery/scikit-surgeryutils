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
    description='scikit-surgeryutils - Tests/demos utilities, based around opencv-contrib-python-headless and PySide6',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/SciKit-Surgery/scikit-surgeryutils',
    author='Matt Clarkson',
    author_email='m.clarkson@ucl.ac.uk',
    license='BSD-3 license',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',


        'License :: OSI Approved :: BSD License',


        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',

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
        'numpy<2.0.0',
        'PySide6>=6.5.1.1',
        'opencv-contrib-python-headless>=4.2.0.32',
        'scikit-surgerycore>=0.1.7',
        'scikit-surgeryimage>=0.10.1',
        'scikit-surgeryvtk>=2.2.1',
        'scikit-surgeryarucotracker',
        'scikit-surgerycalibration>=0.2.5'
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
            'sksurgeryvideocalibration=sksurgeryutils.ui.sksurgeryvideocalibration_command_line:main',
            'sksurgeryvideocalibrationchecker=sksurgeryutils.ui.sksurgeryvideocalibrationchecker_command_line:main',
        ],
    },
)
