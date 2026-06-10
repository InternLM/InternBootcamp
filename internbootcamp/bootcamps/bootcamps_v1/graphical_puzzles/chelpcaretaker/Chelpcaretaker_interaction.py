from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.chelpcaretaker.Chelpcaretaker_reward_calculator import ChelpcaretakerRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def solve_turboplow(n, m):
    rf = False
    if n > m:
        n, m, rf = m, n, True
    w = -1 if m == 9 else 1
    Z = ((7, 2, 2), (2, 2, 7), (1, 7, 1), (4, 7, 4))
    Zx = []
    for x in range(n):
        current = []
        for i, j, k in Z:
            current.append((i << x, j << x, k << x))
        Zx.append(current)
    q = [tuple([0] * m)]
    d = {q[0]: 0}
    pr = {q[0]: None}

    def put(p, x, y, i, j, k):
        res = False
        pp = list(p)
        for vi, vj, vk in Zx[x]:
            if (i & vi) or (j & vj) or (k & vk):
                continue
            pp[y] = i | vi
            if y + 1 >= m:
                continue
            pp[y+1] = j | vj
            if y + 2 >= m:
                continue
            pp[y+2] = k | vk
            pc = tuple(pp)
            if pc in d:
                continue
            d[pc] = d[p] + 1
            pr[pc] = p
            q.append(pc)
            res = True
        return res

    for p in q:
        jm = m
        im = n
        for j in range(1, m - 1):
            if j > jm:
                break
            if j + 1 >= m:
                continue
            p1, p2, p3 = p[j-1], p[j], p[j+1]
            for i in range(1, n - 1):
                if i > im:
                    break
                if p2 & (3 << i):
                    continue
                if (p1 & (1 << i)) and (p2 & (1 << (i-1))):
                    continue
                if put(p, i-1, j-1, p1, p2, p3) and im == n:
                    im = i + w
                    jm = j - 1

    max_k = -1
    best_key = None
    for key, value in d.items():
        if value > max_k:
            max_k = value
            best_key = key

    if best_key is None:
        return 0, ['.' * m for _ in range(n)]

    r = [['.'] * m for _ in range(n)]
    current = best_key
    l = 'A'
    while pr.get(current) is not None:
        prev = pr[current]
        for y in range(m):
            for x in range(n):
                if (current[y] & (1 << x)) and not (prev[y] & (1 << x)):
                    r[x][y] = l
        current = prev
        l = chr(ord(l) + 1)

    if rf:
        transposed = []
        for col in range(m):
            transposed_row = []
            for row in range(n):
                transposed_row.append(r[row][col])
            transposed.append(''.join(transposed_row))
        r = transposed
    else:
        r = [''.join(row) for row in r]

    return max_k, r

def is_valid_t_shape(coords):
    if len(coords) != 5:
        return False
    min_r = min(r for r, _ in coords)
    min_c = min(c for _, c in coords)
    translated = set((r - min_r, c - min_c) for r, c in coords)
    patterns = [
        {(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)},
        {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)},
        {(0, 1), (1, 1), (2, 0), (2, 1), (2, 2)},
        {(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)},
    ]
    return translated in patterns


class ChelpcaretakerInteraction(BaseInteraction):
    """Chelpcaretaker交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = ChelpcaretakerRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Chelpcaretaker问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法

