import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CxortreeInstructionGenerator(BaseInstructionGenerator):
    """Cxortree Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_val=1000):
        """
        初始化Cxortree指令生成器
        
        Args:
            max_n: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # 生成序列的最大长度
        self.max_val = max_val  # 生成数的最大值
    
    def case_generator(self):
        # 生成测试用例
        n = random.randint(2, self.max_n)
        elements = set()
        while len(elements) < n:
            elements.add(random.randint(0, self.max_val))
        elements = list(elements)
        random.shuffle(elements)
        # 计算正确答案
        correct_output = calculate_min_removals(elements)
        return {
            'input': elements,
            'output': correct_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        elements = question_case['input']
        n = len(elements)
        elements_str = ' '.join(map(str, elements))
        example_input = "0 1 5 2 6"
        example_output = 1
        return f"""给定一个由不同非负整数组成的序列，你需要删除最少数量的元素，使得剩下的序列是“好的”。一个序列是“好的”当且仅当根据以下规则构建的图是一棵树：

- 对于每个元素b_i，找到另一个元素b_j（j≠i），使得b_i XOR b_j的值最小。在b_i和b_j之间添加一条无向边。
- 形成的图必须是一棵树（连通且无环）。

输入格式：
第一行是序列长度n，第二行是n个不同的非负整数。

输出格式：
输出需要删除的最少元素数目。

示例输入：
5
{example_input}
示例输出：
{example_output}

现在的问题实例是：
{n}
{elements_str}

请确保你的答案仅包含一个整数，并放置在[answer]标签内，例如：[answer]{example_output}[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

