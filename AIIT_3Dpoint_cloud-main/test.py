import open3d as o3d


def convert_ply_to_pcd(ply_file, pcd_file):
    # 读取PLY文件
    point_cloud = o3d.io.read_point_cloud(ply_file)

    # 保存为PCD文件
    o3d.io.write_point_cloud(pcd_file, point_cloud)


# 使用示例
ply_file_path = 'C:\\Users\\N203\Desktop\\bunny (1)\\bunny\data\\bun000.ply'  # 填入ply文件的路径
pcd_file_path = 'test.pcd'  # 填入pcd文件的路径
convert_ply_to_pcd(ply_file_path, pcd_file_path)
