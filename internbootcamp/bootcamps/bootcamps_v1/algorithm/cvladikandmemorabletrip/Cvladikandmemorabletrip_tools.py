import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cvladikandmemorabletrip.Cvladikandmemorabletrip_reward_calculator import CvladikandmemorabletripRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def compute_max_comfort(n, a):
    # 预处理每个城市的最左和最右出现位置
    lmost = {}
    rmost = {}
    for i in range(n):
        city = a[i]
        if city not in lmost:
            lmost[city] = i
        rmost[city] = i
    
    dp = [0] * (n + 1)
    
    for i in range(n):
        dp[i+1] = dp[i]  # 默认不选当前段
        
        segment_cities = set()
        current_xor = 0
        min_l = n  # 当前段最小左边界
        valid = True
        
        # 从i往左扫描
        for j in range(i, -1, -1):
            city = a[j]
            
            # 检查该城市是否违反右边界约束
            if rmost.get(city, -1) > i:
                valid = False
                break
            
            # 更新当前段最小左边界
            min_l = min(min_l, lmost[city])
            
            # 仅当j到达当前段理论最小左边界时进行状态转移
            if j == min_l and valid:
                # 计算当前段的XOR
                if city not in segment_cities:
                    segment_cities.add(city)
                    current_xor ^= city
                
                # 状态转移
                dp[i+1] = max(dp[i+1], dp[j] + current_xor)
    
    return dp[n]

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CvladikandmemorabletripVerificationTool(BaseTool):
    """Cvladikandmemorabletrip验证工具"""
    
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
            score = CvladikandmemorabletripRewardCalculator.verify_score(
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
            logger.error(f"CvladikandmemorabletripVerificationTool执行错误: {str(e)}")
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
    def _rule_description():
        return """## 规则详解
    *分段规则**：选择的各分段必须满足：若某分段包含城市x的乘客，则该城市所有乘客必须在同一分段
    *舒适度计算**：每个分段的舒适度是该段内不同城市代码的异或(XOR)值
    *目标**：选择若干不相交分段，使总舒适度最大"""
