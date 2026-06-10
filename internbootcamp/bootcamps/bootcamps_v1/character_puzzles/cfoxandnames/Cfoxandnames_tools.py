import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cfoxandnames.Cfoxandnames_reward_calculator import CfoxandnamesRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def solve_puzzle(names):
    graph = defaultdict(list)
    for c in string.ascii_lowercase:  # 初始化所有字母节点
        graph[c] = []
    
    # 构建字母约束关系图
    for i in range(len(names)-1):
        a, b = names[i], names[i+1]
        min_len = min(len(a), len(b))
        j = 0
        while j < min_len and a[j] == b[j]:
            j += 1
        
        if j == min_len:  # 处理前缀情况
            if len(a) > len(b):
                return "Impossible"
            continue
        
        # 添加字符顺序约束：a[j]必须出现在b[j]之前
        x, y = a[j], b[j]
        graph[y].append(x)  # 修正方向：y依赖x → x必须出现在y前面
    
    # 拓扑排序
    in_degree = {c:0 for c in string.ascii_lowercase}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    
    queue = deque([c for c in string.ascii_lowercase if in_degree[c] == 0])
    top_order = []
    
    while queue:
        u = queue.popleft()
        top_order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    return "Impossible" if len(top_order)!=26 else "".join(reversed(top_order))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CfoxandnamesVerificationTool(BaseTool):
    """Cfoxandnames验证工具"""
    
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
            score = CfoxandnamesRewardCalculator.verify_score(
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
            logger.error(f"CfoxandnamesVerificationTool执行错误: {str(e)}")
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
    def _generate_names(self, n):
        names = set()
        char_pool = random.sample(string.ascii_lowercase, random.randint(3,5))  # 限制字符集增加冲突

        while len(names) < n:
            length = random.randint(self.min_length, self.max_length)
            name = "".join(random.choices(char_pool, k=length))
            names.add(name)
        return list(names)
