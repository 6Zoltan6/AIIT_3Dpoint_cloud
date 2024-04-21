# mainWindow.py

import numpy as np
np.set_printoptions(suppress=True)

from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import *

import vtkmodules.all
import vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from demo import Ui_MainWindow


""" ---------------------------初始化变量--------------------------------- """

PARAM_DICT = {}


""" ---------------------------主窗口--------------------------------- """

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.ui.showlayout.addWidget(self.vtkWidget)
        self.colors = vtk.vtkNamedColors()
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0, 0, 0)
        self.ren.SetBackground2(255, 149, 105)
        self.ren.GradientBackgroundOn()
        self.renWin = self.vtkWidget.GetRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.iren = self.renWin.GetInteractor()
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.camera = vtk.vtkCamera()
        self.camera.SetFocalPoint(0, 0, 0)
        self.ren.SetActiveCamera(self.camera)
        self.renWin.Render()
        self.iren.SetInteractorStyle(self.style)
        self.iren.Initialize()
        self.axesActor = vtk.vtkAxesActor()
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()
        self.axes.InteractiveOn()