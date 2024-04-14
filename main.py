import open3d as o3d
import sys
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QFileDialog, QFrame, QLabel, QTextEdit, \
    QVBoxLayout


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.statusBar()

        menubar = self.menuBar()

        # 创建菜单项
        fileMenu = menubar.addMenu('文件')
        toolsMenu = menubar.addMenu('工具')
        denoiseMenu = menubar.addMenu('去噪')
        filterMenu = menubar.addMenu('滤波')
        registerMenu = menubar.addMenu('配准')
        segmentationMenu = menubar.addMenu('分割')

        # 文件菜单中加载点云的功能
        loadCloudAction = QAction('加载点云', self)
        loadCloudAction.triggered.connect(self.loadPointCloud)
        fileMenu.addAction(loadCloudAction)

        exitAction = QAction('退出', self)
        exitAction.triggered.connect(qApp.quit)
        fileMenu.addAction(exitAction)

        # 主视图布局
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QtWidgets.QHBoxLayout(self.main_widget)

        # 控制台和点云视图的分割视图
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # 控制台框架
        frame = QtWidgets.QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)

        # 字体设置
        font = QFont("Arial", 12, QFont.Bold)

        # 属性 label
        properties_label = QLabel("属性")
        properties_label.setFont(font)  # 设置与控制台相同的字体
        # 属性 text edit
        properties_editor = QTextEdit()

        # 文件 label
        files_label = QLabel("文件")
        files_label.setFont(font)  # 设置与控制台相同的字体
        # 文件 text edit
        files_editor = QTextEdit()

        # 控制台 label
        console_label = QLabel("控制台")
        console_label.setFont(font)

        # 控制台 text edit
        console_editor = QTextEdit()

        # 垂直布局器
        frame_layout = QVBoxLayout()

        # 分配每个部分的空间；这里属性和文件仅获得必要的空间，而控制台获取所有剩余空间
        frame_layout.addWidget(properties_label)
        frame_layout.addWidget(properties_editor)
        frame_layout.addWidget(files_label)
        frame_layout.addWidget(files_editor)
        frame_layout.addWidget(console_label)
        frame_layout.addWidget(console_editor, 1)  # 控制台占据所有剩余空间

        frame.setLayout(frame_layout)  # 将布局应用于控制台框架

        # 这个demo里控制台只是一个文本编辑
        console_editor = QtWidgets.QTextEdit()

        # 用于显示点云的窗口（在这个例子中它只是一个占位符）
        # 实际上你需要运行一个Open3D可视化窗口
        # 并且将它作为一个外部应用嵌入到一个QWidget中
        cloud_widget = QtWidgets.QWidget()
        cloud_widget.setStyleSheet("background-color: white;")

        splitter.addWidget(frame)
        splitter.addWidget(cloud_widget)
        layout.addWidget(splitter)

        self.setWindowTitle('点云数据处理软件')
        # 设置窗口初始大小
        self.resize(1600, 1200)
        self.show()

    def loadPointCloud(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]

        if fname:
            print(f"加载文件: {fname}")
            # 这里，你将使用 Open3D 加载和处理点云文件
            # 例如:
            # cloud = o3d.io.read_point_cloud(fname)
            # o3d.visualization.draw_geometries([cloud])

            # 注意: open3d绘图调用会打开一个新的窗口，它不是内嵌在 PyQt 应用中。


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
