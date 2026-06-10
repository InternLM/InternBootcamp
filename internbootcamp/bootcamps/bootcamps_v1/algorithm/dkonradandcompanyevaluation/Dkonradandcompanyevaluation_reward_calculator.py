import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def compute_correct_output(n, m, edges, updates):
    G = [[] for _ in range(n + 1)]
    for a, b in edges:
        G[a].append(b)
        G[b].append(a)
    
    arr = list(range(n + 1))
    deg = [len(g) for g in G]
    gtrs = [[] for _ in range(n + 1)]
    cnt = [0] * (n + 1)
    
    ans = 0
    for u in range(1, n + 1):
        if deg[u] > 320:
            gtrs[u] = [v for v in G[u] if arr[v] > arr[u]]
            ans += (deg[u] - len(gtrs[u])) * len(gtrs[u])
        else:
            cnt[u] = sum(1 for v in G[u] if arr[v] > arr[u])
            ans += (deg[u] - cnt[u]) * cnt[u]
    
    correct_outputs = [ans]
    q = len(updates)
    
    for t in range(1, q + 1):
        u = updates[t - 1]
        ans -= (deg[u] - (len(gtrs[u]) if deg[u] > 320 else cnt[u])) * (len(gtrs[u]) if deg[u] > 320 else cnt[u])
        
        candidates = gtrs[u] if deg[u] > 320 else G[u]
        processed = [v for v in candidates if arr[u] < arr[v]]
        
        for v in processed:
            ans_before = (deg[v] - (len(gtrs[v]) if deg[v] > 320 else cnt[v])) * (len(gtrs[v]) if deg[v] > 320 else cnt[v])
            if deg[v] > 320:
                gtrs[v].append(u)
            else:
                cnt[v] += 1
            ans_after = (deg[v] - (len(gtrs[v]) if deg[v] > 320 else cnt[v])) * (len(gtrs[v]) if deg[v] > 320 else cnt[v])
            ans += (ans_after - ans_before)
        
        if deg[u] > 320:
            gtrs[u].clear()
        else:
            cnt[u] = 0
        
        arr[u] = n + t
        correct_outputs.append(ans)
    
    return correct_outputs


class DkonradandcompanyevaluationRewardCalculator(BaseRewardCalculator):
    """Dkonradandcompanyevaluation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        numbers = []
        for line in matches[-1].strip().splitlines():
            stripped = line.strip()
            if stripped.isdigit() or (stripped.startswith('-') and stripped[1:].isdigit()):
                numbers.append(int(stripped))
        return numbers if len(numbers) > 0 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('correct_outputs', [])
        if solution is None:
            return False
        return solution == expected
    
    # 其他额外方法

