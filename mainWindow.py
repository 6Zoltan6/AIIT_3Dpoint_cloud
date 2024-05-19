# mainWindow.py

import time
import os
import math
import open3d as o3d
import laspy
import numpy as np
from jedi.api import file_name

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
        self.grabKeyboard()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.gridLayout = QtWidgets.QGridLayout(self.ui.mainWidget)
        self.init_ui()

        self.update_treeWidget(status='init')
        self.update_tableWidget(status='init')



        self.ui.action_open.triggered.connect(self.open_file)
        self.ui.action_open1.triggered.connect(self.open_file)
        self.ui.action_left.triggered.connect(self.leftview_change)
        self.ui.action_right.triggered.connect(self.rightview_change)
        self.ui.action_front.triggered.connect(self.frontview_change)
        self.ui.action_back.triggered.connect(self.backview_change)
        self.ui.action_above.triggered.connect(self.aboveview_change)
        self.ui.action_bottom.triggered.connect(self.bottomview_change)

        self.ui.action_4.triggered.connect(self.close)
        self.ui.action_15.triggered.connect(self.change_point_color)
        self.ui.action_29.triggered.connect(self.change_background_color)

        ##颜色
        self.ui.action_15.triggered.connect(self.change_point_color)
        ##背景板
        self.ui.action_29.triggered.connect(self.change_background_color)
####点云拾取
        self.ui.action_25.triggered.connect(self.pickpointFrame.activate)
        #####列表展示
        self.pointlstFrame = Pointlst_Frame(self, pick_Actor, self.ren, self.iren, self.renWin, self.camera,
                                            self.ui.listWidget)

        ####高程着色
        self.ui.action_16.triggered.connect(self.height_color)

        # 绑定按键

        self.ui.action_50.triggered.connect(self.intensity_color)

        self.ui.action_11.triggered.connect(self.merge)
#############
        # 绑定函数
        self.ui.action_2.triggered.connect(self.save_file)
        self.ui.action_50.triggered.connect(self.intensity_color)
        self.ui.action_11.triggered.connect(self.merge)
        self.update_listWidget(info='*** 初始化成功 ***')

        #####点云拾取列表
        self.ui.action_26.triggered.connect(self.pointlstFrame.activate)


    def init_ui(self):
        self.vtkWidget = QVTKRenderWindowInteractor()
        self.ui.showlayout.addWidget(self.vtkWidget, 1)
        self.colors = vtk.vtkNamedColors()
        self.ren = vtk.vtkRenderer()  # 场景渲染
        self.ren.SetBackground(0, 0, 0)  # 页面底部颜色
        self.ren.SetBackground2(255, 149, 105)  # 页面顶部颜色
        self.ren.GradientBackgroundOn()  # 开启渐变背景
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
##########拾取点云
        self.pickpointFrame = Pick_Point_Frame(self, pick_Actor, self.ren, self.iren, self.renWin, self.camera,
                                               self.ui.listWidget)


    def update_treeWidget(self, status, info=None):
        if status == 'init':
            __qtreewidgetitem = QTreeWidgetItem()
            __qtreewidgetitem.setText(0, u"1")
            self.ui.treeWidget.setHeaderItem(__qtreewidgetitem)
            self.ui.treeWidget.setFocusPolicy(Qt.ClickFocus)
            self.ui.treeWidget.header().setVisible(False)
            self.ui.treeWidget.itemClicked.connect(self.check_onClicked)
            self.ui.treeWidget.setSelectionMode(QTreeWidget.ExtendedSelection)
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
        elif status == 'addsub':
            PARAM_DICT['data_subtree_all'][info[1]] = [info[0], QtWidgets.QTreeWidgetItem(
                PARAM_DICT['data_tree_all'][info[0]])]
            PARAM_DICT['data_subtree_all'][info[1]][1].setText(0, info[1])
            PARAM_DICT['data_subtree_all'][info[1]][1].setToolTip(0, info[1])
            PARAM_DICT['data_subtree_all'][info[1]][1].setIcon(0, QIcon('./image/导出点云.png'))
            PARAM_DICT['data_subtree_all'][info[1]][1].setCheckState(0, Qt.Checked)
            check_State[info[1]] = 2
        elif status == 'delete':
            item = info[1]
            parent = item.parent()
            parent.removeChild(item)
            if parent.childCount() == 0:
                rootIndex = self.ui.treeWidget.indexOfTopLevelItem(parent)
                self.ui.treeWidget.takeTopLevelItem(rootIndex)

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


    # 点击数据触发显示包围盒函数
    def show_boundbox(self, file_name):
        global BOUND_BOX
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(VIEW_DICT[file_name][1].GetOutputPort())
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outline.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(self.colors.GetColor3d('Gold'))
        BOUND_BOX = actor
        self.ren.AddActor(actor)
        BOUND_BOX.VisibilityOff()
        self.renWin.Render()

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

    # 属性栏触发包围盒是否可视函数
    def bound_Visible(self, state):
        global BOUND_BOX
        if state:
            BOUND_BOX.VisibilityOn()
            self.renWin.Render()
        else:
            BOUND_BOX.VisibilityOff()
            self.renWin.Render()

    # 属性栏触发点云大小变化函数
    def sizechange(self):
        global VIEW_DICT, PROPERTY_DICT
        size = int(self.spinwidth.value())
        try:
            item1 = self.ui.treeWidget.currentItem()
            actor = VIEW_DICT[item1.text(0)][0]
            actor.GetProperty().SetPointSize(size)
            VIEW_DICT[item1.text(0)][0] = actor
            self.renWin.Render()
            PROPERTY_DICT[item1.text(0)]['Pointsize'] = size
        except:
            pass

    # 属性栏触发颜色显示函数
    def colorChange(self):
        index = self.colorCombo.currentIndex()
        text = self.colorCombo.itemText(index)
        if text == 'RGB':
            self.show_point(OBJECT_DICT[list(CURRENT_OBJECT.keys())[0]]['data'], list(CURRENT_OBJECT.keys())[0],
                            PROPERTY_DICT[list(CURRENT_OBJECT.keys())[0]]['colors'], todo='replace')
        elif text == 'Intensity':
            self.show_point(OBJECT_DICT[list(CURRENT_OBJECT.keys())[0]]['data'], list(CURRENT_OBJECT.keys())[0],
                            PROPERTY_DICT[list(CURRENT_OBJECT.keys())[0]]['intensity_show'], todo='replace')
        else:
            self.show_point(OBJECT_DICT[list(CURRENT_OBJECT.keys())[0]]['data'], list(CURRENT_OBJECT.keys())[0],
                            PROPERTY_DICT[list(CURRENT_OBJECT.keys())[0]]['None_show'], todo='replace')

    def update_listWidget(self, info):
        now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        self.ui.listWidget.addItem('[' + str(now_time) + '] ' + info)
        self.ui.listWidget.setCurrentRow(self.ui.listWidget.count() - 1)

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

    def color_transform(self, value):
        value = value.upper()
        digit = list(map(str, range(10))) + list("ABCDEF")
        if isinstance(value, tuple):
            string = '#'
            for i in value:
                a1 = i // 16
                a2 = i % 16
                string += digit[a1] + digit[a2]
            return string
        elif isinstance(value, str):
            a1 = digit.index(value[1]) * 16 + digit.index(value[2])
            a2 = digit.index(value[3]) * 16 + digit.index(value[4])
            a3 = digit.index(value[5]) * 16 + digit.index(value[6])
            return (a1, a2, a3)

    def change_point_color(self):
        global VIEW_DICT, PROPERTY_DICT
        objcolor = QColorDialog.getColor()
        if objcolor.isValid():
            objcolor = self.color_transform(objcolor.name())
            try:
                item = self.ui.treeWidget.currentItem()
                vtk_polydata = VIEW_DICT[item.text(0)][2]
                colors = np.array([[objcolor[0], objcolor[1], objcolor[2]]])
                colors = np.repeat(colors, PROPERTY_DICT[item.text(0)]['Pointnum'], axis=0)
                vtk_polydata.GetPointData().SetScalars(
                    numpy_to_vtk(colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR))
                VIEW_DICT[item.text(0)][2] = vtk_polydata
                self.renWin.Render()
                PROPERTY_DICT[item.text(0)]['colors'] = colors
            except:
                pass

    # 改变背景颜色函数
    def change_background_color(self):
        objcolor = QColorDialog.getColor()
        if objcolor.isValid():
            objcolor = self.color_transform(objcolor.name())
            self.ren.SetBackground(objcolor[0] / 255, objcolor[1] / 255, objcolor[2] / 255)
            self.ren.GradientBackgroundOff()
            self.renWin.Render()


    def save_file(self):
        try:
            item = self.ui.treeWidget.currentItem()
            parent = item.parent()
        except:
            parent = None
        if parent is None:
            pass
            QMessageBox.warning(self.ui.mainWidget, '警告', '请先选中数据对象！')
        else:
            current_data = OBJECT_DICT[item.text(0)]['data']
            path = QFileDialog.getSaveFileName(self.ui.mainWidget, '保存文件', "",
                                               "PCD Files (*.pcd);;ASCII Files (*.txt *.asc *.csv *.pts *.xyz);;"
                                               "LAS Files (*.las *.laz);;PLY Files (*.ply);;"
                                               "Mesh Files (*.obj *.stl *.off);;3DS Files (*.3ds);;VTK Files (*.vtk)")[
                0]
            if len(path) != 0:
                if '.pcd' in path:
                    pcd = o3d.geometry.PointCloud()
                    pcd.points = o3d.utility.Vector3dVector(current_data)
                    o3d.io.write_point_cloud(path, pcd)
                    self.update_listWidget('保存文件成功：' + path)
                elif '.txt' in path or '.asc' in path:
                    np.savetxt(path, current_data)
                    self.update_listWidget('保存文件成功：' + path)
                elif '.las' in path:
                    las = laspy.create(file_version="1.2", point_format=3)
                    las.x = current_data[:, 0]
                    las.y = current_data[:, 1]
                    las.z = current_data[:, 2]
                    las.red = PROPERTY_DICT[item.text(0)]['colors'][:, 0] / 255
                    las.green = PROPERTY_DICT[item.text(0)]['colors'][:, 1] / 255
                    las.blue = PROPERTY_DICT[item.text(0)]['colors'][:, 2] / 255
                    las.write(path)
                    self.update_listWidget('保存文件成功：' + path)
                elif '.' in path:
                    QMessageBox.warning(self.ui.mainWidget, '警告', '格式不支持！')

            # 函数实现

    def height_color(self):
        global VIEW_DICT, PROPERTY_DICT
        try:
            item = self.ui.treeWidget.currentItem()
            vtk_polydata = VIEW_DICT[item.text(0)][2]
            zmax = max(CURRENT_OBJECT[item.text(0)]['data'][:, 2])
            zmin = min(CURRENT_OBJECT[item.text(0)]['data'][:, 2])

            height_array = numpy_to_vtk(CURRENT_OBJECT[item.text(0)]['data'][:, 2])
            vtk_polydata.GetPointData().SetScalars(height_array)

            # 创建一个vtkLookupTable对象，用来设置颜色映射
            lookup_table = vtk.vtkLookupTable()
            lookup_table.SetTableRange(zmin, zmax)
            lookup_table.SetHueRange(0.6667, 0)
            lookup_table.SetSaturationRange(1, 1)
            lookup_table.SetValueRange(1, 1)
            lookup_table.Build()

            vtk_vertex = vtk.vtkVertexGlyphFilter()
            vtk_vertex.SetInputData(vtk_polydata)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(vtk_vertex.GetOutputPort())
            mapper.SetLookupTable(lookup_table)
            mapper.SetScalarRange(zmin, zmax)

            pointCloudActor = vtk.vtkActor()
            pointCloudActor.SetMapper(mapper)

            self.ren.RemoveActor(VIEW_DICT[item.text(0)][0])
            VIEW_DICT[item.text(0)][0] = pointCloudActor
            self.ren.AddActor(pointCloudActor)
            self.renWin.Render()
            # PROPERTY_DICT[item.text(0)]['colors'] = ['colorFunc', lookup_table]

        except:
            pass

        # try:
        #     intensity = las.intensity.astype(int)
        #     intensity_ = intensity / np.max(intensity) * 255
        #     if math.isnan(intensity_[0]):
        #         intensity_show = 255 * np.ones((len(intensity), 3))
        #     else:
        #         intensity_show = np.vstack((intensity_, intensity_, intensity_)).transpose()
        #     if color == 'None':
        #         color = 'Intensity'
        # except:
        #     intensity = None
        #     intensity_show = 255 * np.ones((point.shape[0], 3))
        #
        # PROPERTY_DICT[file_name] = {'Name': file_name, 'Visible': 1, 'Color': color, 'colors': colors,
        #                             'Pointnum': -1, 'Pointsize': 1, 'intensity': intensity,
        #                             'intensity_show': intensity_show, 'None_show': 255 * np.ones((point.shape[0], 3))}

    def intensity_color(self):
        item = self.ui.treeWidget.currentItem()
        try:
            self.show_point(CURRENT_OBJECT[item.text(0)]['data'], item.text(0),
                            PROPERTY_DICT[item.text(0)]['intensity_show'], todo='replace')
        except:
            pass

    def merge(self):
        try:
            items = self.ui.treeWidget.selectedItems()
            if len(items) < 2:
                QMessageBox.warning(self.ui.mainWidget, '警告', '请选中两个点云！')
                return
            parent = items[0].parent()
        except:
            parent = None
        if parent is None:
            pass
            QMessageBox.warning(self.ui.mainWidget, '警告', '请先选中数据对象！')
        else:
            current_data1 = OBJECT_DICT[items[0].text(0)]['data']
            colors1 = PROPERTY_DICT[items[0].text(0)]['colors']
            current_data2 = OBJECT_DICT[items[1].text(0)]['data']
            colors2 = PROPERTY_DICT[items[1].text(0)]['colors']
            current_data = np.vstack((current_data1, current_data2))
            colors = np.vstack((colors1, colors2))
            file_name = 'merged'
            OBJECT_DICT[file_name] = {'type': 'point'}
            OBJECT_DICT[file_name]['data'] = current_data
            self.update_treeWidget(status='addsub', info=[parent.text(0), file_name])
            PROPERTY_DICT[file_name] = {'Name': file_name, 'Visible': 1, 'Color': 'RGB', 'colors': colors,
                                        'Pointnum': len(OBJECT_DICT[file_name]['data']), 'Pointsize': 1}
            self.show_point(OBJECT_DICT[file_name]['data'], file_name, colors)


#####点云颜色
    def color_transform(self, value):
        value = value.upper()
        digit = list(map(str, range(10))) + list("ABCDEF")
        if isinstance(value, tuple):
            string = '#'
            for i in value:
                a1 = i // 16
                a2 = i % 16
                string += digit[a1] + digit[a2]
            return string
        elif isinstance(value, str):
            a1 = digit.index(value[1]) * 16 + digit.index(value[2])
            a2 = digit.index(value[3]) * 16 + digit.index(value[4])
            a3 = digit.index(value[5]) * 16 + digit.index(value[6])
            return (a1, a2, a3)

    def change_point_color(self):
        global VIEW_DICT, PROPERTY_DICT
        objcolor = QColorDialog.getColor()
        if objcolor.isValid():
            objcolor = self.color_transform(objcolor.name())
            try:
                item = self.ui.treeWidget.currentItem()
                vtk_polydata = VIEW_DICT[item.text(0)][2]
                colors = np.array([[objcolor[0], objcolor[1], objcolor[2]]])
                colors = np.repeat(colors, PROPERTY_DICT[item.text(0)]['Pointnum'], axis=0)
                vtk_polydata.GetPointData().SetScalars(
                    numpy_to_vtk(colors, deep=True, array_type=vtk.VTK_UNSIGNED_CHAR))
                VIEW_DICT[item.text(0)][2] = vtk_polydata
                self.renWin.Render()
                PROPERTY_DICT[item.text(0)]['colors'] = colors
            except:
                pass

    # 改变背景颜色函数
    def change_background_color(self):
        objcolor = QColorDialog.getColor()
        if objcolor.isValid():
            objcolor = self.color_transform(objcolor.name())
            self.ren.SetBackground(objcolor[0] / 255, objcolor[1] / 255, objcolor[2] / 255)
            self.ren.GradientBackgroundOff()
            self.renWin.Render()

    # 恢复默认背景颜色函数
    def background_Default(self):
        self.ren.SetBackground(0, 0, 0)  # 页面底部颜色
        self.ren.SetBackground2(255, 149, 105)  # 页面顶部颜色
        self.ren.GradientBackgroundOn()  # 开启渐变背景
        self.renWin.Render()


       ########点云着色
    #####高程着色
    # 函数实现
    def height_color(self):
        global VIEW_DICT, PROPERTY_DICT
        try:
            item = self.ui.treeWidget.currentItem()
            vtk_polydata = VIEW_DICT[item.text(0)][2]
            zmax = max(CURRENT_OBJECT[item.text(0)]['data'][:, 2])
            zmin = min(CURRENT_OBJECT[item.text(0)]['data'][:, 2])

            height_array = numpy_to_vtk(CURRENT_OBJECT[item.text(0)]['data'][:, 2])
            vtk_polydata.GetPointData().SetScalars(height_array)

            # 创建一个vtkLookupTable对象，用来设置颜色映射
            lookup_table = vtk.vtkLookupTable()
            lookup_table.SetTableRange(zmin, zmax)
            lookup_table.SetHueRange(0.6667, 0)
            lookup_table.SetSaturationRange(1, 1)
            lookup_table.SetValueRange(1, 1)
            lookup_table.Build()

            vtk_vertex = vtk.vtkVertexGlyphFilter()
            vtk_vertex.SetInputData(vtk_polydata)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(vtk_vertex.GetOutputPort())
            mapper.SetLookupTable(lookup_table)
            mapper.SetScalarRange(zmin, zmax)

            pointCloudActor = vtk.vtkActor()
            pointCloudActor.SetMapper(mapper)

            self.ren.RemoveActor(VIEW_DICT[item.text(0)][0])
            VIEW_DICT[item.text(0)][0] = pointCloudActor
            self.ren.AddActor(pointCloudActor)
            self.renWin.Render()
            # PROPERTY_DICT[item.text(0)]['colors'] = ['colorFunc', lookup_table]

        except:
            pass


# #############强度着色
#     try:
#         intensity = las.intensity.astype(int)
#         intensity_ = intensity / np.max(intensity) * 255
#         if math.isnan(intensity_[0]):
#             intensity_show = 255 * np.ones((len(intensity), 3))
#         else:
#             intensity_show = np.vstack((intensity_, intensity_, intensity_)).transpose()
#         if color == 'None':
#             color = 'Intensity'
#     except:
#         intensity = None
#         intensity_show = 255 * np.ones((point.shape[0], 3))
#
#     PROPERTY_DICT[file_name] = {'Name': file_name, 'Visible': 1, 'Color': color, 'colors': colors,
#                                 'Pointnum': -1, 'Pointsize': 1, 'intensity': intensity,
#                                 'intensity_show': intensity_show, 'None_show': 255 * np.ones((point.shape[0], 3))}
#
#
#  ####显示强度
#     def intensity_color(self):
#         item = self.ui.treeWidget.currentItem()
#         try:
#             self.show_point(CURRENT_OBJECT[item.text(0)]['data'], item.text(0),
#                             PROPERTY_DICT[item.text(0)]['intensity_show'], todo='replace')
#         except:
#             pass
#


###########密度着色
    def density_color(self):
        try:
            item = self.ui.treeWidget.currentItem()
            point = CURRENT_OBJECT[item.text(0)]['data']

            tree = cKDTree(point)
            dis, idx = tree.query(point, k=10)
            density = np.mean(dis, axis=1)

            vtk_polydata = VIEW_DICT[item.text(0)][2]
            dmax = max(density)
            dmin = min(density)

            density_array = numpy_to_vtk(density)
            vtk_polydata.GetPointData().SetScalars(density_array)

            # 创建一个vtkLookupTable对象，用来设置颜色映射
            lookup_table = vtk.vtkLookupTable()
            lookup_table.SetTableRange(dmin, dmax)
            lookup_table.SetHueRange(0.6667, 0)
            lookup_table.SetSaturationRange(1, 1)
            lookup_table.SetValueRange(1, 1)
            lookup_table.Build()

            vtk_vertex = vtk.vtkVertexGlyphFilter()
            vtk_vertex.SetInputData(vtk_polydata)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(vtk_vertex.GetOutputPort())
            mapper.SetLookupTable(lookup_table)
            mapper.SetScalarRange(dmin, dmax)

            pointCloudActor = vtk.vtkActor()
            pointCloudActor.SetMapper(mapper)

            self.ren.RemoveActor(VIEW_DICT[item.text(0)][0])
            VIEW_DICT[item.text(0)][0] = pointCloudActor
            self.ren.AddActor(pointCloudActor)
            self.renWin.Render()

        except:
            pass



    def intensity_color(self):
        item = self.ui.treeWidget.currentItem()
        try:
            self.show_point(CURRENT_OBJECT[item.text(0)]['data'], item.text(0),
                            PROPERTY_DICT[item.text(0)]['intensity_show'], todo='replace')
        except:
            pass

    def merge(self):
        try:
            items = self.ui.treeWidget.selectedItems()
            if len(items) < 2:
                QMessageBox.warning(self.ui.mainWidget, '警告', '请选中两个点云！')
                return
            parent = items[0].parent()
        except:
            parent = None
        if parent is None:
            pass
            QMessageBox.warning(self.ui.mainWidget, '警告', '请先选中数据对象！')
        else:
            current_data1 = OBJECT_DICT[items[0].text(0)]['data']
            colors1 = PROPERTY_DICT[items[0].text(0)]['colors']
            current_data2 = OBJECT_DICT[items[1].text(0)]['data']
            colors2 = PROPERTY_DICT[items[1].text(0)]['colors']
            current_data = np.vstack((current_data1, current_data2))
            colors = np.vstack((colors1, colors2))
            file_name = 'merged'
            OBJECT_DICT[file_name] = {'type': 'point'}
            OBJECT_DICT[file_name]['data'] = current_data
            self.update_treeWidget(status='addsub', info=[parent.text(0), file_name])
            PROPERTY_DICT[file_name] = {'Name': file_name, 'Visible': 1, 'Color': 'RGB', 'colors': colors,
                                        'Pointnum': len(OBJECT_DICT[file_name]['data']), 'Pointsize': 1}
            self.show_point(OBJECT_DICT[file_name]['data'], file_name, colors)

####点云拾取文本显示
class Pick_Point_Frame(QFrame):
    def __init__(self, parent, pick_Actor, ren, iren, renWin, camera, console_List):
        super().__init__(parent)
        self.iniDragCor = [0, 0]
        self.pick_Actor = pick_Actor
        self.ren = ren
        self.iren = iren
        self.renWin = renWin
        self.camera = camera
        self.console_List = console_List
        self.colors = vtk.vtkNamedColors()

        self.resize(60, 30)
        self.move(325, 68)
        self.setStyleSheet("QFrame{background-color: white; }")
        self.pickrecovery_button = QPushButton(self)
        self.pickrecovery_button.setIcon(QIcon("DY/templates/static/img/重新开始.png"))
        self.pickrecovery_button.setGeometry(5, 5, 20, 20)
        self.pickrecovery_button.clicked.connect(self.to_pickrecovery)
        self.pickquit_button = QPushButton(self)
        self.pickquit_button.setIcon(QIcon("DY/templates/static/img/取消.png"))
        self.pickquit_button.setGeometry(35, 5, 20, 20)
        self.pickquit_button.clicked.connect(self.to_pickquit)
        self.setVisible(False)

    # 拾取点云框架激活函数
    def activate(self):
        self.iren.RemoveObservers('RightButtonPressEvent')
        self.iren.AddObserver('RightButtonPressEvent', self.rightbutton_pickpoint)
        self.setVisible(True)
        self.console_List_updata('开始拾取点云 -> 鼠标右键单击拾取')

    def console_List_updata(self, info):
        now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        self.console_List.addItem('[' + str(now_time) + '] ' + info)
        self.console_List.setCurrentRow(self.console_List.count() - 1)

    # 恢复拾取函数
    def to_pickrecovery(self):
        for i in self.pick_Actor:
            self.ren.RemoveActor(i)
        self.renWin.Render()
        self.console_List_updata('清空拾取的点云 -> 重新拾取')

    # 退出拾取函数
    def to_pickquit(self):
        for i in self.pick_Actor:
            self.ren.RemoveActor(i)
        self.setVisible(False)
        self.iren.RemoveObservers('RightButtonPressEvent')
        self.iren.AddObserver('RightButtonPressEvent', self.rightbutton_changefocus)
        self.console_List_updata('退出拾取点云功能')

    # 右键改变相机焦点函数
    def rightbutton_changefocus(self, obj, event):
        clickPos = self.iren.GetEventPosition()
        cellPicker = vtk.vtkPointPicker()
        self.iren.SetPicker(cellPicker)
        picker = self.iren.GetPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        point_position = picker.GetPickPosition()
        # 改变相机焦点
        self.camera.SetFocalPoint(point_position)
        self.ren.SetActiveCamera(self.camera)
        self.renWin.Render()

    # 拾取过程鼠标右键响应函数
    def rightbutton_pickpoint(self, obj, event):
        clickPos = self.iren.GetEventPosition()
        cellPicker = vtk.vtkPointPicker()
        self.iren.SetPicker(cellPicker)
        picker = self.iren.GetPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        point_position = picker.GetPickPosition()
        # 添加高亮点
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(point_position)
        sphereSource.SetRadius(0.05)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphereSource.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        self.ren.AddActor(actor)
        # 添加文本注释/坐标，id
        atext = vtk.vtkVectorText()
        atext.SetText('Point ID: %d\nX: %.4f\nY: %.4f\nZ: %.4f' % (
            picker.GetPointId(), picker.GetPickPosition()[0], picker.GetPickPosition()[1], picker.GetPickPosition()[2]))
        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInputConnection(atext.GetOutputPort())
        textActor = vtk.vtkFollower()
        textActor.SetMapper(textMapper)
        textActor.SetScale(1, 1, 1)
        textActor.AddPosition(picker.GetPickPosition())
        textActor.GetProperty().SetColor(self.colors.GetColor3d('Red'))
        self.ren.AddActor(textActor)
        # self.ren.ResetCameraClippingRange()
        textActor.SetCamera(self.ren.GetActiveCamera())
        self.pick_Actor.append(actor)
        self.pick_Actor.append(textActor)
        self.renWin.Render()

    def mousePressEvent(self, e):
        self.iniDragCor[0] = e.x()
        self.iniDragCor[1] = e.y()

    def mouseMoveEvent(self, e):
        x = e.x() - self.iniDragCor[0]
        y = e.y() - self.iniDragCor[1]
        cor = QPoint(x, y)
        self.move(self.mapToParent(cor))
    ######点云拾去列表

class Pointlst_Frame(QFrame):
    def __init__(self, parent, pick_Actor, ren, iren, renWin, camera, console_List):
        super().__init__(parent)
        self.iniDragCor = [0, 0]
        self.pick_Actor = pick_Actor
        self.ren = ren
        self.iren = iren
        self.renWin = renWin
        self.camera = camera
        self.console_List = console_List
        self.colors = vtk.vtkNamedColors()

        self.resize(300, 200)
        self.move(325, 68)
        self.setStyleSheet("QFrame{background-color: white; }")
        self.pickrecovery_button = QPushButton(self)
        self.pickrecovery_button.setIcon(QIcon("DY/templates/static/img/重新开始.png"))
        self.pickrecovery_button.setGeometry(5, 5, 20, 20)
        self.pickrecovery_button.clicked.connect(self.to_pickrecovery)
        self.pickquit_button = QPushButton(self)
        self.pickquit_button.setIcon(QIcon("DY/templates/static/img/取消.png"))
        self.pickquit_button.setGeometry(35, 5, 20, 20)
        self.pickquit_button.clicked.connect(self.to_pickquit)

        self.table = QTableWidget(self)
        self.table.resize(300, 170)
        self.table.move(0, 30)
        self.table.verticalHeader().setVisible(False)
        self.table.clearContents()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'X', 'Y', 'Z'])
        self.table.horizontalHeader().setSectionsClickable(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 水平自适应
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.table.resizeColumnsToContents()  # 宽度与内容相适应
        self.table.resizeRowsToContents()
        self.table_rows = 0

        self.setVisible(False)

    def update_table(self, info):
        self.table_rows += 1
        self.table.setRowCount(self.table_rows)
        newItem = QTableWidgetItem('%d'%info[0])
        self.table.setItem(self.table_rows-1, 0, newItem)
        newItem = QTableWidgetItem('%.3f'%info[1])
        self.table.setItem(self.table_rows-1, 1, newItem)
        newItem = QTableWidgetItem('%.3f'%info[2])
        self.table.setItem(self.table_rows - 1, 2, newItem)
        newItem = QTableWidgetItem('%.3f'%info[3])
        self.table.setItem(self.table_rows - 1, 3, newItem)


    # 拾取点云框架激活函数
    def activate(self):
        self.iren.RemoveObservers('RightButtonPressEvent')
        self.iren.AddObserver('RightButtonPressEvent', self.rightbutton_pickpoint)
        self.setVisible(True)
        self.console_List_updata('开始拾取点云 -> 鼠标右键单击拾取')

    def console_List_updata(self, info):
        now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        self.console_List.addItem('[' + str(now_time) + '] ' + info)
        self.console_List.setCurrentRow(self.console_List.count() - 1)

    # 恢复拾取函数
    def to_pickrecovery(self):
        self.table_rows = 0
        self.table.clearContents()
        for i in self.pick_Actor:
            self.ren.RemoveActor(i)
        self.renWin.Render()
        self.console_List_updata('清空拾取的点云 -> 重新拾取')

    # 退出拾取函数
    def to_pickquit(self):
        self.table_rows = 0
        self.table.clearContents()
        self.setVisible(False)
        for i in self.pick_Actor:
            self.ren.RemoveActor(i)
        self.renWin.Render()
        self.iren.RemoveObservers('RightButtonPressEvent')
        self.iren.AddObserver('RightButtonPressEvent', self.rightbutton_changefocus)
        self.console_List_updata('退出拾取点云功能')

    # 右键改变相机焦点函数
    def rightbutton_changefocus(self, obj, event):
        clickPos = self.iren.GetEventPosition()
        cellPicker = vtk.vtkPointPicker()
        self.iren.SetPicker(cellPicker)
        picker = self.iren.GetPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        point_position = picker.GetPickPosition()
        # 改变相机焦点
        self.camera.SetFocalPoint(point_position)
        self.ren.SetActiveCamera(self.camera)
        self.renWin.Render()

    # 拾取过程鼠标右键响应函数
    def rightbutton_pickpoint(self, obj, event):
        clickPos = self.iren.GetEventPosition()
        cellPicker = vtk.vtkPointPicker()
        self.iren.SetPicker(cellPicker)
        picker = self.iren.GetPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        point_position = picker.GetPickPosition()
        self.update_table([picker.GetPointId(), picker.GetPickPosition()[0], picker.GetPickPosition()[1], picker.GetPickPosition()[2]])
        # 添加高亮点
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(point_position)
        sphereSource.SetRadius(0.05)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphereSource.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        self.ren.AddActor(actor)
        # 添加文本注释/坐标，id
        atext = vtk.vtkVectorText()
        atext.SetText('Point ID: %d' % (picker.GetPointId()))
        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInputConnection(atext.GetOutputPort())
        textActor = vtk.vtkFollower()
        textActor.SetMapper(textMapper)
        textActor.SetScale(1, 1, 1)
        textActor.AddPosition(picker.GetPickPosition())
        textActor.GetProperty().SetColor(self.colors.GetColor3d('Red'))
        self.ren.AddActor(textActor)
        # self.ren.ResetCameraClippingRange()
        textActor.SetCamera(self.ren.GetActiveCamera())
        self.pick_Actor.append(actor)
        self.pick_Actor.append(textActor)
        self.renWin.Render()



    def mousePressEvent(self, e):
        self.iniDragCor[0] = e.x()
        self.iniDragCor[1] = e.y()

    def mouseMoveEvent(self, e):
        x = e.x() - self.iniDragCor[0]
        y = e.y() - self.iniDragCor[1]
        cor = QPoint(x, y)
        self.move(self.mapToParent(cor))
