# 绑定按键
self.ui.action_16.triggered.connect(self.height_color)

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
