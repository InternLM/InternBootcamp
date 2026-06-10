import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import re
import random

# === 源文件中的全局函数 ===

def compute_expected_outputs(n, m, edges, queries):
    vert = defaultdict(list)
    indeg = defaultdict(int)
    outdeg = defaultdict(int)
    
    # 修正边处理逻辑：u为较大编号的员工（初始薪金更高）
    for a, b in edges:
        u = max(a, b)
        v = min(a, b)
        vert[u].append(v)
        indeg[u] += 1
        outdeg[v] += 1
    
    ans = 0
    for i in range(1, n+1):
        ans += indeg[i] * outdeg[i]
    expected = [ans]
    
    for v in queries:
        # 移除当前节点贡献
        ans -= indeg[v] * outdeg[v]
        
        # 处理所有指向v的边（反向边）
        sons = list(vert[v])
        for son in sons:
            # 移除son节点原有贡献
            ans -= indeg[son]
            # 增加反转边后的贡献
            ans += (outdeg[son] - 1)
            
            # 调整度数
            indeg[v] -= 1
            outdeg[v] += 1
            indeg[son] += 1
            outdeg[son] -= 1
            
            # 添加反向边
            vert[son].append(v)
        
        # 清空原边
        vert[v].clear()
        # 添加新贡献
        ans += indeg[v] * outdeg[v]
        expected.append(ans)
    
    return expected


class FkonradandcompanyevaluationRewardCalculator(BaseRewardCalculator):
    """Fkonradandcompanyevaluation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\[.*?\])\s*\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            # 处理各种数字格式
            numbers = list(map(int, re.findall(r'-?\d+', last_match)))
            return numbers
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 严格验证答案长度和数值
        expected = identity['expected_outputs']
        return (
            isinstance(solution, list) and
            len(solution) == len(expected) and
            all(x == y for x, y in zip(solution, expected))
        )
    
    # 其他额外方法

