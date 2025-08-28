from ..base import Basebootcamp
from .DeepCAD.Edit_plain.parameter_editor import step_generation, cae_analysis, frd_extract

import random
import numpy as np
import re # 625行，extract函数需调用

def rand_exclusive(a, b):
    return a + (b - a) * random.random()


class Flangeplanebootcamp(Basebootcamp):
    def __init__(self, D_min=40, D_max=400, thickness_min=5, thickness_max=45, pressure_min=1, pressure_max=100):
        self.D_min = D_min
        self.D_max = D_max
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
                "Density": 7900
            },
            {
                "Name": "Stainless Steel 304",  # 不锈钢304法兰 (耐腐蚀型) 
                "YoungsModulus": 193000,  # 不锈钢略低于碳钢   
                "PoissonRatio": 0.29,
                "Density": 8000  # 略高于碳钢
            },
            {
                "Name": "Low Temperature Carbon Steel",  # 低温碳钢法兰 (ASTM A350 LF2 - 低温工况) 
                "YoungsModulus": 202000,  # -20℃时的典型值   
                "PoissonRatio": 0.30,
                "Density": 7850
            },
            {
                "Name": "Gray Cast Iron",  # 铸铁法兰 (Class 150 FF典型材料) 
                "YoungsModulus": 110000,  # 显著低于钢材   
                "PoissonRatio": 0.25,
                "Density": 7200  # 略低于钢材
            },
            {
                "Name": "Chrome-Moly Alloy Steel",  # 高温合金钢法兰 (ASTM A182 F11 - 高温工况) 
                "YoungsModulus": 203000,  # 500℃时的典型值   
                "PoissonRatio": 0.29,
                "Density": 7800
            }
        ]

    def case_generator(self):
        pressure = random.uniform(self.pressure_min, self.pressure_max)
        thickness = random.uniform(self.thickness_min, self.thickness_max)
        D = random.uniform(self.D_min, self.D_max)
        B1 = rand_exclusive(self.ratio_min * D, 
                            D - 2 * (self.L_min + self.L_min * self.void))
        BoltCenterRadius = rand_exclusive(B1 + (self.L_min + self.L_min * self.void), 
                                          D - (self.L_min + self.L_min * self.void))
        L = rand_exclusive(self.L_min, min((BoltCenterRadius - B1) / (1 + self.void), 
                                           (D - BoltCenterRadius) / (1 + self.void), 
                                           np.sin(np.pi / self.bolt_count_edit_min) * BoltCenterRadius))
        bolt_count_edit = random.randint(self.bolt_count_edit_min, np.ceil(np.pi / np.arcsin(L / BoltCenterRadius) - 1))
        bolt_count_edit = bolt_count_edit // 2 * 2

        mat = random.choice(self.mats)
        
        return {
            'pressure': pressure,
            'thickness': thickness,
            'D': D,
            'B1': B1,
            'L': L,
            'BoltCenterRadius': BoltCenterRadius,
            'bolt_count_edit': bolt_count_edit,

            "Name": mat["Name"],
            "YoungsModulus": mat["YoungsModulus"], 
            "PoissonRatio": mat["PoissonRatio"],
            "Density": mat["Density"]
        }

    def prompt_func(self, identity):
        prompts = [
f"""
“平板法兰”是工业管道系统中常见的法兰型式，其密封面完全为平面（既无突面也无凹面）。
你是一名机械结构分析工程师。请对以下参数的平板法兰进行线弹性静力分析，并给出最大节点位移模 |u|_max = √(dx² + dy² + dz²) 的数值（单位：μm）。

★ 重要：若未严格按照“五、输出格式”给出结果，答案视为无效。

一、坐标系（右手系）
    • origin: {{ "x": 0.0, "y": 0.0, "z": 0.0 }}
    • x_axis: {{ "x": 1.0, "y": 0.0, "z": 0.0 }}
    • y_axis: {{ "x": 0.0, "y": 0.0, "z": 1.0 }}
    • z_axis: {{ "x": 0.0, "y": -1.0, "z": 0.0 }}

二、几何建模 - 平板法兰
    1. 草图（位于 origin，法向量 +z_axis)
        • 外径圆：半径 = {identity["D"]} mm  
        • 内径圆：半径 = {identity["B1"]} mm  
        • 螺栓孔：半径 = {identity["L"]} mm  
            - 孔数 = {identity["bolt_count_edit"]}  
            - 圆心均布在半径 {identity["BoltCenterRadius"]} mm 的圆周上
    2. 拉伸：沿 +z_axis 一次性等厚拉伸，厚度 = {identity["thickness"]} mm
    3. 材料：{identity["Name"]}  
        • Young’s Modulus = {identity["YoungsModulus"]} MPa  
        • Poisson Ratio   = {identity["PoissonRatio"]}  
        • Density         = {identity["Density"]} kg/m³

三、边界条件与载荷
    • 固定：外径圆柱面各自由度完全约束（u = 0）   
    • 载荷：内径圆柱面施加均匀“内压” {identity["pressure"]} MPa（膨胀载荷）

四、分析假设
    • 线弹性、小变形、静态、各向同性
    • 忽略次要载荷：自重、螺栓预紧力、垫片压缩、接触非线性、温度载荷、热膨胀失配、制造残余应力、外部弯矩/轴向力、扭矩、动载/冲击、地震/风、疲劳循环、腐蚀减薄、浸没/流体浮力、磁力/电力、高压试验、运输/吊装

五、输出格式（务必严格遵守）
    最终答案仅一行，\\boxed{{数值}} μm
    示例：\\boxed{{1}} μm
""",
f"""
“平板法兰”属于工业管路常见连接件，其密封面完全平坦（无突面 / 无凹槽）。
你是一位机械结构分析工程师，请对下列输入参数的平板法兰做小变形线弹性静力分析，并给出最大节点位移模 |u|_max = √(dx² + dy² + dz²)（单位：μm）。

★ 重要提醒：若结果未严格按照“五、输出格式”呈现，答案一律判定为无效。

一、坐标系（右手系）
    • origin  : {{ "x": 0.0, "y": 0.0, "z": 0.0 }}
    • x_axis  : {{ "x": 1.0, "y": 0.0, "z": 0.0 }}
    • y_axis  : {{ "x": 0.0, "y": 0.0, "z": 1.0 }}
    • z_axis  : {{ "x": 0.0, "y":-1.0, "z": 0.0 }}

二、几何建模
    1) 草图放置于 origin，法向 +z_axis  
       • 外径圆半径 = {identity["D"]} mm 
       • 内径圆半径 = {identity["B1"]} mm  
       • 螺栓孔半径 = {identity["L"]} mm  
         - 孔数 = {identity["bolt_count_edit"]}  
         - 圆心均布在半径 {identity["BoltCenterRadius"]} mm 的圆周上
    2) 沿 +z_axis 一次性拉伸，厚度 = {identity["thickness"]} mm
    3) 材料：{identity["Name"]}  
       • E  = {identity["YoungsModulus"]} MPa  
       • ν  = {identity["PoissonRatio"]}  
       • ρ  = {identity["Density"]} kg/m³

三、边界与载荷
    • 约束：外径圆柱面全固定（u = 0）  
    • 荷载：内径圆柱面均布内压 {identity["pressure"]} MPa

四、分析假设
    • 线弹性、小变形、静载、各向同性  
    • 忽略：自重、预紧力、垫片、接触、温度、残余应力、外部力矩 / 轴力、扭矩、动载、地震、疲劳、腐蚀、浮力、磁力、电力、试压、运输等

五、输出格式（务必遵守）
    最终答案仅保留一行：\\boxed{{数值}} μm  
    例：\\boxed{{1}} μm
""",
f"""
作为机械结构分析领域的工程师，您被委派对一种典型的“平板法兰”执行理论静力分析任务。该法兰属于工业管道系统中常见的连接部件，其密封面为完全平面（无突台或凹槽）。

请完成如下线弹性静力分析，并计算最大节点位移模量 |u|_max = √(dx² + dy² + dz²)，结果以微米（μm）为单位。

【坐标系统定义】（右手笛卡尔坐标系）
- 原点 origin: (0.0, 0.0, 0.0)
- x 轴方向: (1.0, 0.0, 0.0)
- y 轴方向: (0.0, 0.0, 1.0)
- z 轴方向: (0.0, -1.0, 0.0)

【几何构型】
- 法兰草图位于原点平面，法向沿 +z 轴
  - 外径圆半径: {identity["D"]} mm
  - 内径圆半径: {identity["B1"]} mm
  - 螺栓孔数量: {identity["bolt_count_edit"]}，均布于半径为 {identity["BoltCenterRadius"]} mm 的圆周上
  - 单个螺栓孔半径: {identity["L"]} mm
- 沿 +z 轴方向整体拉伸成型，厚度为 {identity["thickness"]} mm

【材料属性】
- 名称: {identity["Name"]}
- 弹性模量: {identity["YoungsModulus"]} MPa
- 泊松比: {identity["PoissonRatio"]}
- 密度: {identity["Density"]} kg/m³

【边界与载荷条件】
- 边界：外径圆柱面上所有自由度固定（位移为零）
- 载荷：内径圆柱面承受均匀内压 {identity["pressure"]} MPa（导致结构膨胀）

【分析前提】
- 线弹性、小变形、静态平衡、材料各向同性
- 忽略以下次要因素：自重、螺栓预紧力、垫片作用、接触非线性、温度效应、热膨胀差异、残余应力、外部弯矩/轴向力/扭矩、动态载荷、地震风载、疲劳、腐蚀减薄、流体浮力、电磁力、水压试验、运输载荷

【输出要求】（必须严格遵守）
最终答案仅允许输出一行，格式如下：
\\boxed{{计算结果}} μm
例如：\\boxed{{5}} μm
""",
f"""
你现在担任一名资深机械结构工程师，需完成一项纯理论分析任务：对一个“平板法兰”进行线弹性静力学解析。

目标：求出最大节点位移模 |u|_max = √(dx² + dy² + dz²)，单位为 μm。

请按以下步骤处理：

1. 【坐标系】采用右手系：
   - 原点: (0,0,0)
   - x轴: (1,0,0)
   - y轴: (0,0,1)
   - z轴: (0,-1,0)

2. 【几何建模】
   - 草图位于原点，垂直于 +z 轴
     - 外径 = {identity["D"]} mm
     - 内径 = {identity["B1"]} mm
     - 螺栓孔数 = {identity["bolt_count_edit"]}，中心分布于半径 {identity["BoltCenterRadius"]} mm 的圆周
     - 单孔半径 = {identity["L"]} mm
   - 沿 +z 方向等厚拉伸，总厚度 = {identity["thickness"]} mm

3. 【材料信息】
   - 材料名: {identity["Name"]}
   - 弹性模量 E = {identity["YoungsModulus"]} MPa
   - 泊松比 ν = {identity["PoissonRatio"]}
   - 密度 ρ = {identity["Density"]} kg/m³

4. 【边界与加载】
   - 外圆柱面全约束（u=0）
   - 内圆柱面施加均匀内压 p = {identity["pressure"]} MPa

5. 【理想化假设】
   - 线弹性、小变形、静态、各向同性
   - 忽略重力、螺栓力、垫片、接触非线性、温度变化、残余应力、外加载荷（弯矩/轴力/扭矩）、动载、腐蚀、浮力、电磁效应等

6. 【输出格式】（极其重要）
   必须严格符合：
   \\boxed{{数值}} μm
   示例：\\boxed{{3}} μm
   其他任何形式均视为无效。
""",
f"""
假设你是一位精通弹性力学的机械工程师，现在需要解决以下问题：

问题：一个“平板法兰”在承受内压时的最大位移是多少？

已知该法兰具有完全平面密封面，无突面或凹面结构。

请思考并回答下列要素：

- 坐标系是右手系：
  - 原点 (0,0,0)
  - x轴指向 (1,0,0)
  - y轴指向 (0,0,1)
  - z轴指向 (0,-1,0)

- 几何参数：
  - 外径半径: {identity["D"]} mm
  - 内径半径: {identity["B1"]} mm
  - 螺栓孔数: {identity["bolt_count_edit"]}，分布在半径 {identity["BoltCenterRadius"]} mm 的圆上
  - 每个螺栓孔半径: {identity["L"]} mm
  - 沿 +z 轴方向拉伸，厚度为 {identity["thickness"]} mm

- 材料特性：
  - 名称: {identity["Name"]}
  - 弹性模量: {identity["YoungsModulus"]} MPa
  - 泊松比: {identity["PoissonRatio"]}
  - 密度: {identity["Density"]} kg/m³

- 加载情况：
  - 外圆柱面完全固定
  - 内圆柱面受均匀内压 {identity["pressure"]} MPa

- 分析假设：
  - 线弹性、小变形、静态、各向同性
  - 忽略自重、螺栓预紧、垫片、接触非线性、温度影响、残余应力、外部载荷、动态效应、腐蚀等

基于以上条件，请推导并给出最大位移模长 |u|_max = √(dx² + dy² + dz²) 的理论估算值（单位 μm）。

⚠️ 注意：答案必须且只能以如下格式呈现：
\\boxed{{你的答案}} μm
例如：\\boxed{{7}} μm
其他格式将被判定为错误。
""",
f"""
请根据以下全部信息，对“平板法兰”执行一次线弹性静力分析，并返回最大节点位移模量（单位：μm）。

🔧 核心任务：
计算 |u|_max = √(dx² + dy² + dz²) 的理论值

📐 坐标系统（右手系）：
- 原点：(0.0, 0.0, 0.0)
- x轴：(1.0, 0.0, 0.0)
- y轴：(0.0, 0.0, 1.0)
- z轴：(0.0, -1.0, 0.0)

📏 几何描述：
- 构造平面：过原点，法向为 +z 轴
- 外圆半径：{identity["D"]} mm
- 内圆半径：{identity["B1"]} mm
- 螺栓孔：共 {identity["bolt_count_edit"]} 个，中心位于半径 {identity["BoltCenterRadius"]} mm 的圆周，单孔半径 {identity["L"]} mm
- 成型方式：沿 +z 轴一次性拉伸，厚度 {identity["thickness"]} mm

⚙️ 材料属性：
- 名称：{identity["Name"]}
- 弹性模量：{identity["YoungsModulus"]} MPa
- 泊松比：{identity["PoissonRatio"]}
- 密度：{identity["Density"]} kg/m³

📌 边界与载荷：
- 约束：外圆柱面全固定（u = 0）
- 载荷：内圆柱面施加均匀内压 {identity["pressure"]} MPa

🧩 理想化假设：
- 线弹性、小变形、静态、各向同性
- 忽略：自重、螺栓预紧、垫片压缩、接触非线性、温度效应、残余应力、外部弯矩/轴力/扭矩、动载、腐蚀、浮力、电磁力、水压试验、运输载荷

📤 输出规范（必须严格遵守）：
最终输出格式为：
\\boxed{{数值}} μm
例如：\\boxed{{2}} μm
任何格式错误将导致答案无效。
""",
f"""
嘿，现在你是个懂弹性力学的结构工程师。咱们来干个纯理论活儿：分析一个“平板法兰”在内压下的最大位移。

这个法兰长啥样？

- 密封面是平的，没凸台也没凹槽
- 坐标系是右手的：
  - 原点在 (0,0,0)
  - x轴朝 (1,0,0)
  - y轴朝 (0,0,1)
  - z轴朝 (0,-1,0)

几何尺寸：
- 外径半径：{identity["D"]} mm
- 内径半径：{identity["B1"]} mm
- 螺栓孔有 {identity["bolt_count_edit"]} 个，均匀分布在半径 {identity["BoltCenterRadius"]} mm 的圆上，每个孔半径 {identity["L"]} mm
- 整体厚度是 {identity["thickness"]} mm，沿 +z 方向拉出来的

材料是 {identity["Name"]}：
- 弹性模量 {identity["YoungsModulus"]} MPa
- 泊松比 {identity["PoissonRatio"]}
- 密度 {identity["Density"]} kg/m³

怎么加载的？
- 外圈圆柱面焊死了，不能动（全约束）
- 内圈受均匀内压 {identity["pressure"]} MPa，往外胀

假设很理想：
- 线弹性、小变形、静态、各向同性
- 忽掉重力、螺栓力、温度、残余应力、弯矩、冲击、腐蚀……全都忽略

你要算的是最大位移大小 |u|_max = √(dx² + dy² + dz²)，单位是 μm。

⚠️ 最后输出这一行：
\\boxed{{你的答案}} μm
比如 \\boxed{{4}} μm
""",
f"""
请你以机械结构分析工程师的身份，逐步推理并求解如下问题：

已知一个“平板法兰”（密封面为完整平面），在仅受内压作用下，其最大节点位移模量是多少？

分析条件如下：

【第1步：坐标系统】
使用右手笛卡尔坐标系：
- origin: (0,0,0)
- x_axis: (1,0,0)
- y_axis: (0,0,1)
- z_axis: (0,-1,0)

【第2步：几何建模】
- 草图位于 origin，法向 +z
  - 外圆半径 = {identity["D"]} mm
  - 内圆半径 = {identity["B1"]} mm
  - 螺栓孔：数量 {identity["bolt_count_edit"]}，分布圆半径 {identity["BoltCenterRadius"]} mm，单孔半径 {identity["L"]} mm
- 沿 +z 轴拉伸，厚度 = {identity["thickness"]} mm

【第3步：材料参数】
- 名称：{identity["Name"]}
- E = {identity["YoungsModulus"]} MPa
- ν = {identity["PoissonRatio"]}
- ρ = {identity["Density"]} kg/m³

【第4步：边界与载荷】
- 外圆柱面：全自由度约束（u = 0）
- 内圆柱面：施加均匀内压 = {identity["pressure"]} MPa

【第5步：简化假设】
- 线弹性、小变形、静态、各向同性
- 忽略所有次要效应：自重、预紧力、垫片、接触、温度、残余应力、外部载荷、动态、腐蚀等

【最终输出】
请输出最大位移模 |u|_max = √(dx² + dy² + dz²) 的数值（单位 μm），格式必须为：
\\boxed{{数值}} μm
示例：\\boxed{{6}} μm
违反格式即视为错误。
""",
f"""
研究课题：基于经典弹性力学的平板法兰位移场分析

1. 引言
平板法兰是一种标准管道连接元件，其特征是密封表面呈完全平面形态，不含任何凸起或凹陷结构。本分析旨在确定结构的最大节点位移模 |u|_max = √(dx² + dy² + dz²)，结果以微米（μm）为单位表示。

重要提示：计算结果必须严格遵循第6节规定的格式，否则将被视为无效。

2. 参考坐标系（右手系）
- 坐标原点：{{ "x": 0.0, "y": 0.0, "z": 0.0 }}
- X轴单位向量：{{ "x": 1.0, "y": 0.0, "z": 0.0 }}
- Y轴单位向量：{{ "x": 0.0, "y": 0.0, "z": 1.0 }}
- Z轴单位向量：{{ "x": 0.0, "y": -1.0, "z": 0.0 }}

3. 结构几何描述
3.1 基准草图构建（位于坐标原点，法线方向为+z_axis）
    - 外轮廓圆：半径 = {identity["D"]} mm
    - 内孔圆：半径 = {identity["B1"]} mm
    - 螺栓通孔配置：
      * 单孔半径 = {identity["L"]} mm
      * 孔位数量 = {identity["bolt_count_edit"]}
      * 分布圆半径 = {identity["BoltCenterRadius"]} mm（周向均布）
3.2 三维实体生成：草图沿+z_axis方向拉伸，拉伸距离 = {identity["thickness"]} mm
3.3 材料参数（{identity["Name"]}）：
    - 弹性模量 E = {identity["YoungsModulus"]} MPa
    - 泊松比 ν = {identity["PoissonRatio"]}
    - 材料密度 ρ = {identity["Density"]} kg/m³

4. 边界条件设置
- 位移边界：外圆柱表面施加全约束（u = v = w = 0）
- 载荷边界：内圆柱表面承受均匀压力载荷 p = {identity["pressure"]} MPa（径向向外）

5. 分析假设与简化
- 基本假设：线弹性本构、小变形理论、准静态响应、材料各向同性
- 忽略效应：体力、螺栓预载、垫片作用、接触非线性、温度场、热应变、初始应力、外力矩、轴力、扭矩、动载荷、冲击、环境载荷、循环载荷、材料退化、流体作用、电磁场、试验载荷、装配载荷

6. 输出格式要求
结果表示：\\boxed{{数值}} μm
格式示例：\\boxed{{1}} μm
""",
f"""
任务：平板法兰线弹性静力分析

定义：
- 平板法兰：工业管道系统连接件，密封面为纯平面（无突面、无凹面）
- 分析目标：求解最大节点位移模 |u|_max = √(dx² + dy² + dz²) [单位：μm]

⚡ 警告：输出必须严格遵守指定格式，否则答案无效

═══ 输入参数 ═══

1. 坐标系参数（右手坐标系）
   └─ 原点：{{ "x": 0.0, "y": 0.0, "z": 0.0 }}
   └─ X轴：{{ "x": 1.0, "y": 0.0, "z": 0.0 }}
   └─ Y轴：{{ "x": 0.0, "y": 0.0, "z": 1.0 }}
   └─ Z轴：{{ "x": 0.0, "y": -1.0, "z": 0.0 }}

2. 几何模型
   2.1 二维草图（原点处，法向+z_axis）
       └─ 外圆：R = {identity["D"]} mm
       └─ 内圆：R = {identity["B1"]} mm
       └─ 螺栓孔阵列：
           └─ 孔径：R = {identity["L"]} mm
           └─ 数量：{identity["bolt_count_edit"]}
           └─ 位置：均布于R = {identity["BoltCenterRadius"]} mm 圆周
   2.2 三维生成：沿+z_axis拉伸，高度 = {identity["thickness"]} mm
   2.3 材料定义：{identity["Name"]}
       └─ E = {identity["YoungsModulus"]} MPa（弹性模量）
       └─ ν = {identity["PoissonRatio"]}（泊松比）
       └─ ρ = {identity["Density"]} kg/m³（密度）

3. 力学边界
   └─ 约束：外圆柱面全约束（u = 0）
   └─ 载荷：内圆柱面均布内压 = {identity["pressure"]} MPa

4. 分析设定
   └─ 包含：线弹性、小变形、静态、各向同性
   └─ 排除：所有次要载荷效应

═══ 输出规范 ═══
格式：\\boxed{{数值}} μm
示例：\\boxed{{1}} μm
""",
f"""
请你扮演一位机械结构分析工程师，帮我分析一个平板法兰的变形问题。

首先说明一下，平板法兰是管道系统中的连接部件，它的密封面是完全平的（既没有突起也没有凹陷）。

我需要你计算这个法兰的最大位移值 |u|_max = √(dx² + dy² + dz²)，结果用微米（μm）表示。

请特别注意：你必须按照最后给出的格式要求输出答案，不然会被判定为无效。

这是分析所需的所有信息：

关于坐标系（采用右手坐标系）：
• 坐标原点在：x=0.0, y=0.0, z=0.0
• X轴指向：x=1.0, y=0.0, z=0.0  
• Y轴指向：x=0.0, y=0.0, z=1.0
• Z轴指向：x=0.0, y=-1.0, z=0.0

关于法兰的几何形状：
1. 先画一个草图（位于原点处，法向量沿+z方向）：
   - 画一个外圆，半径是 {identity["D"]} mm
   - 画一个内圆，半径是 {identity["B1"]} mm
   - 画 {identity["bolt_count_edit"]} 个螺栓孔，每个孔的半径是 {identity["L"]} mm
   - 这些孔的圆心均匀分布在半径为 {identity["BoltCenterRadius"]} mm 的圆周上
2. 然后把草图沿+z方向拉伸 {identity["thickness"]} mm 的厚度
3. 使用的材料是 {identity["Name"]}：
   - 杨氏模量：{identity["YoungsModulus"]} MPa
   - 泊松比：{identity["PoissonRatio"]}
   - 密度：{identity["Density"]} kg/m³

关于载荷和约束：
• 把外圆柱面完全固定住（各个方向的位移都是0）
• 在内圆柱面上施加 {identity["pressure"]} MPa 的均匀内压（使其向外膨胀）

分析时的假设条件：
• 材料是线弹性的、各向同性的
• 只考虑小变形
• 这是静力分析
• 不考虑任何次要因素（比如重力、螺栓预紧力、垫片压缩、接触非线性、温度载荷、热膨胀失配、制造残余应力、外部弯矩/轴向力、扭矩、动载/冲击、地震/风、疲劳循环、腐蚀减薄、浸没/流体浮力、磁力/电力、高压试验、运输/吊装等）

你的答案格式必须是：\\boxed{{数值}} μm
比如：\\boxed{{1}} μm
""",
f"""
【分析任务】平板法兰静力分析

【关键定义】
平板法兰：管道连接件，密封面为纯平面（无突面/凹面）
目标：计算最大位移 |u|_max = √(dx² + dy² + dz²) [μm]

⚠️ 输出必须符合格式要求，否则无效！

【输入数据】
▶ 坐标系（右手）：
  原点(0,0,0)；X轴(1,0,0)；Y轴(0,0,1)；Z轴(0,-1,0)

▶ 几何：
  • 外径 R_out = {identity["D"]} mm
  • 内径 R_in = {identity["B1"]} mm 
  • 厚度 t = {identity["thickness"]} mm（+Z向拉伸）
  • 螺栓孔：r={identity["L"]} mm，n={identity["bolt_count_edit"]}个，分布圆R={identity["BoltCenterRadius"]} mm

▶ 材料（{identity["Name"]}）：
  E = {identity["YoungsModulus"]} MPa
  ν = {identity["PoissonRatio"]}
  ρ = {identity["Density"]} kg/m³

▶ 边界条件：
  • 固定：外圆柱面（u=0）
  • 载荷：内圆柱面内压 P = {identity["pressure"]} MPa

▶ 假设：线弹性/小变形/静态/各向同性
  忽略：重力等所有次要载荷

【必需输出】\\boxed{{数值}} μm
""",
f"""
技术任务：平板法兰线弹性静力分析

背景说明：平板法兰作为工业管道系统的标准连接件，其密封面为纯平面设计（无突面或凹面特征）。

任务要求：请以机械结构分析工程师的身份，根据以下参数计算最大节点位移模 |u|_max = √(dx² + dy² + dz²)，单位：μm。

【注意】必须严格遵循第五部分规定的输出格式，否则结果无效。

第一部分：坐标系定义（右手坐标系）
- 原点位置: {{ "x": 0.0, "y": 0.0, "z": 0.0 }}
- X轴方向: {{ "x": 1.0, "y": 0.0, "z": 0.0 }}
- Y轴方向: {{ "x": 0.0, "y": 0.0, "z": 1.0 }}
- Z轴方向: {{ "x": 0.0, "y": -1.0, "z": 0.0 }}

第二部分：平板法兰几何参数
1. 基础草图参数（草图平面位于原点，法向量沿+z_axis）
   - 外圆半径：{identity["D"]} mm
   - 内圆半径：{identity["B1"]} mm
   - 螺栓孔参数：
     * 单孔半径：{identity["L"]} mm
     * 孔位数量：{identity["bolt_count_edit"]}
     * 分布圆半径：{identity["BoltCenterRadius"]} mm（孔心均匀分布）
2. 三维建模：沿+z_axis方向拉伸，拉伸高度 = {identity["thickness"]} mm
3. 材料属性：{identity["Name"]}
   - 弹性模量 E = {identity["YoungsModulus"]} MPa
   - 泊松比 ν = {identity["PoissonRatio"]}
   - 密度 ρ = {identity["Density"]} kg/m³

第三部分：载荷与约束条件
- 位移约束：外圆柱面完全固定（所有方向位移为零）
- 压力载荷：内圆柱面承受 {identity["pressure"]} MPa 的均匀内压（径向向外）

第四部分：计算假设条件
- 材料行为：线弹性、各向同性
- 变形假设：小变形理论
- 分析类型：静力分析
- 忽略因素：重力、螺栓预紧、垫片效应、接触非线性、温度效应、热膨胀、残余应力、外部力矩、轴向载荷、扭转载荷、动态载荷、冲击载荷、地震载荷、风载荷、疲劳效应、腐蚀影响、流体浮力、电磁力、试验载荷、吊装载荷

第五部分：结果输出要求
输出格式：\\boxed{{数值}} μm
参考示例：\\boxed{{1}} μm
"""
]
        return random.choice(prompts)

    @staticmethod
    def extract_output(output):
        idx = output.rfind("\\boxed{")
        if idx < 0:
            return -1
        idx += 7

        i = idx
        right_brace_idx = None
        while i < len(output):
            if output[i] == "}":
                right_brace_idx = i
                break
            i += 1
        if right_brace_idx is None:
            return -1
        else:
            disp = re.sub(r'[^0-9.]', '', output[idx: right_brace_idx])
            if len(disp):
                return float(disp)
            else:
                return -1

    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return 0.0
        try:
            step_file_path = step_generation(
                                            float(identity["D"]), 
                                            float(identity["B1"]), 
                                            float(identity["L"]), 
                                            float(identity["BoltCenterRadius"]), 
                                            float(identity["thickness"]), 
                                            float(identity["bolt_count_edit"]))
            frd_file_path = cae_analysis(
                                        step_file_path, 
                                        identity["Name"], 
                                        identity["YoungsModulus"], 
                                        identity["PoissonRatio"], 
                                        identity["Density"], 
                                        identity["pressure"])
            result = frd_extract(frd_file_path)
        except Exception as e:
            print(f"[DEBUG ExampleRewardManager] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG ExampleRewardManager] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
        return (solution >= result[1]) * (solution <= result[2])
