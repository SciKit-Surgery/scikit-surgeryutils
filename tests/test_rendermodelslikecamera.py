# coding=utf-8

"""sksurgeryrendermodelslikecamera tests"""

import pytest

@pytest.mark.skip(reason="Need to reimplement")
def test_rendermodelslikecamera(qtbot):
    """ Basic test to run the widget and make sure everything loads OK."""

    test_data = 'tests/data/rendermodels/'
    image = test_data + 'image.png'
    intrinsic = test_data + 'intrinsic.txt'
    extrinsic = test_data + 'extrinsic.txt'
    points = test_data + 'points.txt'
    model_dir = None
    output_file = None

    widget = RenderModelDemoGui(image, model_dir, extrinsic,
                                intrinsic, points, output_file)
    widget.show()

    qtbot.addWidget(widget)
