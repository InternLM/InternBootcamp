import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cdominoes.Cdominoes_reward_calculator import CdominoesRewardCalculator

# 导入依赖库
import random
import math
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CdominoesVerificationTool(BaseTool):
    """Cdominoes验证工具"""
    
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
            score = CdominoesRewardCalculator.verify_score(
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
            logger.error(f"CdominoesVerificationTool执行错误: {str(e)}")
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
    def generate_valid_set(self):
        """生成包含可优化空间的有效集合"""
        total = self.n * self.m
        while True:
            types = ['00', '01', '10', '11']
            probs = [0.25, 0.25, 0.25, 0.25]
            dominoes = random.choices(types, weights=probs, k=total)
            if sum(1 for d in dominoes if d in ['01','10']) > 0:
                return dominoes

    def build_optimal_matrix(self, domino_set):
        """按照官方解题算法构建最优矩阵"""
        # 统计类型
        k = defaultdict(int)
        for d in domino_set:
            if d in ['00','11']:
                k[d] += 1
            else:
                k['mix'] += 1

        # 初始化二维矩阵
        matrix = [[] for _ in range(self.n)]

        # 类型划分（参考官方解法）
        a = k['11'] // self.n
        b = (k['mix'] // 2) // self.n
        c = k['00'] // self.n

        # 基础分配
        for row in matrix:
            row += ['11']*a
            row += ['01']*b
            row += ['10']*b
            row += ['00']*c

        # 余数处理
        rem_11 = k['11'] % self.n
        rem_mix = k['mix'] % (2*self.n)
        rem_00 = k['00'] % self.n

        # Phase 1: 分配余数11
        for i in range(rem_11):
            matrix[i].append('11')

        # Phase 2: 分配余数mix
        for i in range(rem_mix):
            matrix[i%self.n].append('01' if i%2 else '10')

        # Phase 3: 分配余数00
        for i in range(rem_00):
            matrix[i].append('00')

        # 填充并校验每行长度
        for row in matrix:
            random.shuffle(row)
            while len(row) < self.m:
                # 异常处理：补充虚拟domino（理论上不应触发）
                row.append('00')
            del row[self.m:]  # 精确截断

        return matrix

    def scramble_matrix(self, matrix):
        """生成随机输入矩阵"""
        scrambled = []
        for row in matrix:
            new_row = []
            for d in row:
                if d in ['01','10']:
                    new_row.append(random.choice([d, d[::-1]]))
                else:
                    new_row.append(d)
            random.shuffle(new_row)
            scrambled.append(new_row)
        return scrambled
