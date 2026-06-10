from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from typing import Dict, Any, Optional
import numpy as np
import random
import requests
from internbootcamp.bootcamps.fenics_bootcamp import ips


class ThermalControlInstructionGenerator(BaseInstructionGenerator):
    """
    热控制指令生成器 (配置驱动版)
    用于生成热通量控制任务，支持通过 config 字典动态调整物理参数范围和难度。
    """
    
    def __init__(self, 
                 length_range: list = [1.0, 4.0],
                 width_range: list = [1.0, 4.0],
                 kappa_base_range: list = [20.0, 50.0],
                 alpha_range: list = [0.1, 0.25],
                 source_amp_range: list = [100.0, 300.0],
                 flux_range: list = [50.0, 800.0],
                 tolerance: float = 0.5,
                 max_temp_margin: float = 50.0,
                 max_tool_calls: int = 5,
                 seed: Optional[int] = None,
                 **kwargs):
        """
        初始化生成器
        
        Args:
            length_range: 长度范围 [min, max] (m)
            width_range: 宽度范围 [min, max] (m)
            kappa_base_range: 基础热导率范围 [min, max] (W/(m·K))
            alpha_range: 非线性系数范围 [min, max]
            source_amp_range: 内部热源强度范围 [min, max]
            flux_range: 热通量范围 [min, max] (W/m²)
            tolerance: 温度容差 (K)
            max_temp_margin: 最大温度裕度 (K)
            max_tool_calls: 最大工具调用次数
            **kwargs: 其他参数
        """
        super().__init__()
        
        # 设置参数
        self.length_range = length_range
        self.width_range = width_range
        self.kappa_base_range = kappa_base_range
        self.alpha_range = alpha_range
        self.source_amp_range = source_amp_range
        self.flux_range = flux_range
        self.tolerance = tolerance
        self.max_temp_margin = max_temp_margin
        self.max_tool_calls = max_tool_calls


    
    def case_generator(self) -> Dict[str, Any]:
        """
        生成热控制任务案例 (基于配置文件)
        """
        
        while True:
            try:
                # 1. 使用配置的几何参数范围
                L = round(random.uniform(*self.length_range), 2)
                W = round(random.uniform(*self.width_range), 2)
                
                # 2. 使用配置的材料属性参数
                kappa_base = round(random.uniform(*self.kappa_base_range), 1)
                alpha = round(random.uniform(*self.alpha_range), 3)
                source_amp = round(random.uniform(*self.source_amp_range), 1)
                
                config_dict = {
                    "length": L, 
                    "width": W, 
                    "kappa_base": kappa_base, 
                    "alpha": alpha, 
                    "source_amp": source_amp
                }
                
                # 3. 使用配置的热通量范围生成反向求解的目标温度（Oracle解）
                hidden_flux_left = round(random.uniform(*self.flux_range), 1)
                hidden_flux_bottom = round(random.uniform(*self.flux_range), 1)
                
                # 4. 监测点位置
                m1_x = round(random.uniform(0.3 * L, 0.6 * L), 3)
                m1_y = round(random.uniform(0.5 * W, 0.8 * W), 3)
                m2_x = round(random.uniform(0.5 * L, 0.8 * L), 3)
                m2_y = round(random.uniform(0.2 * W, 0.5 * W), 3)
                
                # 确保两点不重合
                if np.sqrt((m1_x - m2_x)**2 + (m1_y - m2_y)**2) < 0.5:
                    continue

                # 5. 使用 API 执行 Oracle 仿真
                try:
                    payload = {
                        "length": config_dict["length"],
                        "width": config_dict["width"],
                        "kappa_base": config_dict["kappa_base"],
                        "alpha": config_dict["alpha"],
                        "source_amp": config_dict["source_amp"],
                        "flux_left": hidden_flux_left,
                        "flux_bottom": hidden_flux_bottom,
                        "monitor1_x": m1_x,
                        "monitor1_y": m1_y,
                        "monitor2_x": m2_x,
                        "monitor2_y": m2_y
                    }
                    
                    response = requests.post(
                        f"{random.choice(ips)}/run_thermal_simulation",
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=200
                    )
                    
                    if not response.ok or not response.json().get("success"):
                        print("Oracle 仿真失败，重新生成案例...")
                        continue
                    
                    result = response.json()
                    oracle_res = {
                        "status": "success",
                        "temp_monitor1": result["temp_monitor1"],
                        "temp_monitor2": result["temp_monitor2"],
                        "max_temp": result["max_temp"]
                    }
                    
                except Exception as e:
                    print(f"Oracle 仿真失败 ({str(e)})，重新生成案例...")
                    continue

                if oracle_res["status"] != "success":
                    print("Oracle 仿真失败，重新生成案例...")
                    continue
                
                t1 = oracle_res["temp_monitor1"]
                t2 = oracle_res["temp_monitor2"]
                max_t = oracle_res["max_temp"]
                
                # 虽然数学上可解，但对LLM来说太反直觉，重置
                if max_t > 1500:
                    continue
                
                # 6. 构建返回的任务身份信息（使用配置参数）
                return {
                    "length": L, 
                    "width": W,
                    "kappa_base": kappa_base, 
                    "alpha": alpha, 
                    "source_amp": source_amp,
                    "monitor1_x": m1_x, 
                    "monitor1_y": m1_y, 
                    "target_temp1": round(t1, 2),
                    "monitor2_x": m2_x, 
                    "monitor2_y": m2_y, 
                    "target_temp2": round(t2, 2),
                    "max_temp_limit": round(max_t + self.max_temp_margin, 1),
                    "tolerance": self.tolerance,
                    "max_tool_calls": self.max_tool_calls,
                    "_hidden_solution": (hidden_flux_left, hidden_flux_bottom)
                }
                
            except Exception as e:
                print(f"Case生成异常: {e}")
                continue

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        # 提取参数以简化模板中的引用
        L = identity['length']
        W = identity['width']
        k_base = identity['kappa_base']
        alpha = identity['alpha']
        src_amp = identity['source_amp']
        m1_x, m1_y = identity['monitor1_x'], identity['monitor1_y']
        t1 = identity['target_temp1']
        m2_x, m2_y = identity['monitor2_x'], identity['monitor2_y']
        t2 = identity['target_temp2']
        tol = identity['tolerance']
        
        prompts = [
            # 1. 【国防军事风】强调任务的紧迫性和原型机的昂贵成本
        f"""
**绝密任务指令：代号“赤炎”**
指挥官，你负责的下一代高超音速飞行器热盾部件正处于关键设计阶段。这是一次不可失败的任务。

**物理实体参数**：
该部件尺寸为 {L}m (长) x {W}m (宽)。
材料热导率具有极度危险的非线性特征：$k(T) = \\frac{{{k_base}}}{{1 + {alpha}(T - 293)}}$。注意：{alpha} 的负温度系数意味着**高温下导热能力急剧下降**，极易诱发热斑。
内部存在强度系数为 {src_amp} 的正弦体积热源。

**边界控制任务**：
除了左边界(flux_left)和下边界(flux_bottom)可控外，其余边界被锁定在 293K。
你需要精确调整这两个热通量，使侦察传感器读数达标：
1. 传感器A ({m1_x}, {m1_y}) 需稳定在 {t1} K (±{tol})。
2. 传感器B ({m2_x}, {m2_y}) 需稳定在 {t2} K (±{tol})。

**输出指令**：
解出 flux_left 和 flux_bottom，并以严格格式输出：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{1250.5, 800.2}}
""",

        # 2. 【学术科研风】强调非线性偏微分方程的反问题求解
        f"""
**实验报告：非线性热传导反问题研究**
首席研究员，我们需要针对一种新型复合材料求解特定的边界条件。

**问题定义**：
在一个 ${L} \\times {W}$ 的矩形域内，控制方程涉及非线性热传导系数 $k(T) = \\frac{{{k_base}}}{{1 + {alpha}(T - 293)}}$。
域内存在非均匀热源项，幅度参数 $S = {src_amp}$。
边界条件：$x=0$ 处热流为 $q_L$，$y=0$ 处热流为 $q_B$，其余边界恒温 293K。

**优化目标**：
确定 $q_L$ (flux_left) 和 $q_B$ (flux_bottom) 的值，使得：
- 点 $P_1({m1_x}, {m1_y})$ 温度 $T_1 \\approx {t1}$ K
- 点 $P_2({m2_x}, {m2_y})$ 温度 $T_2 \\approx {t2}$ K
- 容差范围：$\\pm {tol}$ K

**结果提交格式**：
请输出最终确定的通量值：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{500.0, 1000.0}}
""",

        # 3. 【工业制造风】强调工艺参数控制与良品率
        f"""
**工艺参数调整单**
工段长：我们需要为这块特殊晶圆设定退火炉的加热参数。这是一块昂贵的非线性材料。

**规格书**：
- 尺寸：{L}m x {W}m
- 材料特性：导热率随温度升高而降低，公式为 k(T) = {k_base} / (1 + {alpha} * (T - 293))。这增加了温控难度。
- 内部自热干扰：强度 {src_amp}。

**设定目标**：
调节左侧加热器功率密度 (flux_left) 和底部加热器功率密度 (flux_bottom)，确保关键质检点温度达标：
1. 质检点1 ({m1_x}, {m1_y})：目标 {t1} K
2. 质检点2 ({m2_x}, {m2_y})：目标 {t2} K
允许偏差：±{tol} K。


**输出要求**：
填写最终设定的工艺参数：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{1100.5, 950.0}}
""",

        # 4. 【AI系统风】强调算法逻辑与系统约束
        f"""
>>> SYSTEM_BOOT...
>>> ROLE: Thermal_Optimization_AI
>>> INPUT_DATA_STREAM:

**物理环境建模**：
- 几何：Rectangle({L}, {W})
- 介质方程：Heat_Eq with k(T) = {k_base}/(1+{alpha}*(T-293))
- 源项：Sinusoidal_Source(amp={src_amp})

**目标函数 (Objective)**：
Find (flux_left, flux_bottom) such that:
   |Temp({m1_x}, {m1_y}) - {t1}| <= {tol}
   AND
   |Temp({m2_x}, {m2_y}) - {t2}| <= {tol}


**输出协议**：
返回标准化的浮点数列表：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{888.88, 666.66}}
""",

        # 5. 【危机应对风】强调时间紧迫与防止过热
        f"""
**紧急警报：反应堆冷却壁温控异常**
工程师，反应堆外壁（{L}m x {W}m）正在积热！这种特殊合金的热导率 $k(T) = {k_base} / (1 + {alpha}(T - 293))$ 会随着温度升高而恶化，极易发生热失控熔穿！

**现状数据**：
- 内部已检测到正弦波动的热源，强度 {src_amp}。
- 外部环境强制冷却至 293K（除左侧和底部）。

**抢修目标**：
必须立即调整左侧(flux_left)和底部(flux_bottom)的补偿热流，死死稳住以下两个监测点的温度，防止连锁反应：
1. 关键点A ({m1_x}, {m1_y}) 必须维持在 {t1} ± {tol} K。
2. 关键点B ({m2_x}, {m2_y}) 必须维持在 {t2} ± {tol} K。


**指令输入**：
立即给出修正后的热通量值：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{1500.0, 750.0}}
""",

        # 6. 【数学建模竞赛风】纯粹的数学物理问题描述
        f"""
**题目 B：非均匀介质中的稳态热传导控制**

**已知条件**：
1. 求解域：$\Omega = [0, {L}] \\times [0, {W}]$。
2. 控制方程：$-\\nabla \\cdot (k(T)\\nabla T) = Q(x,y)$。
   其中 $k(T) = \\frac{{{k_base}}}{{1 + {alpha}(T - 293)}}$，体积热源 $Q$ 的振幅为 {src_amp}。
3. 边界条件：
   - $\Gamma_{{left}}$: $-k \\frac{{\\partial T}}{{\\partial n}} = \\text{{flux\_left}}$
   - $\Gamma_{{bottom}}$: $-k \\frac{{\\partial T}}{{\\partial n}} = \\text{{flux\_bottom}}$
   - 其他边界 $T = 293$。

**求解任务**：
确定 flux_left 和 flux_bottom，使得：
- $T({m1_x}, {m1_y}) = {t1} \\pm {tol}$
- $T({m2_x}, {m2_y}) = {t2} \\pm {tol}$


**答案格式**：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{300.2, 400.5}}
""",

        # 7. 【科幻星际风】飞船护盾发生器背景
        f"""
**星舰工程日志 - 2242年**
我是轮机长。我们的“虚空行者”级护盾发生器（尺寸 {L}x{W} 米）需要校准。该装置使用不稳定的晶体核心，其热导率遵循 $k = {k_base}/(1+{alpha}(T-293))$，温度越高传导越慢，这很棘手。

**校准参数**：
核心内部有强度为 {src_amp} 的波动能量源。
我们需要调整左舷(flux_left)和底座(flux_bottom)的能量注入流，以稳定核心节点：
- 节点 Alpha ({m1_x}, {m1_y}): 锁定温度 {t1} K (误差 {tol} K)
- 节点 Beta ({m2_x}, {m2_y}): 锁定温度 {t2} K (误差 {tol} K)


**设置输出**：
输入能量流参数：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{2000.0, 1500.0}}
""",

        # 8. 【极简硬核风】无废话，直接列出参数和约束
        f"""
**任务**：求解二维非线性热传导反问题。
**几何**：L={L}m, W={W}m。
**材料**：$k_{{base}}={k_base}$, $\\alpha={alpha}$ (公式：$k=k_{{base}}/(1+\\alpha(T-293))$)。
**热源**：$S_{{amp}}={src_amp}$ (正弦分布)。
**边界**：除了左侧(flux_left)和下侧(flux_bottom)为纽曼边界外，其余为狄利克雷边界(293K)。

**目标点**：
1. ({m1_x}, {m1_y}) -> {t1}K
2. ({m2_x}, {m2_y}) -> {t2}K
**容差**：±{tol}K。


**输出**：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{1234.5, 678.9}}
""",

        # 9. 【财务审计风】强调计算成本
        f"""
**项目预算审批单**
作为技术总监，你需要审批本次热控系统的设计参数。这块 {L}x{W} 的非线性材料（$k(T)={k_base}/(1+{alpha}\\Delta T)$）极其难搞，且内部热源强度高达 {src_amp}。

**审计要求**：
我们必须以最小的计算成本找到满足以下温控指标的输入通量（flux_left 和 flux_bottom）：
- 监测点A ({m1_x}, {m1_y}) 温度控制在 {t1} K
- 监测点B ({m2_x}, {m2_y}) 温度控制在 {t2} K
- 允许误差范围 {tol} K

**最终决策**：
请填写批准的通量设置：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{900.0, 1200.0}}
""",

        # 10. 【黑客松挑战风】编程与算法挑战语境
        f"""
**Challenger: Thermal_Control_v2**
欢迎来到高保真物理模拟挑战赛。你的目标是“驯服”一块具有负温度系数特性的材料。

**环境配置**：
- Map Size: {L} x {W}
- Nonlinearity: $k(T) = \\frac{{{k_base}}}{{1 + {alpha} \\times (T - 293)}}$ (Difficulty: HARD)
- Internal Heat: Sinusoidal wave, amp={src_amp}

**Level Goals**:
调整 inputs `flux_left` 和 `flux_bottom`，击中以下 Target：
1. Hit Point 1: ({m1_x}, {m1_y}) @ {t1}K ±{tol}
2. Hit Point 2: ({m2_x}, {m2_y}) @ {t2}K ±{tol}


**Submit Flag**:
提交你的最终解：
\\boxed{{flux_left, flux_bottom}}
例如：
\\boxed{{1000.0, 500.0}}
"""
    ]
    
        return random.choice(prompts)