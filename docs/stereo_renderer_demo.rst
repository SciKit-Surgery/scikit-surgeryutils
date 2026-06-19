Stereo Renderer Demo
^^^^^^^^^^^^^^^^^^^^

Features

- Loads left intrinsics, right intrinsics, left-to-right extrinsics
- Loads a set of models, using a single .json file
- Plays video, or loads a single static image
- Overlays models on top of video
- Creates 2 windows.
 - One for interacting
 - One for a stereo display, either interlaced or stacked
- Allows interacting with models, changing the model-to-world transform
- Camera defaults to origin

Usage
^^^^^

Create .json descriptor
-----------------------

A set of models (.vtk, .vtp, .stl, .ply) can be loaded.
Rather than have many command line args, we use a .json file.
The format is::

    {
        "surfaces": {
            "kidney": {
                "file": "kidney.vtk",
                "colour": [213, 142, 119],
                "opacity": 0.5,
                "visibility": true,
                "pickable": true
            },
            "artery": {
                "file": "artery.vtk",
                "colour": [203, 81, 54],
                "opacity": 0.5,
                "visibility": true,
                "pickable": false
            },
            "cyst": {
                "file": "cyst.vtk",
                "colour": [144, 221, 157],
                "opacity": 0.5,
                "visibility": true,
                "pickable": false
            },
            "renalsinusfat": {
                "file": "renalSinusFat.vtk",
                "colour": [161, 115, 220],
                "opacity": 0.5,
                "visibility": true,
                "pickable": false
            },
            "vein": {
                "file": "vein.vtk",
                "colour": [54, 109, 188],
                "opacity": 0.5,
                "visibility": true,
                "pickable": false
            }
        }
    }

Note: There should only ever be 1 "pickable" object.
The pickable object is the one you interact with.

You can set colour ``[R, G, B]``, opacity ``[0, 1]`` and visibility ``[true|false]``, as shown above.

Calibration Files
-----------------

Camera calibration files should be plain text, ASCII files, as would
be compatible with ``numpy.loadtxt(filename)``.

- Intrinsics: [3x3]
- Stereo extrinsics: [4x4]

Note: We do not load distortion parameters. Therefore, video must be undistorted.


Usage
-----

If you have ``pip install``-ed the whole package, you can see the usage message by
running the ``sksurgerystereorenderer`` entry point with ``-h``.

For example::

    promt% sksurgerystereorenderer -h
    usage: sksurgerystereorenderer [-h] -li LEFT_INTRINSICS -ri RIGHT_INTRINSICS -l2r LEFT_TO_RIGHT -m MODELS -r CLIPPING_RANGE -lv LEFT_VIDEO -rv RIGHT_VIDEO [-m2w MODEL_TO_WORLD] [-c2w CAMERA_TO_WORLD]
                                   [-s {stacked,interlaced}] [-v]

    sksurgerystereorenderer - Stereo augmented reality renderer with interactive model manipulation.

    options:
      -h, --help            show this help message and exit
      -li, --left_intrinsics LEFT_INTRINSICS
                            File path to left camera 3x3 intrinsics matrix.
      -ri, --right_intrinsics RIGHT_INTRINSICS
                            File path to right camera 3x3 intrinsics matrix.
      -l2r, --left_to_right LEFT_TO_RIGHT
                            File path to 4x4 stereo left-to-right extrinsic matrix.
      -m, --models MODELS   Path to models .json configuration file.
      -r, --clipping_range CLIPPING_RANGE
                            Near,far clipping range (e.g. '1,1000').
      -lv, --left_video LEFT_VIDEO
                            Left video source: integer device index, video file path, or static image (.png/.jpg).
      -rv, --right_video RIGHT_VIDEO
                            Right video source: integer device index, video file path, or static image (.png/.jpg).
      -m2w, --model_to_world MODEL_TO_WORLD
                            File path to a 4x4 model-to-world matrix applied to all models on startup.
      -c2w, --camera_to_world CAMERA_TO_WORLD
                            File path to a 4x4 camera-to-world matrix for the initial camera pose.
      -s, --stereo_mode {stacked,interlaced}
                            Stereo display mode: 'stacked' (left=top, right=bottom) or 'interlaced'. Default: stacked.
      -v, --version         show program's version number and exit

Alternatively, if you are running a development environment::

    prompt% source .tox/test/bin/activate
    prompt% python sksurgerystereorenderer.py -h

gives the same output as the above help message.

An example would be::

    prompt% source .tox/test/bin/activate
    prompt% python sksurgerystereorenderer.py \
      -m patient.json \
      -li davinci_intrinsics_undistorted.txt \
      -ri davinci_intrinsics_undistorted.txt \
      -l2r left_to_right.txt \
      -lv leftVideo_undistorted.avi \
      -rv rightVideo_undistorted.avi \
      -r 1,1000

Screens
-------

The app can make use of a 2-monitor setup.

- If you have 2 monitors, the primary (e.g. laptop) shows a window for interacting, and the secondary (e.g. external 3D monitor) shows the stereo display. Both maximised.
- If you have 1 monitor, both windows appear on the same monitor, both unmaximised.


Interation Controls
-------------------

Similar to standard VTK controls, and you need a 3-button mouse.

- Left button and move left-right: Rotate about centroid, left-right
- Left button and move up-down: Rotate about centroid, up-down
- Scroll wheel: Zoom in/out, by moving the model towards/away from camera
- Right button and move: spin about forward axis
- Middle button and move: pan (i.e. translation)