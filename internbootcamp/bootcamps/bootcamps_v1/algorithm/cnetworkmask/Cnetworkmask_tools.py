import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnetworkmask.Cnetworkmask_reward_calculator import CnetworkmaskRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def compute_mask(ip_list, net_count):
    mask_elem = (128, 64, 32, 16, 8, 4, 2, 1)
    for i in range(4):
        diff = set()
        for ip in ip_list:
            diff.add(tuple(ip[:i+1]))
        if len(diff) >= net_count:
            cur_mask_block = 0
            for j in range(8):
                cur_mask_block += mask_elem[j]
                abs_diff = set()
                for ip in ip_list:
                    cip = list(ip[:i])
                    current_octet = ip[i] & cur_mask_block
                    cip.append(current_octet)
                    abs_diff.add(tuple(cip))
                current_network_count = len(abs_diff)
                if current_network_count == net_count:
                    mask_parts = ['255'] * i
                    mask_parts.append(str(cur_mask_block))
                    mask_parts.extend(['0'] * (3 - i))
                    return '.'.join(mask_parts)
                elif current_network_count > net_count:
                    return '-1'
            return '-1'
    return '-1'

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CnetworkmaskVerificationTool(BaseTool):
    """Cnetworkmask验证工具"""
    
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
            score = CnetworkmaskRewardCalculator.verify_score(
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
            logger.error(f"CnetworkmaskVerificationTool执行错误: {str(e)}")
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
    def _gen_unsolvable_case(self):
        ips = [
            [255, random.randint(0,255), random.randint(0,255), random.randint(0,255)],
            [0,   random.randint(0,255), random.randint(0,255), random.randint(0,255)]
        ]
        while ips[0] == ips[1]:
            ips[1] = [0, random.randint(0,255), random.randint(0,255), random.randint(0,255)]
        return {
            'n': 2,
            'k': 1,
            'ips': ips
        }

    def _gen_solvable_case(self):
        mask_m = random.randint(8, 28)
        network_prefixes = set()
        while len(network_prefixes) < self.net_count:
            prefix = random.getrandbits(mask_m)
            network_prefixes.add(prefix)

        ips = []
        ips_set = set()

        # Generate unique IPs for network prefixes
        for prefix in network_prefixes:
            while True:
                new_ip = self.generate_ip(prefix, mask_m)
                ip_tuple = tuple(new_ip)
                if ip_tuple not in ips_set:
                    ips.append(new_ip)
                    ips_set.add(ip_tuple)
                    break

        # Generate remaining IPs
        remaining = self.ip_count - self.net_count
        while remaining > 0:
            prefix = random.choice(list(network_prefixes))
            new_ip = self.generate_ip(prefix, mask_m)
            ip_tuple = tuple(new_ip)
            if ip_tuple not in ips_set:
                ips.append(new_ip)
                ips_set.add(ip_tuple)
                remaining -= 1

        random.shuffle(ips)
        return {
            'n': self.ip_count,
            'k': self.net_count,
            'ips': ips
        }

    def generate_ip(self, prefix, mask_m):
        prefix_bits = bin(prefix)[2:].zfill(mask_m)
        remaining_bits = ''.join(random.choices(['0', '1'], k=32 - mask_m))
        full_bits = prefix_bits + remaining_bits
        octets = [int(full_bits[i:i+8], 2) for i in range(0, 32, 8)]
        return octets
