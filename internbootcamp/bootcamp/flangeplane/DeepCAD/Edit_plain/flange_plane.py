import argparse

import json

import FreeCAD
import Part
import ObjectsFem
from femmesh.gmshtools import GmshTools as gt
from femtools import ccxtools

parser = argparse.ArgumentParser(description="加载STEP文件并执行有限元分析")
parser.add_argument("--step_files", help="STEP文件路径", type=str)
parser.add_argument("--working_path", help="工作目录", type=str)
parser.add_argument("--material", help="", type=str)
parser.add_argument("--pressure", help="", type=str)
args = parser.parse_args()

args.material = json.loads(args.material)

# 加载STEP文件
shape = Part.Shape()
shape.read(args.step_files)
assert shape.isClosed(), "几何体不是封闭的三维实体，请修复几何体后重试。"

# 创建一个新的文档
doc = FreeCAD.newDocument("FEM_Analysis")  

# 将STEP文件中的形状添加到文档中
part_obj = doc.addObject("Part::Feature", "ImportedPart")
part_obj.Shape = shape  

# 创建分析对象
analysis_object = ObjectsFem.makeAnalysis(doc, "Analysis")  

# 创建求解器
solver_object = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiX")
solver_object.GeometricalNonlinearity = 'linear'
solver_object.ThermoMechSteadyState = False  # 热力耦合稳态分析
solver_object.MatrixSolverType = 'default'
solver_object.IterationsControlParameterTimeUse = False  # 根据时间步长动态调整非线性迭代的控制参数
analysis_object.addObject(solver_object)

# 创建材料
material_object = ObjectsFem.makeMaterialSolid(doc, "SolidMaterial")
mat = material_object.Material
mat['Name'] = args.material["Name"]
mat['YoungsModulus'] = args.material["YoungsModulus"]
mat['PoissonRatio'] = args.material["PoissonRatio"]
mat['Density'] = args.material["Density"]
material_object.Material = mat
analysis_object.addObject(material_object)

# 面/边选择
faces = part_obj.Shape.Faces  # Area, CenterOfMass, Surface
edges = part_obj.Shape.Edges
ids = {}
for i, f in enumerate(faces, start=1):
    if isinstance(f.Surface, Part.Cylinder) and (abs(f.Surface.Center.x) < 1e-5) and (abs(f.Surface.Center.z) < 1e-5):  # Part.Plane
        ids[i] = f.Surface.Radius
assert len(ids) == 2, "invalid restrictions"
keys_sorted = sorted(ids, key=lambda k: ids[k])
id_restrict = [keys_sorted[1]]
id_force = [keys_sorted[0]]

# 添加固定约束
fixed_constraint = ObjectsFem.makeConstraintFixed(doc, "FemConstraintFixed")
fixed_constraint.References = [(part_obj, f"Face{i}") for i in id_restrict]
analysis_object.addObject(fixed_constraint)

# 添加压强约束
pressure_constraint = ObjectsFem.makeConstraintPressure(doc, "Pressure")
pressure_constraint.References = [(part_obj, f"Face{i}") for i in id_force]
pressure_constraint.Pressure = args.pressure  # 单位：MPa
pressure_constraint.Reversed = False  # 方向是否反向
analysis_object.addObject(pressure_constraint)

# 添加力约束
# force_constraint = ObjectsFem.makeConstraintForce(doc, "FemConstraintForce")
# force_constraint.References = [(part_obj, f"Face{id_force}")]
# force_constraint.Force = 90000.0
# force_constraint.Direction = (part_obj, [f"Edge{longest_edge_idx}"])
# force_constraint.Reversed = False
# analysis_object.addObject(force_constraint)

# 生成网格
femmesh_obj = ObjectsFem.makeMeshGmsh(doc, part_obj.Name + "_Mesh")
femmesh_obj.Shape = part_obj
doc.recompute()

# 使用Gmsh工具生成网格
gmsh_mesh = gt(femmesh_obj)
gmsh_mesh.GmshExe = "gmsh"  # 确保 Gmsh 可执行文件路径正确
gmsh_mesh.create_mesh()
analysis_object.addObject(femmesh_obj)
assert femmesh_obj.FemMesh.VolumeCount > 0, "生成的网格不包含三维体单元，请检查几何体和网格参数。"

# 运行分析
fea = ccxtools.FemToolsCcx()
fea.update_objects()
fea.setup_working_dir(args.working_path) 
fea.setup_ccx()
message = fea.check_prerequisites()
if not message:
    fea.purge_results()
    fea.write_inp_file()
    fea.ccx_run()
    fea.load_results()
else:
    print(message)
