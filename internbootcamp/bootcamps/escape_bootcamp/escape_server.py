import os

import random
import collections
import re
import copy
import uuid
from typing import Dict, Optional, List, Set

import json

import time

import socket
from flask import Flask, request, jsonify

import threading

import redis
import pickle

app = Flask(__name__)

PATH = os.path.dirname(os.path.abspath(__file__))


'''
风格名称:        游戏开始时告诉玩家当前所在的剧本类型
rooms：         房间名称池。当程序生成地图时，会从这个列表中随机抽取名称赋予地图上的节点
descriptions:   环境氛围描述。当玩家进入一个房间时，程序会随机从这里抽取一句话显示出来描述环境的细节。

containers:     容器/搜刮点。定义房间内可以互动的、用来存放物品的对象。
keys:           普通关键道具。作为"锁与钥匙"机制的一部分。
codes:          线索/剧情碎片。记录电子锁的密码。
final_gate:     终极关卡门。持有密码可打开游戏的最终目标点。

junk_names:     干扰道具。随机分布在房间里
'''
junk_names = ["空罐头", "旧报纸", "损坏的零件", "不知名的石头", "断掉的电线"]
ASSET_DB = {
    "深空科幻": {
        "rooms": [
            "反应堆核心", "低温休眠室", "舰桥指挥台", "气闸缓冲区", "外星标本室", 
            "反重力走廊", "量子通讯塔", "纳米维修间", "逃生舱发射口", "水培氧气园"
        ],
        "descriptions": ["全息面板闪烁着红光。", "重力发生器发出低沉的嗡嗡声。", "窗外是无尽的星海。", "地板上残留着蓝色的冷却液。", "空气中弥漫着臭氧的味道。"],
        "containers": ["生物识别保险箱", "船员储物柜", "加固的武器箱", "漂浮的补给囊"],
        "keys": ["舰长授权卡", "工程部秘钥", "同位素电池"],
        "codes": ["损坏的数据板", "刻在墙上的二进制码", "AI终端留下的日志"],
        "final_gate": "主控逃生闸",
    },
    "中世纪奇幻": {
        "rooms": [
            "炼金术士的高塔", "阴暗的地牢", "皇家藏书阁", "元素召唤阵", "废弃的王座厅", 
            "皇家军械库", "地下墓穴", "占星露台", "酒窖", "禁忌花园"
        ],
        "descriptions": ["墙上的火把忽明忽暗。", "空气中有一股硫磺味。", "古老的符文在石壁上微光闪烁。", "地上铺着厚厚的腐烂地毯。", "角落里堆满了不知名的骨头。"],
        "containers": ["符文宝箱", "龙皮背包", "被诅咒的骨灰盒", "镶金的首饰盒"],
        "keys": ["秘银钥匙", "骷髅钥匙", "水晶碎片"],
        "codes": ["羊皮纸卷轴", "沾血的日记页", "刻在石碑上的预言"],
        "final_gate": "位面传送门",
    },
    "赛博朋克": {
        "rooms": [
            "黑客藏身处", "非法义体诊所", "霓虹后巷", "服务器农场", "夜之城酒吧", 
            "浮空车停机坪", "垃圾回收站", "脑机接口实验室", "地下黑市", "无人机充电站"
        ],
        "descriptions": ["霓虹灯管滋滋作响。", "雨水顺着生锈的管道流下。", "到处是裸露的电线和电路板。", "全息广告在半空中投射出巨大的艺妓脸庞。", "低音炮的震动让地板发颤。"],
        "containers": ["黑客工具箱", "走私货运箱", "加密的数据终端", "便携式服务器"],
        "keys": ["访问芯片", "管理员指纹膜", "NFC秘钥环"],
        "codes": ["破碎的智能眼镜", "全息投影留言", "网络骇客留下的涂鸦"],
        "final_gate": "企业大厦电梯",
    },
    "维多利亚恐怖": {
        "rooms": [
            "废弃手术室", "标本陈列室", "迷雾墓园", "疯人院禁闭室", "挂满画像的走廊", 
            "祭祀地下室", "钟楼阁楼", "渗水的浴室", "被烧毁的育儿室", "人偶工坊"
        ],
        "descriptions": ["墙壁上渗出暗红色的液体。", "远处传来若有若无的哭声。", "这里冷得刺骨。", "镜子里似乎有什么东西在动。", "地板在脚下嘎吱作响。"],
        "containers": ["腐烂的木棺", "生锈的医疗柜", "上锁的日记本", "祭祀用的瓮"],
        "keys": ["生锈的黄铜钥匙", "沾血的手术刀柄", "眼球形状的宝石"],
        "codes": ["写在墙上的血书", "撕碎的病历单", "疯子的呓语纸条"],
        "final_gate": "庄园大门",
    },
    "西部荒野": {
        "rooms": [
            "喧闹的酒馆", "警长办公室", "马厩", "金矿坑道", "荒野营地", 
            "火车站台", "银行金库", "强盗窝点", "荒废的教堂", "铁匠铺"
        ],
        "descriptions": ["风滚草从脚边滚过。", "空气中弥漫着火药和威士忌的味道。", "钢琴自动弹奏着走调的曲子。", "通缉令贴满了墙壁。", "苍蝇在腐烂的食物上嗡嗡作响。"],
        "containers": ["沉重的保险柜", "强盗的钱袋", "弹药箱", "威士忌木桶"],
        "keys": ["警长徽章", "金库钥匙", "马刺"],
        "codes": ["藏宝图碎片", "通缉令背面的数字", "扑克牌上的暗号"],
        "final_gate": "末班火车",
    }
}


def generate_world_config(min_num, max_num):
    assert min_num >= 4, "至少需要4个房间：起点 + 钥匙 + 箱子 + 出口"
    assert max_num <= 10, "目前至多支持10个房间的生成"

    possible_dirs = ["北", "南", "东", "西", "上", "下"]
    reverse_dirs = {"北": "南", 
                    "南": "北", 
                    "东": "西", 
                    "西": "东", 
                    "上": "下", 
                    "下": "上"}
    theme_key = random.choice(list(ASSET_DB.keys()))
    assets = ASSET_DB[theme_key]

    # 1. 随机决定房间数量
    num_rooms = random.randint(min_num, max_num)
    room_names = random.sample(assets["rooms"], num_rooms)
    
    # 2. 构建地图结构 (随机树)
    rooms_data = {}
    for i in range(num_rooms):
        prefix = "你醒来的地方。" if i == 0 else ""
        rooms_data[i] = {
            "id": i,
            "name": room_names[i],
            "desc": prefix + random.choice(assets['descriptions']),
            "exits": {},         # {已连接房间：方向}
            "items": [],         # 可拿物品
            "interactables": []  # 可互动物品（出口/箱子）
        }

    # 3. 随机连接房间
    connected = [0]
    unconnected = list(range(1, num_rooms))
    
    while unconnected:
        src = random.choice(connected)
        target = random.choice(unconnected)
        available_dirs = [d for d in possible_dirs if d not in rooms_data[src]["exits"].values()]
        if not available_dirs: 
            continue
        direction = random.choice(available_dirs)
        rooms_data[src]["exits"][target] = direction
        rooms_data[target]["exits"][src] = reverse_dirs[direction]
        connected.append(target)
        unconnected.remove(target)

    # 4.逻辑链
    # 4.1  三个不同的房间放置 钥匙、箱子、出口
    available_ids = list(range(1, num_rooms))
    room_key_id, room_container_id, room_exit_id = random.sample(available_ids, 3)

    # 4.2 为钥匙、箱子、线索、出口命名
    key_name = random.choice(assets["keys"])
    container_name = random.choice(assets["containers"])
    clue_name = random.choice(assets["codes"])
    final_gate_name = assets["final_gate"]

    # 4.3  生成最终密码
    final_code = str(random.randint(1000, 9999))
    
    # 4.4  设置终点 - 需要密码
    rooms_data[room_exit_id]["interactables"].append({
        "name": final_gate_name,
        "type": "exit",
        "locked": True,
        "mechanism": "code", 
        "code": final_code,
        "desc": f"这是唯一的出口: {final_gate_name}。旁边有一个数字键盘。"
    })
    
    # 4.5  密码线索
    clue_item = {
        "name": clue_name,
        "type": "clue",
        "content": f"上面潦草地写着一组数字: {final_code}",
        "desc": "这似乎是通往出口的关键线索。"
    }

    # 4.6  箱子 - 需要钥匙
    container_obj = {
        "name": container_name,
        "type": "container",
        "locked": True,
        "mechanism": "key",
        "key_needed": key_name,
        "contents": [clue_item],
        "desc": f"一个锁着的{container_name}，锁孔形状很奇特。"
    }

    # 4.7  放置钥匙
    rooms_data[room_key_id]["items"].append({
        "name": key_name, 
        "type": "key", 
        "desc": f"一把{key_name}。"
    })
    
    # 4.8  放置箱子
    rooms_data[room_container_id]["interactables"].append(container_obj)

    # 4.9  添加干扰项
    for rid in rooms_data:
        for junk in random.sample(junk_names, random.randint(0, len(junk_names))):
            rooms_data[rid]["items"].append({
                "name": junk,
                "type": "junk",
                "desc": "没什么用的垃圾。"
            })

    return {
        "theme": theme_key,
        "rooms": rooms_data}

def get_simple_path(start, end, custom_graph):
    """
        custom_graph: {"room1": {"exits": {"room2": "direction2", 
                                            ...}}, 
                        ...}
    """
    queue = collections.deque([(start, [start])])
    visited = {start}
    
    while queue:
        curr, path = queue.popleft()
        if curr == end: 
            return path
        
        neighbors = custom_graph[curr]['exits']

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []


def get_dfs_trace_ending_at(start, end, custom_graph, stop_after_end=False):
    """生成一个遍历路径。
        param stop_after_end: 如果为 True，一旦到达 end，不再探索 end 连接的其他分支，直接结束。
    """
    path_to_end = set(get_simple_path(start, end, custom_graph))
    trace = []
    
    def dfs(current, parent):
        trace.append(current)
        
        # 到达目标后是否停止
        if stop_after_end and current == end:
            return

        neighbors = [n for n in custom_graph[current]['exits'] if n != parent]
        
        next_on_path = None
        others = []
        for n in neighbors:
            if n in path_to_end and n not in trace: 
                next_on_path = n
            elif n in path_to_end:
                if n != parent: 
                    others.append(n)
            else:
                others.append(n)
        
        # 1. 先探索无关分支 (Bad Luck)
        for n in others:
            dfs(n, current)
            trace.append(current) # 回溯
        
        # 2. 最后走向目标 (Correct Path)
        if next_on_path is not None:
            dfs(next_on_path, current)
    
    dfs(start, None)
    return trace


class RandomPuzzleGame:
    def __init__(self, config: Dict):    
        self.theme = config["theme"]
        self.rooms = copy.deepcopy(config["rooms"])

        self.current_room_id = 0
        self.inventory = []    # 背包
        self.finished = False

    def look(self):
        r = self.rooms[self.current_room_id]

        info = f"【{r['name']}】\n{r['desc']}\n"

        exits_str = ", ".join([f"{d} -> {self.rooms[rid]['name']}" for rid, d in r['exits'].items()])
        info += f"[出口]: {exits_str}\n"

        items = [i['name'] for i in r['items']]
        if items: 
            info += f"[地上物品]: {', '.join(items)}\n"

        objs = [f"{i['name']}" for i in r['interactables']]
        if objs: 
            info += f"[设施]: {', '.join(objs)}\n"
        return info

    def move(self, direction):
        r = self.rooms[self.current_room_id]
        target_id = None
        for rid, d in r['exits'].items():
            if direction == d:
                target_id = rid
                break
        if target_id is not None:
            self.current_room_id = target_id
            return f"你向{direction}走去，进入了 {self.rooms[target_id]['name']}。"
        return "那边没有路。"

    def take(self, item_name):
        r = self.rooms[self.current_room_id]
        for i in r['items']:
            if item_name in i['name']:
                r['items'].remove(i)
                self.inventory.append(i)
                return f"你捡起了 {i['name']}。"
        return "这里没有这个东西。"

    def inspect(self, item_name):
        # 背包物品
        for i in self.inventory:
            if item_name in i['name']:
                content = i.get('content', i.get('desc', '没什么特别的。'))
                return f"你仔细观察 {item_name}: {content}"
        r = self.rooms[self.current_room_id]
        # 房间物品
        for i in r['interactables']:
            if item_name in i['name']:
                return f"{i['name']}: {i['desc']}"
        # # 地上物品（look已经看过了）
        # for i in r['items']:
        #     if i['name'] == item_name:
        #         content = i.get('content', i.get('desc', '没什么特别的。'))
        #         return f"你仔细观察 {i['name']}: {content}"
        return "你找不到这个东西。"

    def use(self, item_name, target_name):
        r = self.rooms[self.current_room_id]
        item = next((i for i in self.inventory if item_name in i['name']), None)
        target = next((t for t in r['interactables'] if target_name in t['name']), None)
        
        if not item or not target: 
            return "无效的操作。"
        
        if target['type'] == 'container' and target.get('mechanism') == 'key':
            if target.get('key_needed') == item['name']:
                if not target['locked']: 
                    return "它已经打开了。"
                target['locked'] = False
                loot = target['contents']
                r['items'].extend(loot)
                target['contents'] = []
                return f"咔嚓一声，{target['name']} 打开了！里面掉出来: {[l['name'] for l in loot]}"
            else:
                return "钥匙插不进去。"
        else:
            return "没有任何反应。"

    def input_code(self, target_name, code):
        r = self.rooms[self.current_room_id]
        target = next((t for t in r['interactables'] if target_name in t['name']), None)
        
        if not target: 
            return "找不到目标。"
        
        if target.get('mechanism') == 'code' and target['type'] == 'exit':
            if str(code).strip() == str(target.get('code')).strip():
                target['locked'] = False
                self.finished = True
                return f"密码正确！气压阀嘶嘶作响，{target['name']} 缓缓打开。你自由了！"
            else:
                return "密码错误，红灯闪烁，访问被拒绝。"
        else:
            return "这里不需要输入密码。"
    
    def get_debug_map(self):
        """生成当前地图的 ASCII 树状图，包含入口标记"""
        room_tags = {rid: [] for rid in self.rooms}
        for rid, room in self.rooms.items():
            # 为 ID 0 的房间添加入口标记
            if rid == 0:
                room_tags[rid].append("🏠入口")
            
            # 检查该房间是否有出口
            exit_obj = next((o for o in room['interactables'] if o['type'] == 'exit'), None)
            if exit_obj:
                code_str = f"(密码:{exit_obj['code']})" if exit_obj.get('mechanism') == 'code' else ""
                room_tags[rid].append(f"🚩出口{code_str}")
            
            for obj in room['interactables']:
                if obj['type'] == 'container':
                    room_tags[rid].append(f"📦箱(需{obj['key_needed']})")
                    break
            
            for item in room['items']:
                if item.get('type') == 'key':
                    room_tags[rid].append(f"🔑{item['name']}")
                    break

        output_lines = []
        visited = set()

        def build_tree(current_id, prefix="", is_last=True, direction_from_parent=""):
            visited.add(current_id)
            room = self.rooms[current_id]
            name = f"[{room['id']}]{room['name']}"
            tags = " ".join([f"[{t}]" for t in room_tags[current_id]])
            connector = "└── " if is_last else "├── "
            if current_id == 0:
                line = f"{name} {tags}"
                prefix_child = ""
            else:
                line = f"{prefix}{connector}({direction_from_parent}) {name} {tags}"
                prefix_child = prefix + ("    " if is_last else "│   ")
            output_lines.append(line)
            children = []
            for target_id, direction in room['exits'].items():
                if target_id not in visited:
                    children.append((target_id, direction))
            for i, (child_id, direction) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                build_tree(child_id, prefix_child, is_last_child, direction)

        build_tree(0)
        return "\n".join(output_lines)

    def action(self, func, args):
        try:
            if func == "move":
                feedback = self.move(args.get("direction"))
            elif func == "look":
                feedback = self.look()
            elif func == "take":
                feedback = self.take(args.get("item_name"))
            elif func == "inspect":
                feedback = self.inspect(args.get("item_name"))                    
            elif func == "use":
                feedback = self.use(args.get("item_name"), args.get("target_name"))
            elif func == "input_code":
                feedback = self.input_code(args.get("target_name"), args.get("code"))
            else:
                feedback = f"未知动作: {func}"
        except Exception as e:
            feedback = f"执行异常: {str(e)}"
        return feedback


class PuzzleValidator:
    def __init__(self, game_instance):
        self.game = None
        self.initial_state = game_instance
        self._reset_game_simulation()
        
        self.locations = self._identify_chain_locations()
        
        # 自动捡起
        self.critical_whitelist = {
            self.locations['key_name'],
            self.locations['container_name'],
            self.locations['clue_name'],
            self.locations['gate_name']
        }
    
    def _reset_game_simulation(self):
        """将游戏重置为初始状态，以便进行模拟"""
        self.game = copy.deepcopy(self.initial_state)

    def _identify_chain_locations(self):
        locs = {
            "start": 0,
            "key_room": None,
            "container_room": None,
            "exit_room": None,
            "key_name": "未知钥匙",
            "container_name": "未知箱子",
            "clue_name": "未知线索",
            "gate_name": "未知大门",
            "final_code": "????"
        }
        
        for rid, room in self.game.rooms.items():
            for obj in room['interactables']:
                if obj['type'] == 'container':
                    locs["container_room"] = rid
                    locs["container_name"] = obj['name']
                    locs["key_name"] = obj['key_needed']
                    locs["clue_name"] = obj['contents'][0]['name']
                    content_str = obj['contents'][0].get('content', '')
                    nums = re.findall(r'\d+', content_str)
                    locs["final_code"] = nums[-1] if nums else "0000"
                elif obj['type'] == 'exit':
                    locs["exit_room"] = rid
                    locs["gate_name"] = obj['name']

        if locs["key_name"]:
            for rid, room in self.game.rooms.items():
                for item in room['items']:
                    if item['name'] == locs["key_name"]:
                        locs["key_room"] = rid
                        break
        return locs

    def _get_adaptive_path(self, start, end, visited_memory):
        """
            逻辑最严密的路径生成：
            visited_memory: defaultdict(set) 结构
        """
        # --- 阶段一：尝试完全基于记忆导航 ---
        # 只有当终点在记忆中，且通过已知边能连通时，才走记忆路径
        if end in visited_memory:
            return get_simple_path(start, end, visited_memory)

      # --- 阶段二：非酋探索模式 ---
        path = []
        
        # 上帝视角：获取全图从当前点到终点的真实最短路径
        # 用途：在每个路口判断哪个是"正确方向"，哪个是"非酋该走的弯路"
        full_correct_path = get_simple_path(start, end, self.game.rooms)
        
        def dfs_bad_luck(current_node, parent_node):
            path.append(current_node)
            
            # 3. 一旦遇到终点，哪怕后面还有未知节点，也直接停下来
            if current_node == end:
                return True 
            
            # 获取真实地图的邻居
            neighbors = list(self.game.rooms[current_node]['exits'].keys())
            valid_neighbors = [n for n in neighbors if n != parent_node]
            
            correct_branch = None
            distraction_branches = []
            
            # 确定下一步的"正确方向"
            # 如果当前节点在通往终点的最短路径上，取出路径上的下一个节点
            if current_node in full_correct_path:
                try:
                    curr_idx = full_correct_path.index(current_node)
                    # 确保不是路径的最后一个点
                    if curr_idx + 1 < len(full_correct_path):
                        correct_branch = full_correct_path[curr_idx + 1]
                except ValueError:
                    pass

            # 分类邻居：干扰项 vs 正确项
            for neighbor in valid_neighbors:
                if neighbor == correct_branch:
                    continue
                
                # 1. 检查记忆：只添加包含"未知节点"的分支
                # 如果分支内的所有节点都在 visited_memory 中，说明是已知的死胡同，跳过
                if self._has_unknown_in_branch(current_node, neighbor, visited_memory):
                    distraction_branches.append(neighbor)
            
            # 2. 非酋行为：先把所有未知的干扰分支走一遍
            for bad_node in distraction_branches:
                if dfs_bad_luck(bad_node, current_node):
                    return True # 如果在干扰分支里意外撞到了终点（虽然逻辑上不太可能，除非终点不在最短路上），立即停止
                path.append(current_node) # 探索完该分支后回溯
                
            # 最后才走正确的路（前提是正确的路也是未知的，或者通往终点）
            if correct_branch is not None:
                if dfs_bad_luck(correct_branch, current_node):
                    return True
                # 如果正确路径走不通（理论上不会发生），也需要回溯
                path.append(current_node)
                
            return False

        dfs_bad_luck(start, None)
        return path
    
    def _update_memory(self, memory, path):
        """
            辅助函数：根据行走的路径更新记忆拓扑图。
        """
        for node in path:
            if node not in memory:
                memory[node] = {"exits": {}}

        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            
            # 获取真实地图中的方向信息
            if v in self.game.rooms[u]['exits']:
                dir_u_to_v = self.game.rooms[u]['exits'][v]
                memory[u]["exits"][v] = dir_u_to_v
                
                # 同时记录反向路径（因为是双向联通的）
                dir_v_to_u = self.game.rooms[v]['exits'][u]
                memory[v]["exits"][u] = dir_v_to_u
    
    def _has_unknown_in_branch(self, root, branch_start, visited_memory):
        """
            检查分支是否有未知点。
            visited_memory 现在是 dict，我们用 (node in visited_memory) 来判断是否去过该房间。
        """
        # 获取上帝视角的真实连接情况进行预判
        stack = [branch_start]
        seen = {root, branch_start}
        
        while stack:
            node = stack.pop()
            
            # 如果这个节点不在记忆的 Key 中，说明完全没去过，这是一个未知分支
            if node not in visited_memory:
                return True 
            
            # 获取真实地图的邻居
            real_neighbors = self.game.rooms[node]['exits'].keys()
            for neighbor in real_neighbors:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        return False

    def _generate_formatted_log(self, path_segments):
        """
            auto_explore: 如果为 True，则开启地毯式搜刮模式
        """
        # 智能逻辑
        actions_at_key = [{"type": "take", "target": self.locations['key_name']}]
        actions_at_container = [
            {"type": "use", "item": self.locations['key_name'], "target": self.locations['container_name']},
            {"type": "take", "target": self.locations['clue_name']},
            {"type": "inspect", "target": self.locations['clue_name']} 
        ]
        actions_at_exit = [
            {"type": "input_code", "target": self.locations['gate_name'], "code": self.locations['final_code']}
        ]
        segment_actions = [actions_at_key, actions_at_container, actions_at_exit]

        num = 3
        assert len(path_segments) == num, "必须是3次移动：钥匙+箱子+出口"

        def merge_to_line(output):
            return output.replace(chr(10), ' ').strip()

        # 初始化
        self._reset_game_simulation()
        sequence = []
        seen_rooms = set()        # 记录已进过的房间，防止重复 look
        
        # 1. 初始状态：查看起点
        start_id = self.game.current_room_id
        seen_rooms.add(start_id)
        sequence.append(f"{self.game.rooms[start_id]['name']}, look(), {merge_to_line(self.game.look())}")

        for i in range(num):
            for next_id in path_segments[i][1:]:
                # 2. 移动
                curr_id = self.game.current_room_id
                direction = self.game.rooms[curr_id]['exits'].get(next_id)
                sequence.append(f"{self.game.rooms[curr_id]['name']}, move('{direction}'), {merge_to_line(self.game.move(direction))}")
                
                # 3. 进入新房间 Look
                if next_id not in seen_rooms:
                    seen_rooms.add(next_id)
                    sequence.append(f"{self.game.rooms[next_id]['name']}, look(), {merge_to_line(self.game.look())}")

            # 4. 显式交互            
            for act in segment_actions[i]:
                curr_room_name = self.game.rooms[self.game.current_room_id]['name']
                act_type = act['type']
                
                if act_type == 'take':                    
                    sequence.append(f"{curr_room_name}, take('{act['target']}'), {merge_to_line(self.game.take(act['target']))}")
                elif act_type == 'use':
                    sequence.append(f"{curr_room_name}, use('{act['item']}', '{act['target']}'), {merge_to_line(self.game.use(act['item'], act['target']))}") 
                elif act_type == 'inspect':
                    sequence.append(f"{curr_room_name}, inspect('{act['target']}'), {merge_to_line(self.game.inspect(act['target']))}")
                elif act_type == 'input_code':
                    sequence.append(f"{curr_room_name}, input_code('{act['target']}', '{act['code']}'), {merge_to_line(self.game.input_code(act['target'], act['code']))}")
                
        return len(sequence), sequence

    def get_min_path_display(self):
        S = self.locations["start"]
        K = self.locations["key_room"]
        C = self.locations["container_room"]
        E = self.locations["exit_room"]
        
        p1 = get_simple_path(S, K, self.game.rooms)
        p2 = get_simple_path(K, C, self.game.rooms)
        p3 = get_simple_path(C, E, self.game.rooms)
        
        return self._generate_formatted_log([p1, p2, p3])

    def get_max_path_display(self):
        S = self.locations["start"]
        K = self.locations["key_room"]
        C = self.locations["container_room"]
        E = self.locations["exit_room"]
        
        # 初始化记忆库
        visited_memory = {}
        visited_memory[S] = {"exits": {}}
        
        # 1. 寻找钥匙 (S -> K)
        path_explore = get_dfs_trace_ending_at(S, K, self.game.rooms, stop_after_end=True)
        self._update_memory(visited_memory, path_explore) # 更新记忆拓扑
        
        # 2. 去开箱子 (K -> C)
        path_task = self._get_adaptive_path(K, C, visited_memory)
        self._update_memory(visited_memory, path_task)    # 更新记忆拓扑
        
        # 3. 去出口 (C -> E)
        path_escape = self._get_adaptive_path(C, E, visited_memory)
                
        return self._generate_formatted_log([path_explore, path_task, path_escape])


class GameRegistry:
    """基于 Redis 的游戏注册表，支持多进程并发访问"""
    _instance = None

    # 设置超时时间为 30 分钟（由 Redis TTL 自动管理过期）
    TIMEOUT_SECONDS = 30 * 60

    # Redis key 前缀与后缀
    KEY_PREFIX = "puzzle_game:"
    STATE_SUFFIX = ":state"
    STEPS_SUFFIX = ":steps"
    LOCK_SUFFIX = ":lock"

    def __init__(self):
        self.r = redis.Redis(host=os.environ.get('REDIS_HOST'), port=6379, db=2, password='bc')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _state_key(self, lbl: str) -> str:
        return f"{self.KEY_PREFIX}{lbl}{self.STATE_SUFFIX}"

    def _steps_key(self, lbl: str) -> str:
        return f"{self.KEY_PREFIX}{lbl}{self.STEPS_SUFFIX}"

    def _lock_key(self, lbl: str) -> str:
        return f"{self.KEY_PREFIX}{lbl}{self.LOCK_SUFFIX}"

    def step_and_act(self, lbl: str, action: str, args: dict):
        """原子地执行：步数+1，然后执行游戏动作（通过 Redis 分布式锁保证原子性）"""
        lock = self.r.lock(self._lock_key(lbl), timeout=10)
        if not lock.acquire(blocking=True, blocking_timeout=5):
            return "操作超时，请重试"
        try:
            data = self.r.get(self._state_key(lbl))
            if data is None:
                return None

            game = pickle.loads(data)
            feedback = game.action(action, args)

            # 将修改后的游戏状态写回 Redis，并刷新 TTL
            pipe = self.r.pipeline()
            pipe.set(self._state_key(lbl), pickle.dumps(game), ex=self.TIMEOUT_SECONDS)
            pipe.incr(self._steps_key(lbl))
            pipe.expire(self._steps_key(lbl), self.TIMEOUT_SECONDS)
            pipe.execute()

            return feedback
        finally:
            try:
                lock.release()
            except Exception:
                pass

    def register(self, env: RandomPuzzleGame, lbl: str):
        pipe = self.r.pipeline()
        pipe.set(self._state_key(lbl), pickle.dumps(env), ex=self.TIMEOUT_SECONDS)
        pipe.set(self._steps_key(lbl), 0, ex=self.TIMEOUT_SECONDS)
        pipe.execute()

    def get(self, lbl: str) -> Optional[RandomPuzzleGame]:
        data = self.r.get(self._state_key(lbl))
        if data is None:
            return None
        return pickle.loads(data)

    def exists(self, lbl: str) -> bool:
        return self.r.exists(self._state_key(lbl)) > 0

    def remove(self, lbl: str):
        self.r.delete(self._state_key(lbl), self._steps_key(lbl))

    def list_all(self) -> List[str]:
        pattern = f"{self.KEY_PREFIX}*{self.STATE_SUFFIX}"
        keys = self.r.keys(pattern)
        prefix_len = len(self.KEY_PREFIX)
        suffix_len = len(self.STATE_SUFFIX)
        labels = []
        for k in keys:
            k_str = k.decode('utf-8') if isinstance(k, bytes) else k
            lbl = k_str[prefix_len:-suffix_len]
            labels.append(lbl)
        return labels

    def move(self, lbl: str):
        if self.r.exists(self._steps_key(lbl)):
            self.r.incr(self._steps_key(lbl))

    def move_count(self, lbl: str) -> int:
        val = self.r.get(self._steps_key(lbl))
        if val is None:
            return -1
        return int(val)


registry = GameRegistry.get_instance()


def create_game(min_num, max_num):
    os.makedirs(f"{PATH}/libraries", exist_ok=True)

    game_config = generate_world_config(min_num=min_num, max_num=max_num)
    game = RandomPuzzleGame(game_config)
    
    # 破解
    validator = PuzzleValidator(copy.deepcopy(game))
    min_steps, min_strs = validator.get_min_path_display()
    max_steps, max_strs = validator.get_max_path_display()
    min_str = '\n'.join(min_strs)
    max_str = '\n'.join(max_strs)
    solution = f"""
【最短路径】 {min_steps} 步
{min_str}
【最长路径】 {max_steps} 步
{max_str}
"""

    # 去重
    game_id = str(uuid.uuid4())
    while os.path.exists(f"{PATH}/libraries/{game_id}.json"):
        game_id = str(uuid.uuid4())

    with open(f"{PATH}/libraries/{game_id}.json", 'w', encoding='utf-8') as f:
        json.dump(
            {
                "game_config": game_config,
                "map": game.get_debug_map(),
                "solution": solution}, 
            f, 
            ensure_ascii=False, 
            indent=2)

    return {
        "game_id": game_id,
        "theme": game_config["theme"],
        "max_steps": max_steps
    }


@app.route('/create_session', methods=['POST'])
def create_session():
    data = request.get_json()
    game_id = data.get('game_id')

    filepath = f"{PATH}/libraries/{game_id}.json"

    if not os.path.exists(filepath):
        return jsonify({
                "success": False, 
                "info": f"库中未记录 game_id={game_id} 的游戏设置，请检查是否输入有误"})
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)

    # JSON 加载后的键是字符串，强制转换回整数
    raw_rooms = content["game_config"]["rooms"]
    fixed_rooms = {int(k): v for k, v in raw_rooms.items()}
    
    # 还需要递归修复 exits 里面的键，因为它们也被存成了字符串
    for r_id, r_data in fixed_rooms.items():
        if "exits" in r_data:
            r_data["exits"] = {int(target_id): direction for target_id, direction in r_data["exits"].items()}
            
    content["game_config"]["rooms"] = fixed_rooms

    number = random.randint(0, 999999)
    pin = str(number).zfill(6)
   
    game = RandomPuzzleGame(content["game_config"])
    registry.register(game, f"{game_id}-{pin}")

    return jsonify({
            "success": True,
            "info": f"游戏(game_id={game_id})初始化成功，通行证 pin={pin}"})


@app.route('/apply_action', methods=['POST'])
def apply_action():
    data = request.get_json()
    game_id, pin, action, args = data.get('game_id'), data.get('pin'), data.get('action'), data.get('args')
    lbl = f"{game_id}-{pin}"
    
    feedback = registry.step_and_act(lbl, action, args)
    if feedback is None:
        return jsonify({"feedback": "game_id或pin输入有误，或游戏已过期"})
    return jsonify({"feedback": feedback})


@app.route('/get_result', methods=['POST'])
def get_result():
    data = request.get_json()
    game_id, pin = data.get('game_id'), data.get('pin')
    lbl = f"{game_id}-{pin}"
    game = registry.get(lbl)
    if game is not None:
        return jsonify({
                "success": game.finished,
                "turns": registry.move_count(lbl)
                })
    else:
        return jsonify({
                "success": False,
                "turns": -1
                })


@app.route('/remove_game', methods=['POST'])
def remove_game():
    data = request.get_json()
    game_id, pin = data.get('game_id'), data.get('pin')
    lbl = f"{game_id}-{pin}"
    if registry.exists(lbl):
        registry.remove(lbl)
        return jsonify({"removed": True})
    return jsonify({"removed": False})


from internbootcamp.utils.tool_server.utils import find_available_port
from gunicorn.app.base import BaseApplication
import multiprocessing


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    # 获取 port
    port = find_available_port("0.0.0.0", 49152)

    # 获取 ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # 保存 ip
    with open("ip.py", "w", encoding="utf-8") as f:
        f.write(f'ips = ["http://{ip}:{port}"]\n')

    # app.run(debug=False, host="0.0.0.0", port=port)
    options = {
        "bind": f"0.0.0.0:{port}",
        "workers": multiprocessing.cpu_count() * 2 + 1,
        "threads": 32,               # 每个 worker 内的线程数
        "worker_class": "gthread",  # 多线程模式需要指定
    }
    StandaloneApplication(app, options).run()