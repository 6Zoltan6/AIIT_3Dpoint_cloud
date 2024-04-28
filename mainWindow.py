# mainWindow.py

import time
import os
import math
import open3d as o3d
import laspy
import numpy as np
np.set_printoptions(suppress=True)
from scipy.spatial import cKDTree

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# import CSF
import vtkmodules.all
import vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from demo import Ui_MainWindow

""" ---------------------------初始化变量--------------------------------- """

# PARAM_DICT = {}
PARAM_DICT = {'data_tree_all': {},
              'data_subtree_all': {},}
OBJECT_DICT = {}
VIEW_DICT = {}
CURRENT_OBJECT = {}
BOUND_BOX = []
PROPERTY_DICT = {}
check_State = {}
pick_Actor = []

""" ---------------------------主窗口--------------------------------- """

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_ui()
        #111
        self.update_treeWidget(status='init')
        self.update_tableWidget(status='init')
        #
        self.ui.action_open.triggered.connect(self.open_file)
        self.ui.action_open1.triggered.connect(self.open_file)
        #1111

        # self.ui.action_left.triggered.connect(self.leftview_change)
        # self.ui.action_right.triggered.connect(self.rightview_change)
        # self.ui.action_front.triggered.connect(self.frontview_change)
        # self.ui.action_back.triggered.connect(self.backview_change)
        # self.ui.action_above.triggered.connect(self.aboveview_change)
        # self.ui.action_bottom.triggered.connect(self.bottomview_change)
        # self.ui.action_2.triggered.connect(self.save_file)

        #1111
        self.update_listWidget(info='*** 初始化成功 ***')

    def init_ui(self):
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.ui.showlayout.addWidget(self.vtkWidget)
        self.colors = vtk.vtkNamedColors()
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0,191,255)
        self.ren.SetBackground2(0,191,255)
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




    def open_file(self):
        global OBJECT_DICT, PROPERTY_DICT
        path = QFileDialog.getOpenFileNames(self.ui.mainWidget, "打开文件", "", "All Files (*);;"
                                            "PCD Files (*.pcd);;LAS Files (*.las *.laz)")[0]
        if len(path) != 0:
            for i in range(len(path)):
                file = path[i].split('/')[-1]
                file_name = file.split('.')[0]
                if '.pcd' in file:
                    pcd = o3d.io.read_point_cloud(path[i])
                    OBJECT_DICT[file_name] = {'type': 'point'}
                    OBJECT_DICT[file_name]['data'] = np.asarray(pcd.points)
                    self.update_listWidget('读入点云文件：' + path[i])
                    self.update_treeWidget(status='updata', info=file)
                    pcd_color = np.asarray(pcd.colors)
                    if len(pcd_color) == 0 or np.max(pcd_color) == 0:
                        color = 'None'
                        colors = 255 * np.ones((len(pcd.points), 3))
                    else:
                        colors = 255 * np.asarray(pcd.colors)
                        color = 'RGB'
                    PROPERTY_DICT[file_name] = {'Name': file_name, 'Visible': 1, 'Color': color, 'colors': colors,
                                                'Pointnum': len(OBJECT_DICT[file_name]['data']), 'Pointsize': 1}
                    self.show_point(OBJECT_DICT[file_name]['data'], file_name, colors)
                elif ('.las' in file) or ('.laz' in file):
                    las = laspy.read(path[i])
                    point = np.vstack((las.x, las.y, las.z)).transpose()
                    try:
                        rgb_nor = np.vstack((las.red / max(las.red), las.green / max(las.green),
                                             las.blue / max(las.blue))).transpose()
                        rgb = 255 * rgb_nor
                        colors = rgb
                        color = 'RGB'
                    except:
                        color = 'None'
                        colors = 255 * np.ones((point.shape[0], 3))
                    if np.max(colors) == 0:
                        colors = 255 * np.ones((point.shape[0], 3))
                    try:
                        intensity = las.intensity.astype(int)
                        intensity_ = intensity / np.max(intensity) * 255
                        if math.isnan(intensity_[0]):
                            intensity_show = 255 * np.ones((len(intensity), 3))
                        else:
                            intensity_show = np.vstack((intensity_, intensity_, intensity_)).transpose()
                        if color == 'None':
                            color = 'Intensity'
                    except:
                        intensity = None
                        intensity_show = 255 * np.ones((point.shape[0], 3))
                    if color == 'None' or color == 'RGB':
                        self.show_point(point, file_name, colors)
                    elif color == 'Intensity':
                        self.show_point(point, file_name, intensity_show)
                    PROPERTY_DICT[file_name] = {'Name': file_name, 'Visible': 1, 'Color': color, 'colors': colors,
                                                'Pointnum': -1, 'Pointsize': 1, 'intensity': intensity,
                                                'intensity_show': intensity_show, 'None_show':255 * np.ones((point.shape[0], 3))}
                    OBJECT_DICT[file_name] = {'type': 'point'}
                    OBJECT_DICT[file_name]['data'] = point
                    PROPERTY_DICT[file_name]['Pointnum'] = len(point)
                    self.update_listWidget('读入点云文件：' + path[i])
                    self.update_treeWidget(status='updata', info=file)
                elif '.' in file:
                    QMessageBox.warning(self.ui.mainWidget, '警告', '格式暂不支持！')

    def update_listWidget(self, info):
        now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        self.ui.listWidget.addItem('[' + str(now_time) + '] ' + info)
        self.ui.listWidget.setCurrentRow(self.ui.listWidget.count() - 1)

    # 读取后显示函数

    def show_point(self, point, file_name, colors, todo='add'):
        global VIEW_DICT
        if todo == 'replace':
            self.ren.RemoveActor(VIEW_DICT[file_name][0])
        vtk_point = vtk.vtkPoints()
        vtk_point.SetData(numpy_to_vtk(point))
        vtk_polydata = vtk.vtkPolyData()
        vtk_polydata.SetPoints(vtk_point)
        Colors = numpy_to_vtk(colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
        vtk_polydata.GetPointData().SetScalars(Colors)
        vtk_vertex = vtk.vtkVertexGlyphFilter()
        vtk_vertex.SetInputData(vtk_polydata)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(vtk_vertex.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(self.mapper)
        # [actor, vtk_vertex]
        VIEW_DICT[file_name] = [actor, vtk_vertex, vtk_polydata]
        self.ren.AddActor(actor)
        if todo == 'add':
            self.ren.ResetCamera()
        self.renWin.Render()

    def update_treeWidget(self, status, info=None):
        if status == 'init':
            __qtreewidgetitem = QTreeWidgetItem()
            __qtreewidgetitem.setText(0, u"1")
            self.ui.treeWidget.setHeaderItem(__qtreewidgetitem)
            self.ui.treeWidget.setFocusPolicy(Qt.ClickFocus)
            self.ui.treeWidget.header().setVisible(False)
            self.ui.treeWidget.itemClicked.connect(self.check_onClicked)
        elif status == 'updata':
            filename = info
            PARAM_DICT['data_tree_all'][filename] = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            PARAM_DICT['data_tree_all'][filename].setText(0, filename)
            PARAM_DICT['data_tree_all'][filename].setToolTip(0, filename)
            PARAM_DICT['data_tree_all'][filename].setIcon(0, QIcon('./image/导出点云.png'))
            PARAM_DICT['data_tree_all'][filename].setCheckState(0, Qt.Checked)
            check_State[filename] = 2
            PARAM_DICT['data_subtree_all'][filename.split('.')[0]] = [filename, QtWidgets.QTreeWidgetItem(
                PARAM_DICT['data_tree_all'][filename])]
            PARAM_DICT['data_subtree_all'][filename.split('.')[0]][1].setText(0, filename.split('.')[0])
            PARAM_DICT['data_subtree_all'][filename.split('.')[0]][1].setToolTip(0, filename.split('.')[0])
            PARAM_DICT['data_subtree_all'][filename.split('.')[0]][1].setIcon(
                0, QIcon('./image/导出点云.png'))
            PARAM_DICT['data_subtree_all'][filename.split('.')[0]][1].setCheckState(0, Qt.Checked)
            check_State[filename.split('.')[0]] = 2


    # 数据栏点击触发函数
    def check_onClicked(self, item):
        global BOUND_BOX, CURRENT_OBJECT, PROPERTY_DICT, check_State
        parent = item.parent()
        if parent is None:
            if item.checkState(0) == check_State[item.text(0)]:
                pass
            elif item.checkState(0) == 0:
                count = item.childCount()
                for i in range(count):
                    VIEW_DICT[item.child(i).text(0)][0].VisibilityOff()
                    self.renWin.Render()
                    check_State[item.child(i).text(0)] = 0
                check_State[item.text(0)] = 0
            elif item.checkState(0) == 2:
                count = item.childCount()
                for i in range(count):
                    if item.child(i).checkState(0) == 2:
                        VIEW_DICT[item.child(i).text(0)][0].VisibilityOn()
                        self.renWin.Render()
                    check_State[item.child(i).text(0)] = 2
                check_State[item.text(0)] = 2
        else:
            if item.checkState(0) == check_State[item.text(0)]:
                pass
            elif item.checkState(0) == 0:
                VIEW_DICT[item.text(0)][0].VisibilityOff()
                self.renWin.Render()
                check_State[item.text(0)] = 0
            elif item.checkState(0) == 2:
                if parent.checkState(0) == 2:
                    VIEW_DICT[item.text(0)][0].VisibilityOn()
                    self.renWin.Render()
                check_State[item.text(0)] = 2
        try:
            item1 = self.ui.treeWidget.currentItem()
            parent = item1.parent()
        except:
            parent = None
        if parent is None:
            pass
        else:
            if item1.text(0) in CURRENT_OBJECT.keys():
                pass
            else:
                # 赋值current，建立包围盒
                CURRENT_OBJECT = {}
                CURRENT_OBJECT[item1.text(0)] = OBJECT_DICT[item1.text(0)]
                # 清除包围盒
                if BOUND_BOX != []:
                    self.ren.RemoveActor(BOUND_BOX)
                self.show_boundbox(item1.text(0))

                # 更新属性表
                self.update_tableWidget(status='updata', info=item1)


    def update_tableWidget(self, status, info=None):
        if status == 'init':
            self.ui.tableWidget.verticalHeader().setVisible(False)
        elif status == 'updata':
            self.ui.tableWidget.clearContents()
            self.ui.tableWidget.setRowCount(5)

            self.ui.tableWidget.setColumnCount(2)
            self.ui.tableWidget.setHorizontalHeaderLabels(['属性', '值/状态'])
            newItem = QTableWidgetItem('名称')
            newItem.setToolTip(info.text(0))
            self.ui.tableWidget.setItem(0, 0, newItem)
            newItem = QTableWidgetItem('包围盒可见')
            self.ui.tableWidget.setItem(1, 0, newItem)
            newItem = QTableWidgetItem('颜色')
            self.ui.tableWidget.setItem(2, 0, newItem)
            newItem = QTableWidgetItem('点云数量')
            newItem.setToolTip(str(PROPERTY_DICT[info.text(0)]['Pointnum']))
            self.ui.tableWidget.setItem(4, 0, newItem)
            newItem = QTableWidgetItem('点云大小')
            self.ui.tableWidget.setItem(3, 0, newItem)

            self.ui.tableWidget.horizontalHeader().setSectionsClickable(False)
            self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 水平自适应
            self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
            # self.ui.property_Table.resizeColumnsToContents()  # 宽度与内容相适应
            self.ui.tableWidget.resizeRowsToContents()
            newItem = QTableWidgetItem(info.text(0))
            newItem.setToolTip(info.text(0))
            self.ui.tableWidget.setItem(0, 1, newItem)
            self.visible = QCheckBox()
            self.visible.setChecked(False)
            self.visible.setStyleSheet('QCheckBox{margin:3px}')
            self.visible.toggled.connect(self.bound_Visible)
            self.ui.tableWidget.setCellWidget(1, 1, self.visible)
            self.colorCombo = QComboBox()
            self.colorCombo.addItem('RGB', 0)
            # self.colorCombo.addItem('Intensity', 0)
            # self.colorCombo.addItem('None', 0)
            # newItem = QTableWidgetItem(PROPERTY_DICT[info.text(0)]['Color'])
            self.ui.tableWidget.setCellWidget(2, 1, self.colorCombo)
            self.colorCombo.currentIndexChanged.connect(self.colorChange)

            newItem = QTableWidgetItem('%d' % PROPERTY_DICT[info.text(0)]['Pointnum'])
            newItem.setToolTip(str(PROPERTY_DICT[info.text(0)]['Pointnum']))
            self.ui.tableWidget.setItem(4, 1, newItem)
            self.spinwidth = QSpinBox()
            self.spinwidth.setMinimum(1)
            self.spinwidth.setMaximum(10)
            self.spinwidth.setSingleStep(1)
            self.spinwidth.setValue(PROPERTY_DICT[info.text(0)]['Pointsize'])
            self.ui.tableWidget.setCellWidget(3, 1, self.spinwidth)
            self.spinwidth.valueChanged.connect(self.sizechange)
def frontview_change(self):
    focus_point = self.camera.GetFocalPoint()
    dis = self.camera.GetDistance()
    self.camera.SetPosition(focus_point[0], focus_point[1] - dis, focus_point[2])
    self.camera.SetViewUp(0, 0, 1)
    self.renWin.Render()

def backview_change(self):
    focus_point = self.camera.GetFocalPoint()
    dis = self.camera.GetDistance()
    self.camera.SetPosition(focus_point[0], focus_point[1] + dis, focus_point[2])
    self.camera.SetViewUp(0, 0, 1)
    self.renWin.Render()

def leftview_change(self):
    focus_point = self.camera.GetFocalPoint()
    dis = self.camera.GetDistance()
    self.camera.SetPosition(focus_point[0] - dis, focus_point[1], focus_point[2])
    self.camera.SetViewUp(0, 0, 1)
    self.renWin.Render()

def rightview_change(self):
    focus_point = self.camera.GetFocalPoint()
    dis = self.camera.GetDistance()
    self.camera.SetPosition(focus_point[0] + dis, focus_point[1], focus_point[2])
    self.camera.SetViewUp(0, 0, 1)
    self.renWin.Render()

def aboveview_change(self):
    focus_point = self.camera.GetFocalPoint()
    dis = self.camera.GetDistance()
    self.camera.SetPosition(focus_point[0], focus_point[1], focus_point[2] + dis)
    self.camera.SetViewUp(0, 1, 0)
    self.renWin.Render()

def bottomview_change(self):
    focus_point = self.camera.GetFocalPoint()
    dis = self.camera.GetDistance()
    self.camera.SetPosition(focus_point[0], focus_point[1], focus_point[2] - dis)
    self.camera.SetViewUp(0, -1, 0)
    self.renWin.Render()
