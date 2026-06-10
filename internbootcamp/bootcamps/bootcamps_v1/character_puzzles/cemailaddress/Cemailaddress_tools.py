import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cemailaddress.Cemailaddress_reward_calculator import CemailaddressRewardCalculator

# 导入依赖库
import random
import string
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CemailaddressVerificationTool(BaseTool):
    """Cemailaddress验证工具"""
    
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
            score = CemailaddressRewardCalculator.verify_score(
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
            logger.error(f"CemailaddressVerificationTool执行错误: {str(e)}")
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
    def _generate_part(self, part_type):
        """生成符合规范的邮箱部分（local或domain）"""
        while True:
            length = random.randint(self.min_local_length if part_type == "local" else self.min_domain_length,
                                   self.max_local_length if part_type == "local" else self.max_domain_length)

            # 首尾必须是小写字母
            first = random.choice(string.ascii_lowercase)
            last = random.choice(string.ascii_lowercase)

            # 中间字符生成（避免连续点）
            middle = []
            for _ in range(length-2):
                choices = string.ascii_lowercase
                if middle and middle[-1] != '.':
                    choices += '.'
                middle.append(random.choice(choices))

            # 拼接并验证
            candidate = first + ''.join(middle) + last
            if '.' in candidate:
                candidate = re.sub(r'\.{2,}', '.', candidate)  # 移除连续点
            if (candidate[0] not in ('.', '@') and 
                candidate[-1] not in ('.', '@') and 
                '@' not in candidate):
                return candidate

    def _generate_email(self):
        """生成合法邮箱并确保对应输入字符串具有唯一最优解"""
        while True:
            local = self._generate_part("local")
            domain = self._generate_part("domain")
            email = f"{local}@{domain}"

            # 生成输入字符串并验证唯一最优解
            input_str = (
                email[0] +
                email[1:-1].replace('@', 'at').replace('.', 'dot') +
                email[-1]
            )

            # 确保输入字符串中仅包含一个at（对应邮箱中的@）
            if input_str.count('at') == 1 and 'at' not in [input_str[:2], input_str[-2:]]:
                return email, input_str
