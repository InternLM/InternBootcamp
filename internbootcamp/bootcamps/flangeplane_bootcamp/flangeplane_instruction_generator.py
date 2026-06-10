import os

import random
import math
from typing import Dict, Any, Optional, List
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

from internbootcamp.bootcamps.flangeplane_bootcamp import ips
from internbootcamp.bootcamps.flangeplane_bootcamp.utils.cost_cal import cost_analysis

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.tri as mtri
import matplotlib.gridspec as gridspec

import requests

import uuid

PATH = os.path.dirname(os.path.abspath(__file__))


def rand_exclusive(a, b):
    return a + (b - a) * random.random()


def plot_flange_combined_view(outer_radius, inner_radius, thickness, 
                              bolt_circle_radius, bolt_hole_radius, bolt_count, save_path):
    # 创建画布
    fig = plt.figure(figsize=(16, 8), dpi=100)
    
    # 使用 GridSpec 手动布局
    # left/right 留出边距，top=0.85 给标题留出足够的绝对空间
    gs = gridspec.GridSpec(1, 2, figure=fig, 
                           left=0.05, right=0.95, 
                           bottom=0.05, top=0.85, 
                           wspace=0.1)

    # 两个标题共享同一个 Y 坐标 (0.92)，保证绝对水平对齐
    title_y_pos = 0.92
    
    # 左侧标题位置 (x=0.27 大约是左半部分的中心)
    fig.text(0.27, title_y_pos, f"Top View", 
             ha='center', va='bottom', fontsize=18, fontweight='bold', color='#333333')
    
    # 右侧标题位置 (x=0.73 大约是右半部分的中心)
    fig.text(0.73, title_y_pos, "3D Solid View", 
             ha='center', va='bottom', fontsize=18, fontweight='bold', color='#333333')

    
    limit_2d = outer_radius * 1.5
    limit_3d = outer_radius * 1.05
    limit_3d_z = thickness * 2.5
    fontsize = 11

    # ==========================================
    # 1. 左侧：2D 俯视图
    # ==========================================
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_aspect('equal')
    
    outer_circle = patches.Circle((0, 0), outer_radius, fill=True, facecolor='#E0E0E0', edgecolor='black', linewidth=2.0)
    ax1.add_patch(outer_circle)
    inner_circle = patches.Circle((0, 0), inner_radius, fill=True, facecolor='white', edgecolor='black', linewidth=1.5)
    ax1.add_patch(inner_circle)
    
    ax1.plot([-limit_2d, limit_2d], [0, 0], color='black', linestyle='-.', linewidth=0.5, alpha=0.5)
    ax1.plot([0, 0], [-limit_2d, limit_2d], color='black', linestyle='-.', linewidth=0.5, alpha=0.5)

    for i in range(bolt_count):
        angle = 2 * np.pi * i / bolt_count
        bx = bolt_circle_radius * np.cos(angle)
        by = bolt_circle_radius * np.sin(angle)
        hole = patches.Circle((bx, by), bolt_hole_radius, fill=True, facecolor='white', edgecolor='black', linewidth=1.0)
        ax1.add_patch(hole)

    def draw_box(ax, x, y, z, text, color, ha, va, zorder=None):
        style = dict(
            color=color, 
            fontsize=fontsize,
            fontweight='bold',
            ha=ha, 
            va=va, 
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, alpha=0.9)
        )
        if zorder is not None:
            style['zorder'] = zorder
        pos = (x, y, z) if z else (x, y)
        ax.text(*pos, text, **style)

    # 尺寸标注
    def draw_radial_dimension(ax, radius, angle_deg, text, color='black', offset_text=1.1):
        angle_rad = np.deg2rad(angle_deg)
        start = (0, 0)
        end = (radius * np.cos(angle_rad), radius * np.sin(angle_rad))
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5, shrinkA=0, shrinkB=0))
        text_pos = (radius * offset_text * np.cos(angle_rad), radius * offset_text * np.sin(angle_rad))
        ha = 'left' if np.cos(angle_rad) > 0 else 'right'
        va = 'bottom' if np.sin(angle_rad) > 0 else 'top'
        draw_box(ax, text_pos[0], text_pos[1], None, text, color, ha=ha, va=va)

    # 内外径和PCD
    draw_radial_dimension(ax1, outer_radius, 30, f"R_out={outer_radius}mm", color='black')
    draw_radial_dimension(ax1, inner_radius, 135, f"R_in={inner_radius}mm", color='blue')
    draw_radial_dimension(ax1, bolt_circle_radius, -45, f"R_pitch={bolt_circle_radius}mm", color='red')

    # 螺栓孔十字
    h_center_x = bolt_circle_radius
    h_center_y = 0
    cross_size = bolt_hole_radius * 1.2
    ax1.plot([h_center_x - cross_size, h_center_x + cross_size], [h_center_y, h_center_y], 'k-', lw=0.5)
    ax1.plot([h_center_x, h_center_x], [h_center_y - cross_size, h_center_y + cross_size], 'k-', lw=0.5)

    # 螺栓孔半径
    arrow_start = (h_center_x, h_center_y)
    h_angle = np.deg2rad(45) 
    arrow_end = (h_center_x + bolt_hole_radius * np.cos(h_angle), 
                h_center_y + bolt_hole_radius * np.sin(h_angle))
    ax1.annotate("", xy=arrow_end, xytext=arrow_start,
                arrowprops=dict(arrowstyle="->", color='green', lw=1.5))
    draw_box(ax1, arrow_end[0] + 2, arrow_end[1] + 2, None, f"R_bolt={bolt_hole_radius}mm", 'green', ha='left', va='bottom')
    
    ax1.set_xlim(-limit_2d, limit_2d)
    ax1.set_ylim(-limit_2d, limit_2d)
    ax1.axis('off')

    # ==========================================
    # 2. 右侧：3D 实体视图
    # ==========================================
    ax2 = fig.add_subplot(gs[0, 1], projection='3d')
    ax2.set_proj_type('ortho')

    def make_cylinder(radius, z_bottom, z_top, center_x=0, center_y=0, resolution=100):
        theta = np.linspace(0, 2*np.pi, resolution)
        z = np.linspace(z_bottom, z_top, 2)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = radius * np.cos(theta_grid) + center_x
        y_grid = radius * np.sin(theta_grid) + center_y
        return x_grid, y_grid, z_grid

    def plot_top_surface_smooth(ax, z_height):
        n_angles = 120 
        theta = np.linspace(0, 2*np.pi, n_angles)
        x_out = outer_radius * np.cos(theta)
        y_out = outer_radius * np.sin(theta)
        x_in = inner_radius * np.cos(theta)
        y_in = inner_radius * np.sin(theta)
        
        hole_xs = []
        hole_ys = []
        n_hole_pts = 40 
        theta_hole = np.linspace(0, 2*np.pi, n_hole_pts)
        
        for i in range(bolt_count):
            angle = 2 * np.pi * i / bolt_count
            bx = bolt_circle_radius * np.cos(angle)
            by = bolt_circle_radius * np.sin(angle)
            hx = bx + bolt_hole_radius * np.cos(theta_hole)
            hy = by + bolt_hole_radius * np.sin(theta_hole)
            hole_xs.extend(hx)
            hole_ys.extend(hy)
            
        x_mid = bolt_circle_radius * np.cos(theta)
        y_mid = bolt_circle_radius * np.sin(theta)
        
        all_x = np.concatenate([x_out, x_in, x_mid, np.array(hole_xs)])
        all_y = np.concatenate([y_out, y_in, y_mid, np.array(hole_ys)])
        
        triang = mtri.Triangulation(all_x, all_y)
        x_tri = all_x[triang.triangles].mean(axis=1)
        y_tri = all_y[triang.triangles].mean(axis=1)
        
        dist_from_center = np.sqrt(x_tri**2 + y_tri**2)
        mask = dist_from_center < inner_radius
        
        for i in range(bolt_count):
            angle = 2 * np.pi * i / bolt_count
            bx = bolt_circle_radius * np.cos(angle)
            by = bolt_circle_radius * np.sin(angle)
            dist_from_hole = np.sqrt((x_tri - bx)**2 + (y_tri - by)**2)
            mask = mask | (dist_from_hole < bolt_hole_radius)
            
        triang.set_mask(mask)
        ax.plot_trisurf(triang, np.full_like(all_x, z_height), color='#DDDDDD', alpha=1.0, shade=True, antialiased=False)

    x, y, z = make_cylinder(outer_radius, 0, thickness)
    ax2.plot_surface(x, y, z, color='#DDDDDD', alpha=1.0, shade=True, antialiased=False)
    
    x, y, z = make_cylinder(inner_radius, 0, thickness)
    ax2.plot_surface(x, y, z, color='#BBBBBB', alpha=1.0, shade=True, antialiased=False)

    plot_top_surface_smooth(ax2, thickness)

    for i in range(bolt_count):
        angle = 2 * np.pi * i / bolt_count
        bx = bolt_circle_radius * np.cos(angle)
        by = bolt_circle_radius * np.sin(angle)
        
        xh, yh, zh = make_cylinder(bolt_hole_radius, 0, thickness, center_x=bx, center_y=by, resolution=40)
        ax2.plot_surface(xh, yh, zh, color='#444444', alpha=1.0, shade=False) 
        
        theta_line = np.linspace(0, 2*np.pi, 60)
        ax2.plot(bx + bolt_hole_radius * np.cos(theta_line), 
                 by + bolt_hole_radius * np.sin(theta_line), 
                 thickness, color='black', linewidth=0.5)

    theta_line = np.linspace(0, 2*np.pi, 200)
    ax2.plot(outer_radius * np.cos(theta_line), outer_radius * np.sin(theta_line), thickness, 'k-', lw=1.0)
    ax2.plot(inner_radius * np.cos(theta_line), inner_radius * np.sin(theta_line), thickness, 'k-', lw=0.8)
    
    # 绘制主尺寸线 (垂直线)
    ax2.plot([outer_radius, outer_radius], [0, 0], [0, thickness], color='black', lw=1.5, zorder=100)
    # 绘制箭头 (V形和倒V形)
    arrow_wing_y = 2   # 箭头宽度
    arrow_height_z = 2    # 箭头高度
    # 下箭头
    ax2.plot([outer_radius, outer_radius, outer_radius], 
             [-arrow_wing_y, 0, arrow_wing_y], 
             [arrow_height_z, 0, arrow_height_z], 
             color='black', lw=1.5, zorder=100)
    # 上箭头
    ax2.plot([outer_radius, outer_radius, outer_radius], 
             [-arrow_wing_y, 0, arrow_wing_y], 
             [thickness - arrow_height_z, thickness, thickness - arrow_height_z], 
             color='black', lw=1.5, zorder=100)

    # 文字位置稍微偏移一点，避免压住箭头
    text_offset_y = arrow_wing_y + 10 
    draw_box(ax2, outer_radius, text_offset_y, thickness / 2, f"Thickness={thickness:.1f}mm", "black", ha='left', va='center',zorder=100)
    
    # ==========================================
    # 3. 整体效果
    # ==========================================
    ax2.set_xlim(-limit_3d, limit_3d)
    ax2.set_ylim(-limit_3d, limit_3d)
    ax2.set_zlim(0, limit_3d_z)
    ax2.set_box_aspect((2*limit_3d, 2*limit_3d, limit_3d_z)) 
    ax2.view_init(elev=30, azim=0)
    ax2.set_axis_off()

    plt.savefig(save_path)
    plt.close(fig)


class FlangeplaneInstructionGenerator(BaseInstructionGenerator):
    def __init__(self, B1_min=16, B1_max=380, thickness_min=5, thickness_max=45, pressure_min=1, pressure_max=100):
        super().__init__()

        self.B1_min = B1_min
        self.B1_max = B1_max
        self.thickness_min = thickness_min
        self.thickness_max = thickness_max
        self.pressure_min = pressure_min
        self.pressure_max = pressure_max

        self.L_min = 5
        self.bolt_count_edit_min = 4
        self.void = 1           # distance between border and bolt
        self.ratio_min = 0.4    # B1 / D

        self.mats = [
            {
                "Name": "Carbon Steel - ASTM A105",  # 碳钢法兰 (ASTM A105 - 通用型) 
                "YoungsModulus": 210000,   
                "PoissonRatio": 0.30,
                "Density": 7900,
                "price": 6
            },
            {
                "Name": "Stainless Steel 304",  # 不锈钢304法兰 (耐腐蚀型) 
                "YoungsModulus": 193000,        # 不锈钢略低于碳钢   
                "PoissonRatio": 0.29,
                "Density": 8000,                # 略高于碳钢
                "price": 16
            },
            {
                "Name": "Low Temperature Carbon Steel",  # 低温碳钢法兰 (ASTM A350 LF2 - 低温工况) 
                "YoungsModulus": 202000,                 # -20℃时的典型值   
                "PoissonRatio": 0.30,
                "Density": 7850,
                "price": 8
            },
            {
                "Name": "Gray Cast Iron",  # 铸铁法兰 (Class 150 FF典型材料) 
                "YoungsModulus": 110000,   # 显著低于钢材   
                "PoissonRatio": 0.25,
                "Density": 7200,           # 略低于钢材
                "price": 8   
            },
            {
                "Name": "Chrome-Moly Alloy Steel",  # 高温合金钢法兰 (ASTM A182 F11 - 高温工况) 
                "YoungsModulus": 203000,            # 500℃时的典型值   
                "PoissonRatio": 0.29,
                "Density": 7800,
                "price": 11
            }
        ]

    def generate_markdown_table(self):
        """
        根据 self.mats 生成 Markdown 表格字符串
        """
        # 1. 定义表头映射 (字典键 -> 表格列名)
        headers = {
            "Name": "材料名称",
            "YoungsModulus": "弹性模量 (MPa)",
            "PoissonRatio": "泊松比",
            "Density": "密度 (kg/m³)",
            "price": "单价 (¥/kg)"
        }
        
        # 2. 生成表头行
        header_row = "| " + " | ".join(headers.values()) + " |"
        
        # 3. 生成分隔线行 (例如 |---|---|)
        separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
        
        # 4. 生成数据行
        data_rows = []
        for mat in self.mats:
            row_items = []
            # 按照 headers 定义的顺序提取数据，确保列对齐
            for key in headers.keys():
                value = mat.get(key, "")
                # 特殊处理浮点数格式，使其更美观（可选）
                if isinstance(value, float):
                    row_items.append(f"{value:.2f}")
                else:
                    row_items.append(str(value))
            
            data_rows.append("| " + " | ".join(row_items) + " |")
        
        # 5. 组合所有部分
        table_str = "\n".join([header_row, separator_row] + data_rows)
        
        return table_str
        
    def case_generator(self) -> Dict[str, Any]:
        while True:
            pressure = round(random.uniform(self.pressure_min, self.pressure_max), 2)
            B1 = round(random.uniform(self.B1_min, self.B1_max), 2)

            parameters = []
            costs = []
            disp_maxs = []

            attempts = 0
            while attempts < 10:
                attempts += 1

                D = round(rand_exclusive(B1 + 2 * (self.L_min + self.L_min * self.void), B1 / self.ratio_min), 2)
                BoltCenterRadius = round(rand_exclusive(B1 + (self.L_min + self.L_min * self.void), D - (self.L_min + self.L_min * self.void)), 2)
                L = round(rand_exclusive(self.L_min, min((BoltCenterRadius - B1) / (1 + self.void), (D - BoltCenterRadius) / (1 + self.void), np.sin(np.pi / (2 * self.bolt_count_edit_min)) * BoltCenterRadius)), 2)

                max_count = np.ceil(np.pi / (2 * np.arcsin(L / BoltCenterRadius)) - 1)
                if max_count < self.bolt_count_edit_min:
                    continue 
                bolt_count_edit = random.randint(self.bolt_count_edit_min, max_count)
                bolt_count_edit = bolt_count_edit // 2 * 2

                thickness = round(random.uniform(self.thickness_min, self.thickness_max), 2)

                mat = random.choice(self.mats)

                PAYLOAD = {
                            "D": D,
                            "B1": B1,
                            "L": L,
                            "BoltCenterRadius": BoltCenterRadius,
                            "thickness": thickness, 
                            "bolt_count_edit": bolt_count_edit,
                            "Name": mat["Name"],
                            "YoungsModulus": mat["YoungsModulus"], 
                            "PoissonRatio": mat["PoissonRatio"],
                            "Density": mat["Density"],
                            "pressure": pressure
                }

                try:           
                    response = requests.post(f"{random.choice(ips)}/cae_analysis", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=200)     
                except requests.exceptions.RequestException as e:
                    print(f"Request failed, {e}")
                    continue

                if not response.ok:
                    print(f"Server returned status {response.status_code}")
                    continue

                try:
                    result = response.json()
                except ValueError:
                    print(f"Response is not json format, {response.text}")
                    continue

                if not result["success"]:
                    print(result["info"])
                    continue

                cost = cost_analysis(thickness, D, B1, bolt_count_edit, L, mat["Density"], mat["price"])

                parameters.append({
                            "D": D,
                            "B1": B1,
                            "L": L,
                            "BoltCenterRadius": BoltCenterRadius,
                            "thickness": thickness, 
                            "bolt_count_edit": bolt_count_edit,
                            "mat": mat,
                            "pressure": pressure
                        })
                costs.append(cost)
                disp_maxs.append(result["disp_max"] + result["unit"])

                if len(costs) == 2:
                    break

            if len(costs) < 2:
                continue
            src_idx = np.argmin(disp_maxs)

            filename = str(uuid.uuid4())
            image_path = os.path.join(PATH, f"data/flangeplane_bootcamp/images/{filename}.jpg")
            plot_flange_combined_view(parameters[src_idx]["D"], parameters[src_idx]["B1"], parameters[src_idx]["thickness"], parameters[src_idx]["BoltCenterRadius"], parameters[src_idx]["L"], parameters[src_idx]["bolt_count_edit"], image_path)

            cost = cost_analysis(parameters[1 - src_idx]["thickness"], parameters[1 - src_idx]["D"], parameters[1 - src_idx]["B1"], parameters[1 - src_idx]["bolt_count_edit"], parameters[1 - src_idx]["L"], parameters[1 - src_idx]["mat"]["Density"], parameters[1 - src_idx]["mat"]["price"])
            
            return {
                "B1": B1,
                "pressure": pressure,
                "Name": mat["Name"],
                "disp_max": disp_maxs[1 - src_idx],
                "cost": cost,
                "mats": self.mats,
                "image_path": image_path
            }

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        mat_table = self.generate_markdown_table()
        prompts = [
f"""
你是一名机械结构优化工程师，任务是针对一种“平板法兰”进行结构与材料协同优化设计。

【问题背景】
    平板法兰的密封面为完全平面（无突面或凹面），广泛应用于低压或非严苛工况管道系统中。现需在满足性能与成本双重约束的前提下，优化其几何与材料参数。

【设计目标】
    请通过迭代参数使得：
    1. 最大节点位移模量 |u|_max = √(dx² + dy² + dz²) 不超过 {identity["disp_max"]} μm
    2. 总耗材成本 ≤ ¥{identity["cost"]}

【初始设计方案】
    - 几何尺寸：请参考附图中的法兰几何参数（含外径、内径、螺栓孔径、分布圆半径及厚度等）。
    - 初始材料：{identity["Name"]}  

【可调参数范围】
    ✅ 允许调整：
    - 外圆半径
    - 螺栓孔半径
    - 螺栓孔数量
    - 螺栓孔分布圆周半径
    - 法兰厚度
    - 材料（可从候选材料库中切换至其他材料）

    ❌ 禁止更改：
    - 内圆半径
    - 内压载荷

【候选材料库】
{mat_table}

【边界条件与载荷】
    - 约束：外圆柱面所有自由度固定（u = 0）
    - 载荷：内圆柱面施加均匀内压 {identity["pressure"]} MPa（径向膨胀）

【分析假设】
    - 线弹性、小变形、静态分析、材料各向同性
    - 忽略自重、螺栓预紧力、接触非线性、温度效应、制造残余应力、动载、腐蚀减薄等次要因素

【可用工具】
    1. 有限元应力分析工具：cae_analysis
    2. 成本计算工具：cost_cal

【输出要求】
    ★ 必须严格遵循以下 JSON 格式输出最终优化参数：
    ```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

    示例:
    ```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

    ⚠️ 注意：
    - 所有数值字段必须为具体数字（浮点或整数），不可用变量名或表达式；
    - 材料名称必须与候选列表完全一致（区分大小写）；
    - 不得输出多个结果，仅返回最优可行解；

现在请从初始设计方案出发，执行优化任务。
""",
f"""
你是一名机械结构优化工程师，现需对一种“平板法兰”开展几何-材料协同优化，在满足性能与成本双约束的前提下输出最终参数。

【设计目标】
1) 最大节点位移模量：|u|_max = √(dx² + dy² + dz²) <= {identity["disp_max"]} μm
2) 总耗材成本：cost ≤ ¥{identity["cost"]}

【初始输入（来自当前方案）】
- 几何参数：具体数值（如外径、孔径、厚度等）如图所示。
- 初始材料：{identity["Name"]}

【可调参数】
- 外圆半径
- 螺栓孔半径
- 螺栓孔数量
- 螺栓孔分布圆周半径
- 法兰厚度
- 材料（可在候选库中切换）

【固定不变】
- 内圆半径
- 内压载荷

【候选材料库】
{mat_table}

【边界与载荷】
- 约束：外圆柱面所有自由度固定（u = 0）
- 载荷：内圆柱面施加均匀内压 {identity["pressure"]} MPa（径向膨胀）

【分析假设】
- 线弹性，小变形，静态，各向同性
- 忽略自重、螺栓预紧、接触非线性、温度、残余应力、动载、腐蚀减薄

【当前支持工具】
- 应力分析 (cae_analysis)
- 成本核算 (cost_cal)

【输出要求（严格遵循）】
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

请从上述初始方案出发执行优化。
""",
f"""
你将扮演机械结构优化工程师，对“平板法兰”进行设计优化，以在位移与成本两方面同时达标。

一、目标与阈值
- 位移约束：最大节点位移 |u|_max = √(dx² + dy² + dz²) 必须小于或等于 {identity["disp_max"]} μm
- 成本约束：总材料成本 cost ≤ ¥{identity["cost"]}

二、给定的初始方案
- 几何定义：法兰的各部分几何尺寸（半径、孔数、厚度等）详见附图。
- 初始材料：{identity["Name"]}

三、可变设计变量
- 外圆半径、螺栓孔半径、螺栓孔数量、螺栓孔分布圆周半径、法兰厚度、材料（限定于材料库）

四、固定条件（不可更改）
- 内圆半径、内压载荷

五、材料候选库
{mat_table}

六、边界与载荷
- 约束：外圆柱面全约束（u=0）
- 载荷：内圆柱面承受均匀内压 {identity["pressure"]} MPa（向外膨胀）

七、分析假设
- 线弹性、小变形、静态、各向同性
- 忽略重力、预紧、接触非线性、温度、残余应力、动载、腐蚀减薄

八、工具箱
    你可以使用以下两个工具来辅助任务：首先是 cae_analysis，用于进行有限元应力分析；其次是 cost_cal，专门用于计算成本。

九、输出格式（唯一且严格）
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

开始从初始方案执行优化并给出唯一最优可行解。
""",
f"""
角色：你是机械结构优化工程师。对象：平板法兰。目标：在保证性能与成本达标的条件下完成几何与材料的联合优化。

A. 指标目标
- |u|_max = √(dx² + dy² + dz²) <= {identity["disp_max"]} μm
- cost ≤ ¥{identity["cost"]}

B. 初始配置
- 几何参数：法兰的几何参数如图中所示。
- 初始材料：{identity["Name"]}

C. 可调整变量
- 外圆半径、螺栓孔半径、螺栓孔数量、螺栓孔分布圆周半径、法兰厚度、材料（限候选库）

D. 不可改变
- 内圆半径
- 内压载荷

E. 材料库（可切换）
{mat_table}

F. 载荷与约束
- 外圆柱面：全约束（u=0）
- 内圆柱面：均匀内压 {identity["pressure"]} MPa（径向膨胀）

G. 分析假设
- 线弹性、小变形、静态、各向同性
- 忽略自重、预紧、接触非线性、温度、残余应力、动载、腐蚀减薄

H. 可用工具
- 有限元应力分析工具：cae_analysis
- 成本计算工具：cost_cal

I. 输出（严格）
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

请据此开展优化并输出唯一结果。
""",
f"""
任务说明：以“平板法兰”为对象，开展几何与材料的协同优化，使位移控制与成本控制同时满足约束。

[关键目标]
- 最大节点位移模：|u|_max = √(dx² + dy² + dz²) 小于或等于 {identity["disp_max"]} μm
- 成本：cost ≤ ¥{identity["cost"]}

[初始方案参数]
- 几何数据：请参阅图示中的法兰几何参数。
- 初始材料：{identity["Name"]}

[可调整项]
- 外圆半径/螺栓孔半径/螺栓孔数量/螺栓孔分布圆周半径/法兰厚度/材料（材料需来自候选库）

[锁定项]
- 内圆半径/内压载荷

[材料候选库]
{mat_table}

[边界条件]
- 外圆柱面：u = 0 全约束
- 内圆柱面：承受 {identity["pressure"]} MPa 均匀内压

[分析前提]
- 线弹性、小变形、静态、各向同性
- 忽略自重、螺栓预紧、接触非线性、温度效应、残余应力、动载与腐蚀减薄

[工具]
你可以使用以下两个工具来辅助任务：首先是 cae_analysis，用于进行有限元应力分析；其次是 cost_cal，专门用于计算成本。

[输出规范]
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

请据此开始优化。
""",
f"""
背景：我们要对一款“平板法兰”实施双约束优化设计，输出一个满足位移上限与成本上限的参数组合。

I. 目标函数与约束
- 最大节点位移模：|u|_max = √(dx² + dy² + dz²) <= {identity["disp_max"]} μm
- 成本上限：cost ≤ ¥{identity["cost"]}

II. 初始设计（给定）
- 几何信息：法兰的几何参数如图中所示。
- 初始材料与属性：{identity["Name"]}

III. 可优化设计变量
- 外圆半径、螺栓孔半径、螺栓孔数量、螺栓孔分布圆周半径、法兰厚度、材料（限材料库）

IV. 固定约束
- 内圆半径、内压载荷

V. 材料候选（价格/性能权衡）
{mat_table}

VI. 载荷与边界
- 外圆柱面：u=0 全约束
- 内圆柱面：均匀内压 {identity["pressure"]} MPa

VII. 分析前提
- 线弹性、小变形、静态、各向同性
- 忽略自重、预紧、接触非线性、温度、残余应力、动载、腐蚀

VIII. 当前支持工具
- 应力分析 (cae_analysis)
- 成本核算 (cost_cal)

IX. 输出限定
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

立即开始优化。
""",
f"""
项目：平板法兰“结构-材料”一体化优化。

目标约束
- 最大节点位移模：|u|_max = √(dx² + dy² + dz²) <= {identity["disp_max"]} μm
- 成本上限：cost ≤ ¥{identity["cost"]}

原始参数
- 几何尺寸：请查看附图以获取法兰的初始几何参数。
- 初始材料：{identity["Name"]}

可调整清单
- 外圆半径 / 螺栓孔半径 / 螺栓孔数量 / 螺栓孔分布圆周半径 / 法兰厚度 / 材料（限本材料库）

禁止修改
- 内圆半径 / 内压载荷

候选材料库
{mat_table}

边界与载荷设置
- 外圆柱面全约束（u=0）
- 内圆柱面均匀内压 {identity["pressure"]} MPa

分析假设
- 线弹性、小变形、静态、各向同性
- 忽略：自重、预紧、接触非线性、温度、残余应力、动载、腐蚀减薄

工具定义
1. cae_analysis: 有限元应力分析工具
2. cost_cal: 成本计算工具

输出（严格且唯一）
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

开始优化并给出最终唯一解。
""",
f"""
职责：作为机械结构优化工程师，请对“平板法兰”进行面向约束的优化设计。

目标边界
- 最大节点位移模：|u|_max = √(dx² + dy² + dz²) <= {identity["disp_max"]} μm
- 成本：cost ≤ ¥{identity["cost"]}

初始输入参数
- 几何规格：法兰的几何参数如图中所示。
- 材料：{identity["Name"]}

可变项
- 外圆半径 / 螺栓孔半径 / 螺栓孔数量 / 螺栓孔分布圆周半径 / 厚度 / 材料（材料需来自材料库）

锁定项
- 内圆半径 / 内压载荷

材料库（可选）
{mat_table}

边界与载荷
- 外圆柱面：完全固定（u=0）
- 内圆柱面：施加 {identity["pressure"]} MPa 均匀内压（径向膨胀）

假设
- 线弹性，小变形，静态，各向同性
- 忽略自重、预紧、接触非线性、温度、残余应力、动载、腐蚀

工具定义
- cae_analysis: 有限元应力分析工具
- cost_cal: 成本计算工具

输出格式（强制）
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```

请按上述要求执行优化。
""",
f"""
角色：优化工程师
对象：平板法兰

待核对的输入
- 几何参数：如图所示（含外径、内径、孔径、孔数、厚度等）。
- 材料={identity["Name"]}
- 内压={identity["pressure"]} MPa

目标核对
- |u|_max <= {identity["disp_max"]} μm → 满足/不满足
- cost ≤ ¥{identity["cost"]} → 满足/不满足

可调项（勾选所用）
- [ ] 外圆半径
- [ ] 螺栓孔半径
- [ ] 螺栓孔数量
- [ ] 螺栓孔分布圆周半径
- [ ] 厚度
- [ ] 材料（仅限材料库）

禁改项
- 内圆半径
- 内压

材料库（从中选择）
{mat_table}

边界与载荷核对
- 外圆柱面：u=0
- 内圆柱面：均匀内压 {identity["pressure"]} MPa

分析假设核对
- 线弹性、小变形、静态、各向同性；忽略自重、预紧、接触、温度、残余应力、动载、腐蚀减薄。

可用工具
- 有限元应力分析工具：cae_analysis
- 成本计算工具：cost_cal

输出核对
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```
""",
f"""
任务：你将接收一组平板法兰初始参数，并在给定约束下完成几何与材料的联合优化。

Q1: 我需要满足哪些硬性指标？
- A1: |u|_max <= {identity["disp_max"]} μm；cost ≤ ¥{identity["cost"]}。

Q2: 初始输入有哪些？
- A2:
  - 几何参数：法兰的几何参数如图中所示。
  - 材料 {identity["Name"]}
  - 内压 {identity["pressure"]} MPa

Q3: 我可以改动什么？
- A3: 外圆半径、螺栓孔半径、螺栓孔数量、螺栓孔分布圆周半径、厚度、材料（候选库内切换）。

Q4: 不允许更改什么？
- A4: 内圆半径、内压。

Q5: 候选材料有哪些？
{mat_table}

Q6: 边界条件和载荷？
- A6: 外圆柱面全固定（u=0）；内圆柱面承受均匀内压 {identity["pressure"]} MPa。

Q7: 分析假设？
- A7: 线弹性、小变形、静态、各向同性；忽略自重、预紧、接触、温度、残余应力、动载、腐蚀减薄。

Q8: 工具支持？
- A8:
  1) cae_analysis：有限元应力分析
  2) cost_cal：成本计算

最终交付：
```json{{"外圆半径(mm)": <float>, "螺栓孔半径(mm)": <float>, "螺栓孔数目": <int>, "螺栓孔圆心分布的圆周半径(mm)": <float>, "厚度(mm)": <float>, "材料": 材料名称}}```

示例:
```json{{"外圆半径(mm)": 40.0, "螺栓孔半径(mm)": 5.0, "螺栓孔数目": 4, "螺栓孔圆心分布的圆周半径(mm)": 30.0, "厚度(mm)": 6.0, "材料": \"Gray Cast Iron\"}}```
"""
]
        return {
            "prompt_txt": random.choice(prompts),
            "prompt_img": identity["image_path"]
            }
