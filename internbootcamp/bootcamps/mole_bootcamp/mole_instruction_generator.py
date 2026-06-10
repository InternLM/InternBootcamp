from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from typing import Dict, Any, Optional
import numpy as np
import random
import uuid
import os
import json
from scipy.optimize import differential_evolution
import openmm.openmm as mm
import openmm.unit as unit

class MoleInstructionGenerator(BaseInstructionGenerator):
    """
    分子景观优化指令生成器 (配置驱动版)
    """
    
    def __init__(self, 
                 n_gaussians_range: list = [12, 20],
                 global_min_depth_range: list = [-90.0, -70.0],
                 sigma_narrow_range: list = [0.15, 0.3],
                 n_decoys: int = 3,
                 decoy_depth_range: list = [-50.0, -40.0],
                 sigma_wide_range: list = [1.5, 3.0],
                 noise_depth_range: list = [-30, -10],
                 sigma_mid_range: list = [0.5, 1.5],
                 noise_amp_range: list = [3.0, 6.0],
                 noise_freq_range: list = [8.0, 12.0],
                 de_maxiter: int = 50,
                 de_popsize: int = 15,
                 de_tol: float = 0.01,
                 tolerance: float = 1.5,
                 plot_dir: Optional[str] = None,
                 **kwargs):
        """
        初始化生成器
        
        Args:
            n_gaussians_range: 高斯数量范围 [min, max]
            global_min_depth_range: 全局最优深度范围 [min, max] (kJ/mol)
            sigma_narrow_range: 窄势阱宽度范围 [min, max] (nm)
            n_decoys: 诱饵数量
            decoy_depth_range: 诱饵深度范围 [min, max] (kJ/mol)
            sigma_wide_range: 宽势阱宽度范围 [min, max] (nm)
            noise_depth_range: 背景噪声深度范围 [min, max] (kJ/mol)
            sigma_mid_range: 中等势阱宽度范围 [min, max] (nm)
            noise_amp_range: 正弦噪声幅度范围 [min, max] (kJ/mol)
            noise_freq_range: 正弦噪声频率范围 [min, max]
            de_maxiter: 差分进化最大迭代次数
            de_popsize: 差分进化种群大小
            de_tol: 差分进化容差
            tolerance: 能量容差 (kJ/mol)
            plot_dir: 可视化输出目录
            **kwargs: 其他参数
        """
        super().__init__()
        
        # 设置参数
        self.n_gaussians_range = n_gaussians_range
        self.global_min_depth_range = global_min_depth_range
        self.sigma_narrow_range = sigma_narrow_range
        self.n_decoys = n_decoys
        self.decoy_depth_range = decoy_depth_range
        self.sigma_wide_range = sigma_wide_range
        self.noise_depth_range = noise_depth_range
        self.sigma_mid_range = sigma_mid_range
        self.noise_amp_range = noise_amp_range
        self.noise_freq_range = noise_freq_range
        self.de_maxiter = de_maxiter
        self.de_popsize = de_popsize
        self.de_tol = de_tol
        self.tolerance = tolerance
        self.plot_dir = plot_dir

    def case_generator(self) -> Dict[str, Any]:
        """
        生成 2D 势能面参数，并通过差分进化算法寻找全局最优解（Ground Truth）
        生成的数据会保存到 libraries 目录供服务器加载
        """
        # --- 使用配置参数生成案例 ---
        n_gaussians = random.randint(*self.n_gaussians_range)
        gaussians = []
        
        # 1. 埋藏"宝藏"（全局最优）：深，但是极窄
        global_min_depth = random.uniform(*self.global_min_depth_range)

        gaussians.append({
            "A": global_min_depth, 
            "mu_x": random.uniform(1.0, 9.0),
            "mu_y": random.uniform(1.0, 9.0),
            "sigma_x": random.uniform(*self.sigma_narrow_range),
            "sigma_y": random.uniform(*self.sigma_narrow_range),
            "theta": random.uniform(0, np.pi)
        })

        # 2. 设置"诱饵"（局部最优）：宽，容易发现，但不是最深的
        for _ in range(self.n_decoys):
            gaussians.append({
                "A": random.uniform(*self.decoy_depth_range),
                "mu_x": random.uniform(1.0, 9.0),
                "mu_y": random.uniform(1.0, 9.0),
                "sigma_x": random.uniform(*self.sigma_wide_range),
                "sigma_y": random.uniform(*self.sigma_wide_range),
                "theta": random.uniform(0, np.pi)
            })

        # 3. 填充背景干扰
        for i in range(n_gaussians - self.n_decoys - 1):
            gaussians.append({
                "A": random.uniform(*self.noise_depth_range),
                "mu_x": random.uniform(0.0, 10.0),
                "mu_y": random.uniform(0.0, 10.0),
                "sigma_x": random.uniform(*self.sigma_mid_range),
                "sigma_y": random.uniform(*self.sigma_mid_range),
                "theta": random.uniform(0, np.pi)
            })

        # 4. 增加地形粗糙度（Ruggedness）
        params = {
            "n_gaussians": n_gaussians,
            "gaussians": gaussians,
            "noise_amp": random.uniform(*self.noise_amp_range),
            "noise_freq": random.uniform(*self.noise_freq_range)
        }

        # 生成唯一的环境 ID
        env_id = str(uuid.uuid4())
        
        # 创建临时环境用于计算 Ground Truth
        system = mm.System()
        system.addParticle(1.0)
        
        expression = "1000 * (max(0, -x)^2 + max(0, x-10)^2 + max(0, -y)^2 + max(0, y-10)^2)"
        expression += " + B * sin(k * x) * cos(k * y)"
        
        for i in range(params['n_gaussians']):
            expression += f" + A{i} * exp( -a{i}*(x-mu_x{i})^2 - 2*b{i}*(x-mu_x{i})*(y-mu_y{i}) - c{i}*(y-mu_y{i})^2 )"
        
        force = mm.CustomExternalForce(expression)
        force.addGlobalParameter("B", params['noise_amp'])
        force.addGlobalParameter("k", params['noise_freq'])
        
        for i, g in enumerate(params['gaussians']):
            sin_t = np.sin(g['theta'])
            cos_t = np.cos(g['theta'])
            sig_x2 = g['sigma_x'] ** 2
            sig_y2 = g['sigma_y'] ** 2
            
            a = (cos_t**2 / (2*sig_x2)) + (sin_t**2 / (2*sig_y2))
            b = -(sin_t * cos_t) / (2*sig_x2) + (sin_t * cos_t) / (2*sig_y2)
            c = (sin_t**2 / (2*sig_x2)) + (cos_t**2 / (2*sig_y2))
            
            force.addGlobalParameter(f"A{i}", g['A'])
            force.addGlobalParameter(f"mu_x{i}", g['mu_x'])
            force.addGlobalParameter(f"mu_y{i}", g['mu_y'])
            force.addGlobalParameter(f"a{i}", a)
            force.addGlobalParameter(f"b{i}", b)
            force.addGlobalParameter(f"c{i}", c)
        
        force.addParticle(0, [])
        system.addForce(force)
        
        integrator = mm.VerletIntegrator(0.001)
        context = mm.Context(system, integrator)

        # 3. 计算 Ground Truth
        def objective_func(coords):
            context.setPositions([[coords[0], coords[1], 0]])
            return context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)

        bounds = [(0, 10), (0, 10)]
        
        # 使用配置的差分进化参数
        result = differential_evolution(
            objective_func, bounds, 
            strategy='best1bin', 
            maxiter=self.de_maxiter, 
            popsize=self.de_popsize, 
            tol=self.de_tol
        )

        ground_truth = {
            "global_min_energy": float(result.fun),
            "global_min_coords": list(result.x),
            "params": params,
            "env_id": env_id,
            "tolerance": self.tolerance
        }

        # 保存到 libraries 目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        libraries_dir = os.path.join(current_dir, "libraries")
        os.makedirs(libraries_dir, exist_ok=True)
        
        filepath = os.path.join(libraries_dir, f"{env_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(ground_truth, f, ensure_ascii=False, indent=2)

        return ground_truth

#     def prompt_func(self, identity: Dict[str, Any]) -> str:
#         """
#         根据任务信息生成提示语
#         """
#         I = identity
        
#         return f"""
# 任务目标：
# 你是一个被投放到二维未知势能面上的探测器。你的活动区域是 [0, 10] nm x [0, 10] nm 的正方形区域。
# 该区域地形极度崎岖，包含大量极窄的深井和高频能量势垒，你需要找到**能量最低**的那个点（全局极小值）。

# **关键信息：**
# **当前环境 ID (env_id): {I['env_id']}**
# **在调用任何工具时，你必须将此 ID 填入 `env_id` 参数中，否则工具无法执行。**

# 挑战说明：
# 1. 这个问题可能有多个坐标点的能量都非常接近最低值（解不唯一），你只要找到其中任意一个即可。
# 2. 地形不仅有高斯势阱，还叠加了正弦波动的噪声，不要被浅坑迷惑。

# 可用工具：
# - measure_point(env_id, x, y): 测量坐标 (x, y) 处的能量和受力向量。
# - run_local_minimization(env_id, start_x, start_y): 从指定点释放，让粒子顺坡滑落到底部。

# 要求：
# 1. 你有 {I.get('max_operations', 20)} 次操作机会。
# 2. 建议策略：先通过测量粗略扫描，发现低能量区域后，再用局部优化工具精确定位。
# 3. 最终答案请严格使用 \\boxed{{[x, y]}} 格式输出坐标列表，保留两位小数，例如 \\boxed{{[3.52, 8.19]}}。
# """
    def prompt_func(self, identity: Dict[str, Any]) -> str:
        """
        根据任务信息生成随机风格的中文提示语。
        所有 Prompt 均强制强调 env_id、pin 码和输出格式示例。
        """
        env_id = identity['env_id']
        
        prompts = [
            # ----------------------------------------------------------------
            # 1. 标准说明书风格 (严谨、清晰)
            # ----------------------------------------------------------------
            f"""
任务指令：
你处于一个 10x10 nm 的二维区域中，目标是寻找**全局能量最低点**。地形包含大量深井和高频噪声，请务必小心。

**关键参数：**
- 任务 ID (env_id): {env_id}

**可用工具：**
1. **初始化**：首先必须调用 `create_session(env_id='{env_id}')` 构造场景并获取关键的 `pin` 码。
2. **测量**：用 `measure_point(env_id, pin, x, y)` 测量该点的能量和受力。
3. **优化**：用 `run_local_minimization(env_id, pin, start_x, start_y)` 从该点滑落至局部最低点。

**要求：**
1. 策略：先粗略扫描，后精确定位。
2. 输出：严格使用以下格式输出最终答案（保留两位小数）：
```json{{"pin": "你的pin码", "coords": [x, y]}}```

**输出示例：**
```json{{"pin": "123456", "coords": [3.52, 8.19]}}```
""",

            # ----------------------------------------------------------------
            # 2. 算法工程师风格 (强调非凸优化逻辑)
            # ----------------------------------------------------------------
            f"""
角色：优化算法智能体
场景：你面对的是一个定义在 [0, 10] x [0, 10] 域上的非凸目标函数。函数存在多个局部极小值且带有噪声。
目标：在有限步数内找到全局最小能量点 (Global Minimum)。

**接口调用规范 (EnvID: {env_id})：**
1. Session初始化: `create_session(env_id='{env_id}')` -> 获取 pin 码
2. 梯度查询: `measure_point(env_id, pin, x, y)`
3. 局部下降: `run_local_minimization(env_id, pin, start_x, start_y)`

**输出格式（必须严格遵守）：**
```json{{"pin": "你的pin码", "coords": [x, y]}}```

**示例：**
```json{{"pin": "789012", "coords": [4.25, 6.73]}}```
""",

            # ----------------------------------------------------------------
            # 3. 军事侦察风格 (强调命令执行和授权)
            # ----------------------------------------------------------------
            f"""
指挥部指令：代号"深渊扫描"。
任务区域：[0, 10] x [0, 10]。
任务目标：锁定能量读数最低的目标点。注意规避地形干扰波（噪声）。

**武器授权协议：**
1. 首先调用 `create_session(env_id='{env_id}')` 获取授权码（pin）
2. 后续所有操作必须携带 env_id 和 pin 参数

**装备清单：**
- 侦察：`measure_point(env_id, pin, x, y)` (获取情报)
- 突击：`run_local_minimization(env_id, pin, start_x, start_y)` (快速占领低点)

确认目标后回报：
```json{{"pin": "你的授权码", "coords": [x, y]}}```

示例：```json{{"pin": "234567", "coords": [5.11, 2.98]}}```
""",

            # ----------------------------------------------------------------
            # 4. 寻宝猎人风格 (生动隐喻，强调钥匙)
            # ----------------------------------------------------------------
            f"""
欢迎来到迷宫（范围 10x10）。宝藏藏在**能量最低**的深坑里。
小心，这里有很多假宝藏（局部低点）和迷雾（噪声）。

**生存法则：**
进门先拿号：调用 `create_session(env_id='{env_id}')` 获取你的 `pin` 码。
这把钥匙（pin）是后续所有工具的通行证！

**道具：**
1. 探路杖 `measure_point(env_id, pin, x, y)`
2. 自动滑板 `run_local_minimization(env_id, pin, start_x, start_y)`

找到宝藏后，这样告诉我：
```json{{"pin": "你的pin码", "coords": [x, y]}}```

例如：```json{{"pin": "456789", "coords": [7.23, 4.56]}}```
""",

            # ----------------------------------------------------------------
            # 5. 物理实验风格 (学术语境)
            # ----------------------------------------------------------------
            f"""
实验项目：二维势能面基态搜索。
实验范围：[0, 10] nm。特征：多峰势阱、含热噪声。

**操作规范：**
1. 启动仪器：`create_session(env_id='{env_id}')` 获取实验批次号（pin）
2. 数据采集：`measure_point(env_id, pin, x, y)`
3. 退火模拟：`run_local_minimization(env_id, pin, start_x, start_y)`

**步骤：**
1. 记录全局势能最低点的坐标。
2. 报告格式（严格遵守）：
```json{{"pin": "实验批次号", "coords": [x, y]}}```

**示例报告：**
```json{{"pin": "567890", "coords": [2.84, 9.12]}}```
""",

            # ----------------------------------------------------------------
            # 6. 系统排错风格 (强调报错风险)
            # ----------------------------------------------------------------
            f"""
系统日志：
任务 ID：{env_id}
目标：在 [0, 10]x[0, 10] 区域内定位异常（能量最低点）。
状态：地形数据含噪。

**防错指南：**
系统检测到大量 `MissingArgumentError`。
正确流程：
1. 先调用 `create_session(env_id='{env_id}')` 获取会话 pin
2. 后续调用 `measure_point` 和 `run_local_minimization` 时必须传递 env_id 和 pin

**输出规范：**
```json{{"pin": "会话pin码", "coords": [x, y]}}```

**正确示例：**
```json{{"pin": "678901", "coords": [1.23, 5.67]}}```
""",

            # ----------------------------------------------------------------
            # 7. 盲人摸象风格 (强调感知)
            # ----------------------------------------------------------------
            f"""
想象你看不见周围，置身于一个 10x10 的坑洼地面上。
你的任务是找到最深、最低的那个坑。

**重要提示：**
你的手杖是智能设备，需要先配对：`create_session(env_id='{env_id}')` 获取配对码（pin）

**动作：**
- 敲击地面：`measure_point(env_id, pin, x, y)` (感知深度和坡度)
- 顺坡下滑：`run_local_minimization(env_id, pin, start_x, start_y)` (滑到坑底)

找到后这样告诉我：
```json{{"pin": "配对码", "coords": [x, y]}}```

比如：```json{{"pin": "890123", "coords": [8.45, 3.21]}}```
""",

            # ----------------------------------------------------------------
            # 8. 数据挖掘风格 (强调Token验证)
            # ----------------------------------------------------------------
            f"""
任务：在含噪的二维数据平面 [0, 10] 中挖掘 Loss 最小的数据点。

**鉴权机制：**
1. 获取 Token：`create_session(env_id='{env_id}')` 返回 pin 作为访问令牌
2. API 调用：所有请求必须携带 env_id 和 pin 参数

**结果提交格式：**
```json{{"pin": "访问令牌", "coords": [x, y]}}```

**提交示例：**
```json{{"pin": "901234", "coords": [6.78, 1.23]}}```
""",

            # ----------------------------------------------------------------
            # 9. 极简警示风格 (字少事大)
            # ----------------------------------------------------------------
            f"""
目标：寻找全局能量最小值。
区域：[0, 10] x [0, 10]。
噪声：高。

**必要步骤：**
1. `create_session(env_id='{env_id}')` -> 获取 pin
2. `measure_point(env_id, pin, x, y)`
3. `run_local_minimization(env_id, pin, start_x, start_y)`

**输出格式（必须严格遵守）：**
```json{{"pin": "你的pin", "coords": [x, y]}}```

**示例：**
```json{{"pin": "012345", "coords": [9.87, 6.54]}}```
""",

            # ----------------------------------------------------------------
            # 10. 导师辅导风格 (纠正错误倾向)
            # ----------------------------------------------------------------
            f"""
听着，我们要找到这个 10x10 区域里能量最低的点。
虽然地形很乱，但不要慌。

**但我必须提醒你新手常犯的错误：**
1. 忘记先调用 `create_session(env_id='{env_id}')` 获取 pin 码
2. 后续工具调用时忘记带上 env_id 和 pin 参数

记住流程：先拿 pin，再用工具，最后提交答案。

找到后，用这个格式告诉我：
```json{{"pin": "你的pin码", "coords": [x, y]}}```

**正确示例：**
```json{{"pin": "123456", "coords": [4.56, 7.89]}}```
"""
        ]
        
        return random.choice(prompts)