# coding=utf-8

"""
App to transform a poly data by a 4x4 matrix.
"""

import numpy as np
import vtk
import sksurgeryvtk.utils.matrix_utils as mu
import sksurgeryvtk.models.vtk_surface_model as sm

#pylint:disable=no-member

def run_demo(input_file,
             output_file,
             transform_file):
    """
    Takes a poly data input, transforms it by a 4x4 matrix, writes output.

    :param input_file: Input poly data as .vtk, .vtp, .stl or .ply file.
    :param output_file: Output poly data as .vtk file.
    :param transform_file: 4x4 matrix in plain text (e.g. numpy.savetxt) format.
    :return:
    """
    if not output_file.endswith('.vtk'):
        raise ValueError('Currently, only .vtk outputs are supported.')

    model = sm.VTKSurfaceModel(input_file,
                               colour=[1.0, 1.0, 1.0],
                               visibility=True)

    matrix = np.loadtxt(transform_file)
    transform = mu.create_vtk_matrix_from_numpy(matrix)
    model.set_model_transform(transform)

    # this line can go, when scikit-surgeryvtk updates to 0.22.0
    model.transform_filter.Update()

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(model.transform_filter.GetOutput())
    writer.Write()
