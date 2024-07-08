def write_obj(vertices, faces, filename):
    with open(filename, 'w') as f:
        for v in vertices:
            f.write('v {} {} {}\n'.format(v[0], v[1], v[2]))
        
        for face in faces:
            f.write('f {} {} {}\n'.format(face[0]+1, face[1]+1, face[2]+1))

def find_faces(edges):
    faces = []
    for i in range(len(edges)):
        for j in range(i+1, len(edges)):
            # 找到共享一个顶点的两条边
            shared_vertices = set(edges[i]) & set(edges[j])
            if len(shared_vertices) == 1:
                # 创建一个面
                face = list(edges[i] + edges[j])
                face.remove(shared_vertices.pop())
                faces.append(face)
    return faces

# 从文件中读取顶点和边
vertices = []
with open('trouser_sofa.pred_mesh.txt', 'r') as f:
    for line in f:
        vertices.append(list(map(float, line.strip().split())))

edges = []
with open('trouser_sofa.pred_edge.txt', 'r') as f:
    for line in f:
        edges.append(list(map(int, line.strip().split())))

# 使用你的函数来找出可以形成面的边的组合
faces = find_faces(edges)

# 写入OBJ文件
write_obj(vertices, faces, 'trouser_sofa.obj')