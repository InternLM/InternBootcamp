import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EkarenandsupermarketRewardCalculator(BaseRewardCalculator):
    """Ekarenandsupermarket奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        class Solver:
            def __init__(self, n, b, items):
                self.n = n
                self.b = b
                self.children = [[] for _ in range(n+2)]
                self.v = [0]*(n+2)
                self.c = [0]*(n+2)
                
                for i in range(1, n+1):
                    item = items[i-1]
                    self.v[i] = item['c']
                    self.c[i] = item['d']
                    if i > 1:
                        self.children[item['x']].append(i)
                
                self.INF = float('inf')

            def solve(self):
                dp = [{} for _ in range(self.n+2)]
                
                def dfs(u):
                    node = {'use': {}, 'nouse': {}}
                    node['use'][0] = 0
                    node['nouse'][0] = 0
                    
                    for v in self.children[u]:
                        child = dfs(v)
                        merged_use = {}
                        merged_nouse = {}
                        
                        # Merge child states into current node
                        for ku in node['use']:
                            for kv in child['use']:
                                key = ku + kv
                                val = node['use'][ku] + child['use'][kv]
                                if val <= self.b:
                                    merged_use[key] = min(merged_use.get(key, self.INF), val)
                                
                            for kv in child['nouse']:
                                key = ku + kv
                                val = node['use'][ku] + child['nouse'][kv]
                                if val <= self.b:
                                    merged_use[key] = min(merged_use.get(key, self.INF), val)
                        
                        for ku in node['nouse']:
                            for kv in child['nouse']:
                                key = ku + kv
                                val = node['nouse'][ku] + child['nouse'][kv]
                                if val <= self.b:
                                    merged_nouse[key] = min(merged_nouse.get(key, self.INF), val)
                        
                        # Update current node's states
                        new_use = {}
                        for k in merged_use:
                            new_use[k] = min(node['use'].get(k, self.INF), merged_use[k])
                        for k in node['use']:
                            new_use[k] = min(new_use.get(k, self.INF), node['use'][k])
                        
                        new_nouse = {}
                        for k in merged_nouse:
                            new_nouse[k] = min(node['nouse'].get(k, self.INF), merged_nouse[k])
                        for k in node['nouse']:
                            new_nouse[k] = min(new_nouse.get(k, self.INF), node['nouse'][k])
                        
                        node['use'] = new_use
                        node['nouse'] = new_nouse
                    
                    # Add current node's options
                    new_use = {}
                    for k in node['use']:
                        newk = k + 1
                        cost = node['use'][k] + (self.v[u] - self.c[u])
                        if cost <= self.b:
                            new_use[newk] = min(node['use'].get(newk, self.INF), cost)
                    node['use'] = {**node['use'], **new_use}
                    
                    new_nouse = {}
                    for k in node['nouse']:
                        newk = k + 1
                        cost = node['nouse'][k] + self.v[u]
                        if cost <= self.b:
                            new_nouse[newk] = min(node['nouse'].get(newk, self.INF), cost)
                    node['nouse'] = {**node['nouse'], **new_nouse}
                    
                    return node
                
                root = dfs(1)
                max_items = 0
                for k in root['use']:
                    if k > max_items and root['use'][k] <= self.b:
                        max_items = k
                for k in root['nouse']:
                    if k > max_items and root['nouse'][k] <= self.b:
                        max_items = k
                return max_items

        n = identity['n']
        b = identity['b']
        items = identity['items']
        return solution == Solver(n, b, items).solve()
    
    # 其他额外方法

