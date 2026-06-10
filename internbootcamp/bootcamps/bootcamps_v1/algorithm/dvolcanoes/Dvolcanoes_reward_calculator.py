import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DvolcanoesRewardCalculator(BaseRewardCalculator):
    """Dvolcanoes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output)
        if matches:
            return matches[-1].strip()
        else:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        m = identity['m']
        volcanoes = identity['volcanoes']
        # 检查终点是否是火山
        if (n, n) in volcanoes:
            correct = -1
        else:
            # 使用优化后的逻辑计算正确的解
            x = {}
            times = set()
            times.add(1)
            times.add(n)
            valid = True
            for a, b in volcanoes:
                if a == n and b == n:
                    valid = False
                    correct = -1
                    break
                times.add(a)
                if a < n:
                    times.add(a + 1)
                if a in x:
                    x[a].add(b)
                else:
                    x[a] = {b}
            if not valid:
                correct = -1
            else:
                timelist = sorted(times)
                rays = []
                for time in timelist:
                    if time == 1:
                        if 1 in x:
                            y_list = sorted(x[1])
                            y_list.append(n + 1)
                            j = 0
                            current_rays = []
                            lastray = None
                            for y in y_list:
                                if j == 0:
                                    current_start = 1
                                    current_end = y - 1
                                else:
                                    current_start = y_prev + 1
                                    current_end = y - 1
                                if current_start <= current_end:
                                    if lastray is None:
                                        lastray = (current_start, current_end)
                                    else:
                                        if current_start <= lastray[1]:
                                            lastray = (lastray[0], current_end)
                                        else:
                                            current_rays.append(lastray)
                                            lastray = (current_start, current_end)
                                y_prev = y
                            if lastray is not None:
                                current_rays.append(lastray)
                            rays = current_rays
                        else:
                            rays = [(1, n)]
                    else:
                        y_list = []
                        if time in x:
                            y_list = sorted(x[time])
                        y_list.append(n + 1)
                        new_rays = []
                        lastray = None
                        for ray in rays:
                            thisray = ray
                            j = 0
                            while j < len(y_list) and y_list[j] <= thisray[1]:
                                if y_list[j] >= thisray[0]:
                                    if thisray[0] <= y_list[j] - 1:
                                        new_rays.append((thisray[0], y_list[j] - 1))
                                    thisray = (y_list[j] + 1, thisray[1])
                                    if thisray[0] > thisray[1]:
                                        break
                                j += 1
                            if thisray[0] <= thisray[1]:
                                if lastray is None:
                                    lastray = thisray
                                else:
                                    if thisray[0] <= lastray[1]:
                                        lastray = (lastray[0], thisray[1])
                                    else:
                                        new_rays.append(lastray)
                                        lastray = thisray
                            else:
                                lastray = None
                        if lastray is not None:
                            new_rays.append(lastray)
                        rays = new_rays
                    if not rays:
                        break
                if rays and rays[-1][1] == n:
                    correct = (n - 1) * 2
                else:
                    correct = -1
        # 解析用户答案
        try:
            solution_int = int(solution)
        except ValueError:
            return False
        # 比较
        return solution_int == correct
    
    # 其他额外方法

