"""
Robot Reach Instruction Generator - 机器人运动规划指令生成器
"""
from typing import Dict, Any
import random

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.bot_bootcamp.bot_server import SimulationContext


class BotInstructionGenerator(BaseInstructionGenerator):
    """机器人到达任务指令生成器"""
    
    def __init__(self, init_obs, joint_angles):
        """
        初始化生成器
        
        Args:
            data_source: 数据源标识
            **kwargs: 其他参数
        """
        super().__init__()
        self.env = SimulationContext()
        self.init_obs = init_obs
        self.joint_angles = joint_angles
    
    def case_generator(self) -> Dict[str, Any]:
        """
        生成机器人运动规划任务案例
        
        Returns:
            Dict[str, Any]: 任务信息字典
        """
        case_data = self.env.generate_static_case_data(self.init_obs, self.joint_angles)
            
        return case_data

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        """
        根据任务信息生成提示语（包含10种变体以增强泛化性）
        
        Args:
            identity (Dict[str, Any]): 任务信息字典，包含 case_id, target, obstacles 等
        
        Returns:
            str: 生成的提示词
        """
        target_str = f"[{identity['target'][0]:.3f}, {identity['target'][1]:.3f}, {identity['target'][2]:.3f}]"
        prompts = [
f"""
任务：你是一个 KUKA iiwa 机械臂的运动规划控制大脑。你的目标是控制机械臂避开障碍物，将末端执行器移动到目标坐标 {target_str}。

重要参数：
- Case ID: {identity['case_id']}

可用工具：
1. **初始化**：首先必须调用 `create_session` 构造场景并获取关键的 `pin` 码。
2. **安全校验**：在规划过程中，用 `check_collision` 验证当前角度是否安全。

挑战模式：
1. **关节控制**：你需要规划7个关节的角度，每个关节的角度范围均为 {self.joint_angles}。
2. **盲盒障碍**：场景中存在 {len(identity['obstacles'])} 个位置未知的障碍物。

成功标准（必须同时满足）：
1. **精度达标**：末端实际位置与目标位置的欧几里得距离必须 **小于 0.05 米**。
2. **安全无碰**：确保路径安全，即未发生碰撞。

请在最终答案处严格使用以下格式包裹结果：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
【系统指令】KUKA iiwa 运动控制单元初始化。
【当前任务】执行末端执行器定位，目标坐标：{target_str}。

【环境参数】
- 任务编号 (Case ID): {identity['case_id']}
- 关节约束: 7轴自由度，角度范围 {self.joint_angles}。
- 障碍物探测: 检测到 {len(identity['obstacles'])} 个未知障碍物。

【系统接口】
1. **Session建立**: 调用 `create_session` 初始化环境，必须保存返回的 `pin` 码用于后续鉴权。
2. **碰撞预警**: 每次计算出新角度后，用 `check_collision` 进行验证。

【完成指标】
- 精度误差 < 0.05m。
- 碰撞状态: False。

请输出最终计算得出的7个关节角度，格式严格如下：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
警报！这是一次紧急救援任务。你控制着一台 KUKA iiwa 机械臂，需要将医疗物资（末端执行器）精确送达坐标 {target_str}。

任务代号: {identity['case_id']}

目前的严峻形势：
1. 操控限制：你需要精确调整7个关节的角度（范围 {self.joint_angles}）以逼近目标。
2. 视野受限：雷达显示有 {len(identity['obstacles'])} 个隐形障碍物挡在路上。

救援辅助协议：
- 立即启动 `create_session` 建立连接并获取通信凭证 `pin`。
- 任何移动指令下达前，可以通过 `check_collision(pin, joint_angles)` 模拟器确认路径安全。

任务成功的唯一标准是：在不发生任何碰撞的前提下，将误差控制在 0.05 米以内。

计算完毕后，请立即发送你的关节角度配置：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
Problem Statement: KUKA iiwa Motion Planning (Case ID: {identity['case_id']})

作为一个算法竞赛选手，你需要编写一个策略来控制机械臂。
目标：Target Position = {target_str}。

API Reference:
- `create_session`: Initializes the environment. Returns a session `pin`.
- `check_collision`: Oracle function to validate if a configuration is safe.

Constraints:
- 搜索空间：7维关节空间，每个维度范围 {self.joint_angles}。
- 黑盒环境：存在 {len(identity['obstacles'])} 个不可见障碍物，触碰即失败。

Accepted Solution Criteria:
- Euclidean Distance(End_Effector, Target) < 0.05
- Collision_Count == 0

请提交你的最终解向量：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
唤醒协议已启动... 
你好，核心代号 {identity['case_id']}。你是安装在空间站上的 KUKA iiwa 智能中枢。
现在的任务是修复船体裂缝，修复点位于 {target_str}。

操作规程：
首先执行 `create_session` 获取访问密钥（pin）。在每次伺服调整前，可以调用 `check_collision` 子程序进行全息模拟，确保不会触碰那 {len(identity['obstacles'])} 块漂浮的未知碎片。

操作提示：你必须精准校准7个伺服电机（范围 {self.joint_angles}）。
务必精准，误差不能超过 0.05 米，否则气密性修复失败。

输出你的最终电机指令序列：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
**自动化测试用例执行报告**
**测试 ID**: {identity['case_id']}
**被测对象**: KUKA iiwa 7-DOF Manipulator

**测试工具链**:
- Setup: 调用 `create_session` 获取测试凭证 `pin`。
- Validation: 使用 `check_collision` 验证配置安全性。

**测试前置条件**:
1. 目标点设定为: {target_str}。
2. 关节活动范围限制在 {self.joint_angles}。
3. 模拟环境中预置 {len(identity['obstacles'])} 个盲区障碍物。

**通过标准 (Pass Criteria)**:
- 最终坐标误差 < 0.05m
- 路径安全性：Safe (No Collision)

请生成满足上述条件的关节配置数据，并填入下方：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
考虑一个七自由度的机械臂系统（KUKA iiwa），其构型空间由7个关节角度 $\\theta_i$ 定义，且 $\\theta_i \\in {self.joint_angles}$。
任务 ID：{identity['case_id']}。

我们需要寻找一个向量 $\\Theta = [\\theta_1, ..., \\theta_7]$，使得机械臂末端位置 $P_{{end}}$ 逼近目标点 $P_{{target}} = {target_str}$。
同时，系统受到 {len(identity['obstacles'])} 个未知几何体的约束（障碍物），路径必须满足 $C(\\Theta) = 0$（无碰撞）。

辅助算子：
1. 初始化算子 $S \\rightarrow pin$：通过 `create_session` 获取。
2. 碰撞检测算子 $Check(pin, \\Theta)$：通过 `check_collision` 实现。

收敛条件：$||P_{{end}} - P_{{target}}||_2 < 0.05$。

请给出满足条件的解向量：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
欢迎来到 KUKA 机械臂操作训练营！今天你的考核任务是 Case {identity['case_id']}。

你的目标很简单：把机械手移动到 {target_str}。

考核提示：
- 进场先拿号：用 `create_session` 拿到你的 `pin` 码。
- 别瞎撞：每次想动之前，用 `check_collision(pin, joint_angles)` 帮你看一眼会不会撞车。

这次考核有几个难点：
1. **精准操控**：你需要调整7个关节（范围 {self.joint_angles}）以精确抵达目标。
2. **小心地雷**：场上有 {len(identity['obstacles'])} 个看不见的障碍物，碰到就挂科。

只要最后距离目标小于 0.05 米且没撞到东西，你就通过了。

想好了吗？请把你的答案写在下面：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
指挥官，我们需要制定一条行动路线。
行动代号：{identity['case_id']}
目标地点：{target_str}

战术支持：
- 通讯建立：执行 `create_session` 获取加密 `pin`。
- 沙盘推演：行动前可以经由 `check_collision` 验证坐标安全性。

资产状况：
- KUKA iiwa 机械臂，7个关节均可调（范围 {self.joint_angles}）。

战场情报：
- 侦测到 {len(identity['obstacles'])} 个隐形威胁区域。

任务要求：
1. 抵达精度需在 0.05 米圆周误差内。
2. 确保全员安全，零碰撞。

请下达最终的关节角度指令：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
""",
f"""
我是 KUKA iiwa 的数字孪生意识。现在的 Case ID 是 {identity['case_id']}。
我的手指（末端执行器）渴望触碰那个点：{target_str}。

为了开始这段旅程，我必须先呼唤 `create_session` 来找回我的灵魂契约（pin）。
为了完成任务，我需要精确转动我的7个关节（范围都在 {self.joint_angles} 内）。
更糟糕的是，我感觉到周围有 {len(identity['obstacles'])} 个看不见的东西。每一次想象中的移动，我都要小心翼翼地用 `check_collision` 询问是否安全。

我必须做到：
1. 离目标非常近（< 0.05米）。
2. 绝对不受伤（无碰撞）。

这是我思考后的最佳姿态：
```json{{\"pin\": pin码, \"joint_angles\": [angle_1, angle_2, ..., angle_7]}}```
"""
]

        # 随机选择一个模板
        return random.choice(prompts)
