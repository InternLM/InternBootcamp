import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DlosttreeInstructionGenerator(BaseInstructionGenerator):
    """Dlosttree Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dlosttree指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，默认随机生成节点数范围2-20
        """
        self.params = params
    
    def case_generator(self):
        """
        生成随机树结构实例
        """
        n = self.params.get('n', random.randint(2, 20))
        
        def generate_random_tree(size):
            if size == 1:
                return []
            nodes = list(range(1, size+1))
            random.shuffle(nodes)
            edges = []
            for i in range(1, size):
                parent = random.choice(nodes[:i])
                edges.append([nodes[i], parent])
            return edges
        
        edges = generate_random_tree(n)
        return {'n': n, 'edges': edges}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        生成包含谜题背景、规则和格式要求的完整问题描述
        """
        n = question_case['n']
        query_limit = (n + 1) // 2  # ⌈n/2⌉
        
        prompt = f"""你是嘉年华游戏的参与者，需要猜出包含{n}个节点的树结构。节点编号为1到{n}，树边需要完全还原。

## 游戏规则
1. 你可以进行最多{query_limit}次距离查询
2. 每次查询格式："? r" (1 ≤ r ≤ {n})
3. 每次返回n个整数表示各节点到r的最短距离

## 胜利条件
通过有限次数的查询确定所有树边。正确输出格式：
1. 第一行为"!"
2. 后续n-1行每行两个用空格分隔的整数表示边

## 当前题目
需要还原的树共有{n}个节点。请设计查询策略并输出正确答案。

请将最终答案按以下格式包裹在[answer]标签内：
[answer]
!
a1 b1
a2 b2
...[/answer]"""

        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

