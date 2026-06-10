from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.battery_bootcamp.battery_utils import execute_pybamm_logic
from typing import Dict, Any, Optional
import numpy as np
import random
import time

class BatteryDesignInstructionGenerator(BaseInstructionGenerator):
    """
    电池设计指令生成器 (配置驱动版)
    用于生成电池参数优化任务，支持通过 config 字典动态调整物理参数范围和难度。
    """
    
    def __init__(self, 
                 chemistry: str = "Chen2020",
                 c_rate_options: list = ["2C", "3C", "4C"],
                 ambient_temp_range: list = [298.0, 310.0],
                 heat_transfer_coeff_range: list = [5.0, 15.0],
                 thickness_range: list = [60.0e-6, 140.0e-6],
                 porosity_range: list = [0.25, 0.45],
                 target_energy_ratio: float = 0.99,
                 target_temp_tolerance: float = 1.0,
                 max_tool_calls: int = 5,
                 **kwargs):
        """
        初始化生成器
        
        Args:
            chemistry: 化学体系，默认 "Chen2020"
            c_rate_options: C-rate选项列表
            ambient_temp_range: 环境温度范围 [min, max] (K)
            heat_transfer_coeff_range: 散热系数范围 [min, max] (W/(m²·K))
            thickness_range: 正极厚度范围 [min, max] (m)
            porosity_range: 正极孔隙率范围 [min, max]
            target_energy_ratio: 目标能量比例
            target_temp_tolerance: 目标温度容差 (K)
            max_tool_calls: 最大工具调用次数
            **kwargs: 其他参数
        """
        super().__init__()
        
        # 设置参数
        self.chemistry = chemistry
        self.c_rate_options = c_rate_options
        self.ambient_temp_range = ambient_temp_range
        self.heat_transfer_coeff_range = heat_transfer_coeff_range
        self.thickness_range = thickness_range
        self.porosity_range = porosity_range
        self.target_energy_ratio = target_energy_ratio
        self.target_temp_tolerance = target_temp_tolerance
        self.max_tool_calls = max_tool_calls
        
        # 预定义物理常数块（供 Prompt 使用）
        self.PHYSICS_CONSTANTS_BLOCK = """
1. **几何尺寸**
   - 负极厚度: **100 µm**
   - 隔膜厚度: **25 µm**
   - 负极集流体(铜)厚度: 12 µm
   - 正极集流体(铝)厚度: 16 µm
   - 电极面积: 0.1027 m²
2. **材料属性**
   - 密度:
     - 正极(固体): 3262 kg/m³
     - 负极(固体): 1657 kg/m³
     - 隔膜(固体): 397 kg/m³
     - 铜箔: 8960 kg/m³ | 铝箔: 2700 kg/m³
     - 电解液: 1200 kg/m³ (填充在正极、负极、隔膜的所有孔隙中)
   - 固定孔隙率:
     - 负极: 0.25
     - 隔膜: 0.47
3. **容量缩放逻辑**
   仿真器会自动根据你的设计调整电池标称容量。基准参考值如下：
   - 基准容量: 5.0 Ah
   - 基准正极厚度: 75.6 µm
   - 基准正极孔隙率: 0.335
"""
    
    def case_generator(self) -> Dict[str, Any]:
        """
        生成电池设计任务案例 (基于配置文件)
        """
        
        while True:
            try:
                # 1. 随机环境 (使用配置参数)
                chemistry = self.chemistry
                c_rate = np.random.choice(self.c_rate_options) 
                ambient_temp = np.random.uniform(*self.ambient_temp_range)
                h_coeff = np.random.uniform(*self.heat_transfer_coeff_range)
                
                context = {
                    "chemistry": chemistry,
                    "c_rate": c_rate,
                    "ambient_temp": ambient_temp,
                    "initial_temp": ambient_temp,
                    "heat_transfer_coeff": h_coeff
                }

                # 2. 生成参考解 (Oracle，使用配置参数)
                ref_thickness = np.random.uniform(*self.thickness_range) 
                ref_porosity = np.random.uniform(*self.porosity_range)

                oracle_res = execute_pybamm_logic(ref_thickness, ref_porosity, context)
                if oracle_res["status"] != "success": 
                    print(oracle_res["message"])
                    continue

                # 3. 设定目标 (使用配置参数)
                ref_wh_kg = oracle_res["specific_energy"]  # 增加厚度可以增加总能量(Wh)，但也增加了质量(kg)。只有在孔隙率和厚度达到最佳匹配时，Wh/kg 才会高。盲目增加厚度会导致电压极化严重，容量放不出来，反而降低 Wh/kg。
                ref_temp = oracle_res["max_temp"]

                target_wh_kg = int(ref_wh_kg * self.target_energy_ratio)  # 使用配置的能量比例
                target_max_temp = int(ref_temp + self.target_temp_tolerance)  # 使用配置的温度容差

                context["target_specific_energy"] = target_wh_kg
                context["target_max_temp"] = target_max_temp

                
                # 将最大调用次数也放入 context，以便 Prompt 使用
                context["max_tool_calls"] = self.max_tool_calls
                
                return context
                
            except Exception as e:
                print(f"Case生成异常: {e}")
                continue

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        """
        根据任务信息生成提示语 (从10个模板中随机选择一个)
        """
        # 别名简写
        I = identity
        phys_block = self.PHYSICS_CONSTANTS_BLOCK
        
        # 定义10个不同的 Prompt 模板
        templates = [
            # ---------------------------------------------------------
            # 模板 1: 原始专家模式
            # ---------------------------------------------------------
            f"""你是一位资深的电池系统设计专家。我们需要为特定工况设计一款锂离子电池的 **正极参数**。

【任务目标】
调整 **正极厚度** 和 **正极孔隙率**，使得电池满足：
1. **电池比能量 >= {I['target_specific_energy']} Wh/kg**
2. **最高电池温度 <= {I['target_max_temp']} K**

【仿真环境与工况】
- 化学体系: {I['chemistry']}
- 放电倍率: {I['c_rate']} (恒流放电至 2.5V)
- 环境与初始温度: {I['ambient_temp']:.1f} K
- 散热系数 (h): {I['heat_transfer_coeff']:.1f} W/(m²·K)

【系统物理约束与计算参数】
为了进行理论预估，请使用以下参数：
{phys_block}

【可用工具】
使用 `run_battery_simulation` 进行虚拟试错。


【输出要求】
找到满足条件的参数后，请严格按此格式输出最终答案（仅包含两个数字）：
\\boxed{{Positive electrode thickness [m], Positive electrode porosity}}
例如: \\boxed{{0.00012, 0.35}}
""",

            # ---------------------------------------------------------
            # 模板 2: 工业规格书
            # ---------------------------------------------------------
            f"""# 锂离子电池正极设计任务书 (编号: BAT-OPT-2024)

## 1. 项目背景
本项目旨在针对特定化学体系开发高比能电芯。需通过仿真确定最佳的**正极微观结构参数**。

## 2. 目标规格 (KPIs)
* **最小比能量 (Wh/kg)**: {I['target_specific_energy']}
* **最大允许温度 (K)**: {I['target_max_temp']}

## 3. 工况定义
* 体系: {I['chemistry']}
* 倍率: {I['c_rate']}
* 环境: {I['ambient_temp']:.1f} K | 散热系数 h={I['heat_transfer_coeff']:.1f}

## 4. 设计约束与参数表
{phys_block}

## 5. 执行要求
利用 `run_battery_simulation` 工具进行验证。
最终输出格式（必须严格遵守）:
\\boxed{{thickness, porosity}}
""",

            # ---------------------------------------------------------
            # 模板 3: 紧急排障风
            # ---------------------------------------------------------
            f"""【紧急求助】生产线警报！
现在的电池设计方案无法满足客户的新要求，我们需要你立即介入修正设计！

当前短板：我们需要在该工况下将比能量提升至 **{I['target_specific_energy']} Wh/kg** 以上，同时必须死守 **{I['target_max_temp']} K** 的热安全红线。

现有环境条件：
- {I['chemistry']} 体系在 {I['c_rate']} 高倍率下运行。
- 环境温度已达 {I['ambient_temp']:.1f} K，散热条件有限 (h={I['heat_transfer_coeff']:.1f})。

请参考下方的物理参数底表，立即计算并仿真出合适的**正极厚度**和**孔隙率**:
{phys_block}

最终方案请直接给出: \\boxed{{thickness, porosity}}
""",

            # ---------------------------------------------------------
            # 模板 4: 第一性原理思维
            # ---------------------------------------------------------
            f"""你是一名物理学家。请从第一性原理出发，推导最佳电池设计。

任务：寻找正极厚度 ($L_{{pos}}$) 和 孔隙率 ($\epsilon_{{pos}}$) 的最优解。
目标函数：$E_{{spec}} \ge {I['target_specific_energy']}$ 且 $T_{{max}} \le {I['target_max_temp']}$。

已知边界条件：
- 化学性质: {I['chemistry']}
- 动力学条件: {I['c_rate']} 放电, $T_{{amb}}={I['ambient_temp']:.1f}K$, $h={I['heat_transfer_coeff']:.1f}$

物理常数参考：
{phys_block}

建议步骤：
1. 先根据目标能量密度和材料密度，估算所需的活性物质载量。
2. 结合散热系数估算热积累风险。
3. 调用 `run_battery_simulation` 验证你的估算。

请输出最终优化的参数: \\boxed{{thickness, porosity}}
""",

            # ---------------------------------------------------------
            # 模板 5: 极简算法风
            # ---------------------------------------------------------
            f"""任务：Optimize_Cathode_Parameters
输入向量：
  - Target_Energy: {I['target_specific_energy']} Wh/kg
  - Target_Temp_Max: {I['target_max_temp']} K
  - Chemistry: {I['chemistry']}
  - C_Rate: {I['c_rate']}
  - Env_Temp: {I['ambient_temp']:.1f}
  - Heat_Transfer_h: {I['heat_transfer_coeff']:.1f}

常量定义：
{phys_block}

操作：
1. 思考最优厚度与孔隙率组合。
2. 使用 `run_battery_simulation` 验证 。
3. 如果不满足约束，根据误差梯度调整。

返回结果：
\\boxed{{thickness, porosity}}
""",

            # ---------------------------------------------------------
            # 模板 6: 教学向导
            # ---------------------------------------------------------
            f"""让我们一起来设计一款高性能锂电池。
首先，我们的目标很明确：化学体系: {I['chemistry']}，要在 {I['c_rate']} 的放电速率下，实现 {I['target_specific_energy']} Wh/kg 的比能量，且温度不超过 {I['target_max_temp']} K。

环境条件是 {I['ambient_temp']:.1f} K 和 h={I['heat_transfer_coeff']:.1f}。

你需要思考两个权衡：
1. 增加厚度会增加活性物质（提升能量），但也增加了离子传输距离（增加内阻产热）。
2. 降低孔隙率能提高能量密度，但可能导致电解液枯竭和高倍率性能下降。

请使用以下参数作为计算基础：
{phys_block}

你可以调用 `run_battery_simulation` 来测试你的假设,。请告诉我你最终选择的参数：
\\boxed{{thickness, porosity}}
""",

            # ---------------------------------------------------------
            # 模板 7: 热管理专家
            # ---------------------------------------------------------
            f"""你好，我是热管理团队的负责人。我们发现当前的电芯在大倍率放电下发热严重，需要你配合调整电极结构。

我们需要将化学体系: {I['chemistry']}，在放电速率 **{I['c_rate']}** 放电过程中的最高温度控制在 **{I['target_max_temp']} K** 以内，同时不能牺牲太多的能量密度（至少保持 **{I['target_specific_energy']} Wh/kg**）。
环境温度固定为 {I['ambient_temp']:.1f} K，外部散热系数仅为 {I['heat_transfer_coeff']:.1f}。

请通过调整正极厚度和孔隙率来平衡内阻产热和能量容量。
太厚会导致极化发热，太薄则能量不足。太密（低孔隙率）会导致离子传输受阻从而过热。

参考数据：
{phys_block}

使用仿真工具验证你的设计。结果形式: \\boxed{{thickness, porosity}}
""",

            # ---------------------------------------------------------
            # 模板 8: 成本效率导向
            # ---------------------------------------------------------
            f"""作为首席算法工程师，你的目标是以**最小的计算成本**找到满足要求的电池参数。
仿真资源极其昂贵，每一次 `run_battery_simulation` 调用都意味着巨大的算力消耗。

**目标状态**:
- Specific Energy >= {I['target_specific_energy']}
- Max Temp <= {I['target_max_temp']}

**环境参数**:
{I['chemistry']}, {I['c_rate']}, {I['ambient_temp']:.1f}K, h={I['heat_transfer_coeff']:.1f}

**物理参数**:
{phys_block}

**策略建议**:
请不要盲目猜测。建议先设定一个合理的初始值（基于基准参数），然后根据仿真结果的偏差方向（偏大或偏小）动态调整步长。
找到可行解后立即停止并在最后一行输出: \\boxed{{thickness, porosity}}
""",

            # ---------------------------------------------------------
            # 模板 9: JSON 数据解析
            # ---------------------------------------------------------
            f"""解析以下 JSON 配置对象，并输出对应的最佳正极设计参数。

```json
{{
  "task": "optimize_cathode",
  "constraints": {{
    "min_energy_density_wh_kg": {I['target_specific_energy']},
    "max_temperature_k": {I['target_max_temp']}
  }},
  "environment": {{
    "chemistry": "{I['chemistry']}",
    "c_rate": "{I['c_rate']}",
    "ambient_temp": {I['ambient_temp']:.1f},
    "h_coeff": {I['heat_transfer_coeff']:.1f}
  }}
}}
参考物理常数数据库： {phys_block}

利用工具进行验证,成功后，仅返回特定格式结果： Output: \boxed{{thickness, porosity}} """,

        # ---------------------------------------------------------
        # 模板 10: 逆向工程
        # ---------------------------------------------------------
        f"""你需要逆向推导一款能够达到以下性能指标的电池设计参数：

    1.能量密度: {I['target_specific_energy']} Wh/kg
    2.热安全界限: {I['target_max_temp']} K

工况环境如下：

    {I['chemistry']} @ {I['c_rate']}

    T_amb: {I['ambient_temp']:.1f} K, h: {I['heat_transfer_coeff']:.1f}

为了达到这个性能，正极的物理形态（厚度和孔隙率）应该是多少？

请利用以下物理参数进行推算，并使用仿真器确认你的推断： {phys_block}

最终答案需封装在: \boxed{{thickness, porosity}}""" ]

        return random.choice(templates)