import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import copy
from collections import deque




class DmarsroverInstructionGenerator(BaseInstructionGenerator):
    """Dmarsrover Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dmarsrover指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.default_params = {'max_depth': 5, 'min_inputs': 3}
        self.default_params.update(params)
    
    def case_generator(self):
        # 生成根节点（顶点1）
        root_type = random.choice(['AND', 'OR', 'XOR', 'NOT'])
        nodes = {1: {'type': root_type, 'children': []}}
        queue = deque([1])
        next_id = 2
        
        # 生成合法树结构
        while queue:
            current_id = queue.popleft()
            current_type = nodes[current_id]['type']
            
            # 确定必需子节点数
            required_children = {'AND':2, 'OR':2, 'XOR':2, 'NOT':1}.get(current_type,0)
            children = []
            
            # 生成子节点
            for _ in range(required_children):
                # 动态决定子节点类型
                if current_id == 1 or random.random() < 0.5:  # 增加逻辑门生成概率
                    child_type = random.choice(['AND', 'OR', 'XOR', 'NOT'])
                else:
                    child_type = 'IN'
                
                # 创建节点
                nodes[next_id] = {'type': child_type}
                if child_type == 'IN':
                    nodes[next_id]['value'] = random.choice([0,1])
                else:
                    nodes[next_id]['children'] = []
                    queue.append(next_id)
                children.append(next_id)
                next_id +=1
            
            nodes[current_id]['children'] = children
        
        # 确保至少min_inputs个输入节点
        def count_inputs():
            return sum(1 for n in nodes.values() if n['type'] == 'IN')
        
        while count_inputs() < self.default_params['min_inputs']:
            # 寻找可添加输入的节点
            candidates = [id for id in nodes 
                         if nodes[id]['type'] in ['AND','OR','XOR','NOT']
                         and len(nodes[id]['children']) < 
                             (2 if nodes[id]['type'] != 'NOT' else 1)]
            if not candidates:
                break
            parent = random.choice(candidates)
            new_id = next_id
            next_id +=1
            nodes[new_id] = {'type': 'IN', 'value': random.choice([0,1])}
            nodes[parent]['children'].append(new_id)
        
        # 收集所有输入节点（正确方法）
        def find_inputs():
            inputs = []
            stack = [1]
            while stack:
                node_id = stack.pop()
                node = nodes.get(node_id)
                if not node: continue
                if node['type'] == 'IN':
                    inputs.append(node_id)
                else:
                    stack.extend(node.get('children',[]))
            return sorted(inputs)
        
        input_nodes = find_inputs()
        
        # 构建节点列表（索引对齐）
        max_id = max(nodes.keys())
        nodes_list = [None]*(max_id+1)
        for id in nodes:
            nodes_list[id] = nodes[id]
        
        # 计算原始结果
        original_output = self.compute_output(nodes_list)
        
        # 计算每个输入翻转后的结果
        answer = []
        for input_id in input_nodes:
            # 深拷贝并修改
            new_nodes = copy.deepcopy(nodes_list)
            new_nodes[input_id]['value'] = 1 - new_nodes[input_id]['value']
            
            # 计算新输出
            new_output = self.compute_output(new_nodes)
            answer.append(str(new_output))
        
        return {
            'nodes': nodes_list,
            'input_order': input_nodes,
            'answer': ''.join(answer)
        }
    
    @staticmethod 
    def prompt_func(case):
        desc = []
        for node_id in range(1, len(case['nodes'])):
            node = case['nodes'][node_id]
            if not node: continue
            if node['type'] == 'IN':
                desc.append(f"顶点 {node_id}: 输入端口，初始值 {node['value']}")
            else:
                children = ', '.join(map(str, node['children']))
                desc.append(f"顶点 {node_id}: {node['type']}门，连接[{children}]")
        
        input_order = ', '.join(map(str, case['input_order']))
        return f"""火星车逻辑电路维修问题：
电路结构：
{chr(10).join(desc)}

需要分析以下输入端口（按编号排序）：{input_order}。
对于每个端口，计算其值翻转后的根节点输出。按顺序组合答案如[answer]10101[/answer]。答案只能是0和1组成的字符串。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def compute_output(self, nodes_list):
        computed = {}

        def evaluate(node_id):
            if node_id in computed:
                return computed[node_id]

            node = nodes_list[node_id]
            if node['type'] == 'IN':
                res = node['value']
            elif node['type'] == 'NOT':
                res = 1 - evaluate(node['children'][0])
            elif node['type'] == 'AND':
                res = evaluate(node['children'][0]) & evaluate(node['children'][1])
            elif node['type'] == 'OR':
                res = evaluate(node['children'][0]) | evaluate(node['children'][1])
            elif node['type'] == 'XOR':
                res = evaluate(node['children'][0]) ^ evaluate(node['children'][1])
            else:
                raise ValueError(f"Invalid node type {node['type']}")

            computed[node_id] = res
            return res

        return evaluate(1)
