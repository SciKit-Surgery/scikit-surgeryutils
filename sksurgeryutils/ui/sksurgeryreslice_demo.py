""" VTK Reslice widget demo. """
from PySide2 import QtWidgets
from sksurgeryvtk.widgets.vtk_reslice_widget import TrackedSliceViewer, \
     MouseWheelSliceViewer

from sksurgeryarucotracker.arucotracker import ArUcoTracker

def run_demo(tracked, dicom_dir):

    """ Demo """
    app = QtWidgets.QApplication([])

    if tracked:
        tracker = ArUcoTracker({})
        tracker.start_tracking()

        slice_viewer = TrackedSliceViewer(dicom_dir, tracker)

    else:
        slice_viewer = MouseWheelSliceViewer(dicom_dir)

    slice_viewer.start()

    app.exec_()
