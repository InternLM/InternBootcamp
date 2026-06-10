import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.evectors.Evectors_reward_calculator import EvectorsRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import List

# === 源文件中的全局函数 ===

def rotate_clockwise(x: int, y: int, times: int) -> (int, int):
    """顺时针旋转向量，times为旋转次数"""
    for _ in range(times % 4):
        x, y = y, -x
    return x, y

def possible(dx: int, dy: int, p: int, q: int) -> bool:
    """验证差分向量是否符合线性组合条件"""
    bm = p**2 + q**2
    if bm == 0:
        return dx == 0 and dy == 0
    return ((-p*dx - q*dy) % bm == 0) and ((-q*dx + p*dy) % bm == 0)

def is_possible(ax: int, ay: int, bx: int, by: int, p: int, q: int) -> bool:
    """验证所有旋转可能性"""
    for rot in range(4):
        rx, ry = rotate_clockwise(ax, ay, rot)
        dx, dy = bx - rx, by - ry
        if possible(dx, dy, p, q) or possible(-dy, dx, p, q):
            return True
    return False

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EvectorsVerificationTool(BaseTool):
    """Evectors验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = EvectorsRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"EvectorsVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法
    def _gen_solvable_case(self) -> Dict:
        """生成保证可解的案例"""
        ax = random.randint(-self.max_coord, self.max_coord)
        ay = random.randint(-self.max_coord, self.max_coord)
        p = random.randint(-self.max_coord, self.max_coord)
        q = random.randint(-self.max_coord, self.max_coord)

        # 随机选择旋转次数和系数
        rot = random.randint(0, 3)
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)

        # 构造合法B向量
        rx, ry = rotate_clockwise(ax, ay, rot)
        bx = rx + a*p + b*q
        by = ry + a*q - b*p
        return {'A': [ax, ay], 'B': [bx, by], 'C': [p, q]}

    def _gen_unsolvable_zeroC(self) -> Dict:
        """生成C=0时的不可解案例"""
        ax = random.randint(-self.max_coord, self.max_coord)
        ay = random.randint(-self.max_coord, self.max_coord)
        p = q = 0

        # 寻找不在旋转对称点上的B
        while True:
            bx = random.randint(-self.max_coord, self.max_coord)
            by = random.randint(-self.max_coord, self.max_coord)
            if not any((bx, by) == rotate_clockwise(ax, ay, r) for r in range(4)):
                return {'A': [ax, ay], 'B': [bx, by], 'C': [p, q]}

    def _gen_unsolvable_general(self) -> Dict:
        """生成普通不可解案例"""
        for _ in range(100):
            case = self._gen_solvable_case()
            ax, ay = case['A']
            bx, by = case['B']
            p, q = case['C']

            # 微调B向量破坏可解性
            delta = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            new_bx = bx + delta[0]
            new_by = by + delta[1]
            if not is_possible(ax, ay, new_bx, new_by, p, q):
                return {'A': [ax, ay], 'B': [new_bx, new_by], 'C': [p, q]}
        return {'A': [0,0], 'B': [1,0], 'C': [0,0]}  # 最终后备案例
