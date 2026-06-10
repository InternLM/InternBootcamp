import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_min_removals(a):
    nodes = [TrieNode()]
    root_id = 0
    id_counter = 1

    # 插入每个数到Trie中
    for num in a:
        cur = root_id
        nodes[cur].size += 1
        for i in reversed(range(30)):  # 处理30位，从高位到低位
            bit = (num >> i) & 1
            if bit:
                if nodes[cur].left == -1:
                    nodes[cur].left = id_counter
                    nodes.append(TrieNode())
                    id_counter += 1
                next_cur = nodes[cur].left
            else:
                if nodes[cur].right == -1:
                    nodes[cur].right = id_counter
                    nodes.append(TrieNode())
                    id_counter += 1
                next_cur = nodes[cur].right
            cur = next_cur
            nodes[cur].size += 1

    ans = 0

    def dfs(cur, current_sum):
        nonlocal ans
        if nodes[cur].size == 2:
            if current_sum > ans:
                ans = current_sum
        # 处理左子节点
        left_child = nodes[cur].left
        if left_child != -1:
            # 计算右子节点是否存在且size>0
            right_child = nodes[cur].right
            add = 1 if (right_child != -1 and nodes[right_child].size > 0) else 0
            dfs(left_child, current_sum + add)
        # 处理右子节点
        right_child = nodes[cur].right
        if right_child != -1:
            left_child = nodes[cur].left
            add = 1 if (left_child != -1 and nodes[left_child].size > 0) else 0
            dfs(right_child, current_sum + add)

    dfs(root_id, 0)
    return len(a) - ans - 2



# === 源文件中的其他类 ===

class TrieNode:
    def __init__(self):
        self.left = -1  # 左子节点索引，-1表示不存在
        self.right = -1  # 右子节点索引，-1表示不存在
        self.size = 0  # 当前节点的大小


class CxortreeRewardCalculator(BaseRewardCalculator):
    """Cxortree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 从输出中提取最后一个[answer]标签内的数字
        matches = re.findall(r'\[answer\](\d+)\[\/answer\]', output, re.IGNORECASE)
        if matches:
            return int(matches[-1])
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证答案是否正确
        return solution == identity['output']
    
    # 其他额外方法

