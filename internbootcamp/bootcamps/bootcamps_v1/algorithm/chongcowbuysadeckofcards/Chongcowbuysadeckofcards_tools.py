import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.chongcowbuysadeckofcards.Chongcowbuysadeckofcards_reward_calculator import ChongcowbuysadeckofcardsRewardCalculator

# 导入依赖库
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ChongcowbuysadeckofcardsVerificationTool(BaseTool):
    """Chongcowbuysadeckofcards验证工具"""
    
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
            score = ChongcowbuysadeckofcardsRewardCalculator.verify_score(
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
            logger.error(f"ChongcowbuysadeckofcardsVerificationTool执行错误: {str(e)}")
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
    @staticmethod
    def calculate_min_turns(n, cards):
        # 预处理卡片数据
        color = [1 if c['color'] == 'B' else 0 for c in cards]
        r = [c['r'] for c in cards]
        b = [c['b'] for c in cards]

        total_r = sum(r)
        total_b = sum(b)
        max_rsave = total_r  # 红令牌最多能节省的总量

        # DP状态定义：dp[mask][rsave] = 最大bsave
        dp = [[-1]*(max_rsave+1) for _ in range(1<<n)]
        dp[0][0] = 0  # 初始状态

        for mask in range(1<<n):
            # 计算当前拥有的红蓝卡数量
            current_r = sum(0 if color[i] else 1 
                          for i in range(n) if (mask >> i) & 1)
            current_b = sum(1 if color[i] else 0 
                          for i in range(n) if (mask >> i) & 1)

            for rsave in range(max_rsave+1):
                if dp[mask][rsave] == -1:
                    continue

                # 尝试购买下一张卡片
                for next_card in range(n):
                    if (mask & (1 << next_card)) == 0:
                        # 计算实际需要支付的令牌
                        needed_r = max(r[next_card] - current_r, 0)
                        needed_b = max(b[next_card] - current_b, 0)

                        # 累计节省的令牌
                        new_rsave = rsave + (r[next_card] - needed_r)
                        new_bsave = dp[mask][rsave] + (b[next_card] - needed_b)
                        new_mask = mask | (1 << next_card)

                        # 更新状态
                        if new_rsave <= max_rsave and new_bsave > dp[new_mask][new_rsave]:
                            dp[new_mask][new_rsave] = new_bsave

        # 计算最终结果
        min_ops = max(total_r, total_b)  # 初始值
        full_mask = (1 << n) - 1

        for rsave in range(max_rsave+1):
            if dp[full_mask][rsave] != -1:
                required_r = max(total_r - rsave, 0)
                required_b = max(total_b - dp[full_mask][rsave], 0)
                min_ops = min(min_ops, max(required_r, required_b))

        return min_ops + n  # 加上购买卡片的n次操作
