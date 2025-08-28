import os
import subprocess

from datetime import datetime
import secrets

import math
import json
import numpy as np

from OCC.Extend.DataExchange import write_step_file

try:
    from ..cadlib.extrude import CADSequence
    from ..cadlib.visualize import create_CAD
except:
    import sys
    sys.path.append("..")
    from cadlib.extrude import CADSequence
    from cadlib.visualize import create_CAD
from .frdconvert import read_frd

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


def calculate_bolt_hole_coordinates(N, R):
    """
    计算法兰螺栓孔的中心点坐标
    :param N: 螺栓孔数量
    :param R: 螺栓孔中心圆半径
    :return: 螺栓孔中心点的坐标列表 [{"y": y1, "x": x1, "z": 0}, {"y": y2, "x": x2, "z": 0}, ...]
    """
    coordinates = []
    for i in range(1, N + 1):
        theta = 2 * math.pi * (i - 1) / N  # 计算角度
        x = R * math.cos(theta)           # 计算x坐标
        y = R * math.sin(theta)           # 计算y坐标
        coordinates.append({"y": round(y, 2), "x": round(x, 2), "z": 0})  # 添加坐标到列表
    return coordinates


def save_and_run(params_to_show):
    # 获取螺栓数量
    bolt_count = int(params_to_show["others"]["bolt_count_edit"])
    
    # 计算螺栓孔坐标
    coordinates = calculate_bolt_hole_coordinates(bolt_count, float(params_to_show["profiles"]["BoltCenterRadius"]))

    info = {
            "entities": {                                                               # 建模实体
                "FK7jL49LUytd8NJ_0": {                                                  # 草图实体
                                        "transform": {                                  # 坐标系
                                            "origin": {                                 # 原点
                                                "y": 0.0,
                                                "x": 0.0,
                                                "z": 0.0
                                            },
                                            "y_axis": {
                                                "y": 0.0,
                                                "x": 0.0,
                                                "z": 1.0
                                            },
                                            "x_axis": {
                                                "y": 0.0,
                                                "x": 1.0,
                                                "z": 0.0
                                            },
                                            "z_axis": {                                 # 法向量，Y轴朝下
                                                "y": -1.0,
                                                "x": 0.0,
                                                "z": 0.0
                                            }
                                        },
                                        "type": "Sketch",
                                        "name": "Sketch 1",
                                        "reference_plane": {},             
                                        "profiles": {                                   # 轮廓
                                            "JGa": {
                                                "loops": [                              # 闭合环列表
                                                    {
                                                        "profile_curves": [             # 外径
                                                            {
                                                                "type": "Circle3D",
                                                                "curve": "JGB",
                                                                "center_point": {       # 圆心
                                                                    "y": 0.0,
                                                                    "x": 0.0,
                                                                    "z": 0.0
                                                                },
                                                                "radius": params_to_show["profiles"]["D"],
                                                                "normal": {             # 法向量
                                                                    "y": -1.0,
                                                                    "x": 0.0,
                                                                    "z": 0.0
                                                                }
                                                            }
                                                        ],
                                                        "is_outer": True
                                                    },
                                                    {
                                                        "profile_curves": [             # 内径
                                                            {
                                                                "type": "Circle3D",
                                                                "curve": "JGF",
                                                                "center_point": {
                                                                    "y": 0.0,
                                                                    "x": 0.0,
                                                                    "z": 0.0
                                                                },
                                                                "radius": params_to_show["profiles"]["B1"],
                                                                "normal": {
                                                                    "y": -1.0,
                                                                    "x": 0.0,
                                                                    "z": 0.0
                                                                }
                                                            }
                                                        ],
                                                        "is_outer": False
                                                    }
                                                ],
                                                "properties": {}
                                            }
                                        }
                                    },
                "FiME8kgh5qvs1e2_0": {                                                  # 拉伸特征
                                        "name": "Extrude 1",
                                        "type": "ExtrudeFeature",
                                        "profiles": [
                                            {
                                                "profile": "JGa",
                                                "sketch": "FK7jL49LUytd8NJ_0"           # 引用FK7jL49LUytd8NJ_0的JGa
                                            }
                                        ],
                                        "operation": "NewBodyFeatureOperation",         # 创建一个新的独立几何体
                                        "start_extent": {
                                            "type": "ProfilePlaneStartDefinition"       # 拉伸的起始位置是草图所在的平面
                                        },
                                        "extent_type": "OneSideFeatureExtentType",      # 单侧拉伸
                                        "extent_one": {
                                            "distance": {                               # 拉伸距离
                                                "type": "ModelParameter",
                                                "role": "AlongDistance",
                                                "name": "none",
                                                "value": params_to_show["extent"]["thickness"]
                                            },
                                            "type": "DistanceExtentDefinition",
                                            "taper_angle": {                            # 拔模斜度
                                                "type": "ModelParameter",
                                                "role": "TaperAngle",
                                                "name": "none",
                                                "value": 0
                                            }
                                        },
                                        "extent_two": {                                 # 若extent_type为TwoSidesFeatureExtentType，可通过该参数设置方向2的拉伸
                                            "distance": {
                                                "type": "ModelParameter",
                                                "role": "AgainstDistance",
                                                "name": "none",
                                                "value": 0
                                            },
                                            "type": "DistanceExtentDefinition",
                                            "taper_angle": {
                                                "type": "ModelParameter",
                                                "role": "Side2TaperAngle",
                                                "name": "none",
                                                "value": 0
                                            }
                                        }
                                    },
            },
            "properties": {                                                             # 边界框
                    "bounding_box": {
                        "max_point": {
                            "y": 0.0,                                                   # 若双向拉伸需要=thickness
                            "x": params_to_show["profiles"]["D"],
                            "z": params_to_show["profiles"]["D"]
                        },
                        "type": "BoundingBox3D",
                        "min_point": {
                            "y": -params_to_show["extent"]["thickness"],
                            "x": -params_to_show["profiles"]["D"],
                            "z": -params_to_show["profiles"]["D"]
                        }
                    }
                },
            "sequence": [                                                               # 操作顺序
                    {                                                                   # 生成草图
                        "index": 0,
                        "type": "Sketch",
                        "entity": "FK7jL49LUytd8NJ_0"
                    },
                    {                                                                   # 拉伸为实体
                        "index": 1,
                        "type": "ExtrudeFeature",
                        "entity": "FiME8kgh5qvs1e2_0"
                    }
                ]
    }
    
    for i in range(bolt_count):
        info["entities"]["FK7jL49LUytd8NJ_0"]["profiles"]["JGa"]["loops"].append(
                                                    {
                                                        "profile_curves": [             # 螺栓孔 i
                                                            {
                                                                "type": "Circle3D",
                                                                "curve": "JG{}".format(chr(i + ord('c'))),
                                                                "center_point": coordinates[i],
                                                                "radius": params_to_show["profiles"]["L"],
                                                                "normal": {
                                                                    "y": -1.0,
                                                                    "x": 0.0,
                                                                    "z": 0.0
                                                                }
                                                            }
                                                        ],
                                                        "is_outer": False
                                                    }
                                            )
    return info


def step_generation(D, B1, L, BoltCenterRadius, thickness, bolt_count_edit):
    PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    params_to_show = {
        "profiles": {
                        "D": D,                              
                        "B1": B1,                            
                        "L": L,                              
                        "BoltCenterRadius": BoltCenterRadius
                    }, 
        "extent": {"thickness": thickness},                    
        "others": {"bolt_count_edit": bolt_count_edit}}   

    # 保存参数
    info = save_and_run(params_to_show)

    # 工作目录
    work_dir = os.path.join(PATH, 
                            "work_dir", 
                            datetime.strftime(datetime.now(), "%Y%m%d%H%M%S%f") + "_" + secrets.token_hex(4))
    os.makedirs(work_dir, exist_ok=True)

    # 零件导出
    step_file_path = os.path.join(work_dir, 'flange.step')
    cad_seq = CADSequence.from_dict(info)
    out_shape = create_CAD(cad_seq)
    write_step_file(out_shape, step_file_path) 

    return step_file_path


def cae_analysis(step_file_path, Name, YoungsModulus, PoissonRatio, Density, pressure):
    PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PATH_EDIT = os.path.join(PATH, "Edit_plain")
    freecad_python = os.path.join(PATH, "squashfs-root/usr/bin/freecadcmd")
    work_dir = os.path.dirname(step_file_path)

    # 参数
    material = {                                   
        "Name": Name,                                          
        "YoungsModulus": "{} MPa".format(YoungsModulus),      
        "PoissonRatio": str(PoissonRatio),                    
        "Density": "{} kg/m^3".format(Density)     
    }
     
    # 有限元计算
    script_path = os.path.join(PATH_EDIT, "flange_plane.py")
    process = subprocess.Popen(
                                [
                                freecad_python, 
                                "-c", 
                                "import sys; "
                                "sys.argv = ['{}', '--material', '{}', '--pressure', '{}', "
                                "'--step_files', '{}', '--working_path', '{}']; "
                                "exec(open('{}').read())".format(
                                                                    script_path,  
                                                                    json.dumps(material),
                                                                    pressure,
                                                                    step_file_path, 
                                                                    work_dir, 
                                                                    script_path)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
    stdout, stderr = process.communicate()
    if len(stderr):
        raise RuntimeError(stderr)
    else:
        return os.path.join(work_dir, "ImportedPart_Mesh.frd")


def frd_extract(frd_path):
    info = read_frd(frd_path)

    # postprocess
    disps = []
    for id in info["DISP"]:
        disps.append(info["DISP"][id])
    disp = np.sqrt(np.sum(np.array(disps)**2, axis=1))
    disp_min = disp.min().item() * 1e6  # m -> μm
    disp_max = disp.max().item() * 1e6  # m -> μm

    unit = (disp_max - disp_min) / 4
    return disp_max, disp_max - unit, disp_max + unit


def main(params_to_show, material, pressure, work_dir):
    PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PATH_EDIT = os.path.join(PATH, "Edit_plain")
    freecad_python = os.path.join(PATH, "squashfs-root/usr/bin/freecadcmd")

    # 保存参数
    info = save_and_run(params_to_show)

    # 零件导出
    step_file_path = os.path.join(work_dir, 'flange.step')
    if 1:  # not os.path.exists(step_file_path):
        cad_seq = CADSequence.from_dict(info)
        out_shape = create_CAD(cad_seq)
        write_step_file(out_shape, step_file_path) 

    # 有限元计算
    script_path = os.path.join(PATH_EDIT, "flange_plane.py")
    process = subprocess.Popen(
                                [
                                freecad_python, 
                                "-c", 
                                "import sys; "
                                "sys.argv = ['{}', '--material', '{}', '--pressure', '{}', "
                                "'--step_files', '{}', '--working_path', '{}']; "
                                "exec(open('{}').read())".format(
                                                                    script_path, 
                                                                    json.dumps(material),
                                                                    pressure,
                                                                    step_file_path, 
                                                                    work_dir, 
                                                                    script_path)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
    stdout, stderr = process.communicate()
    if len(stdout):
        print("INFO: \n")
        print(stdout)
    if len(stderr):
        print("ERROR: \n")
        print(stderr)
        return None
    info = read_frd(os.path.join(work_dir, "ImportedPart_Mesh.frd"))

    # 导出frd参数
    with open(os.path.join(work_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
    
    return info
