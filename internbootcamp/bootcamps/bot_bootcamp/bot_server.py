import os
import json
import re
import random

import uuid

import numpy as np
import pandas as pd
import pybullet as p
import pybullet_data
from typing import Dict, Any, List, Optional
from openai import OpenAI
from tqdm import tqdm
from PIL import Image, ImageDraw

import threading
import redis

import socket
from flask import Flask, request, jsonify

import time

app = Flask(__name__)

PATH = os.path.dirname(os.path.abspath(__file__))


class SimulationContext:
    """
    管理PyBullet实例。每个Case对应一个独立的Context实例。
    """
    def __init__(self, gui=False, case_id=None):        
        # 连接物理引擎
        self.cid = p.connect(p.GUI if gui else p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.cid)
        p.setGravity(0, 0, -9.8, physicsClientId=self.cid)
        
        # 加载 KUKA iiwa 机械臂
        self.robot_id = p.loadURDF("kuka_iiwa/model.urdf", [0, 0, 0], useFixedBase=True, physicsClientId=self.cid)
        self.end_effector_idx = 6  
        self.num_joints = p.getNumJoints(self.robot_id, physicsClientId=self.cid)  

    #     self.target_pos = None # 存储目标位置以便可视化计算
    #     self.img_counter = 0 
        
    #     # --- 相机参数初始化 ---
    #     self._init_camera()

    #     self.visual_path = f"{PATH}/records/{case_id}"
    #     os.makedirs(self.visual_path, exist_ok=True)

    # def _init_camera(self):
    #     """初始化多个相机视角，用于合成全方位视图"""
    #     camera_configs = [
    #         {'name': 'Iso',  'dist': 2.0, 'yaw': 45, 'pitch': -35, 'pos': [0, 0, 0.4]},
    #         {'name': 'Top',  'dist': 1.8, 'yaw': 0,  'pitch': -90, 'pos': [0, 0, 0.0]},
    #         {'name': 'Side', 'dist': 2.2, 'yaw': 90, 'pitch': -15, 'pos': [0, 0, 0.5]}
    #     ]

    #     self.view_matrices = []
    #     for cam in camera_configs:
    #         vm = p.computeViewMatrixFromYawPitchRoll(
    #             cameraTargetPosition=cam['pos'],
    #             distance=cam['dist'],
    #             yaw=cam['yaw'],
    #             pitch=cam['pitch'],
    #             roll=0,
    #             upAxisIndex=2,
    #             physicsClientId=self.cid
    #         )
    #         self.view_matrices.append(vm)

    #     self.proj_matrix = p.computeProjectionMatrixFOV(
    #         fov=60, aspect=1.0, nearVal=0.1, farVal=100.0, physicsClientId=self.cid
    #     )

    # def capture_frame(self, suffix="step"):
    #     """
    #     捕获多个视角的画面，并新增一个数据面板显示7个参数和距离误差。
    #     """
    #     w, h = 480, 480 
    #     rgb_arrays = []

    #     # 1. 获取三个物理视角的图像
    #     for vm in self.view_matrices:
    #         _, _, rgb, _, _ = p.getCameraImage(
    #             width=w, 
    #             height=h, 
    #             viewMatrix=vm, 
    #             projectionMatrix=self.proj_matrix,
    #             renderer=p.ER_TINY_RENDERER, 
    #             physicsClientId=self.cid
    #         )
            
    #         rgb_array = np.reshape(rgb, (h, w, 4)) 
    #         rgb_array = rgb_array[:, :, :3] 
    #         rgb_arrays.append(rgb_array)

    #     # 2. 生成数据面板 (Info Panel)
    #     info_img = Image.new('RGB', (w, h), (240, 240, 240)) # 浅灰背景
    #     draw = ImageDraw.Draw(info_img)
        
    #     # 尝试获取数据
    #     try:
    #         current_joints = [p.getJointState(self.robot_id, i, physicsClientId=self.cid)[0] for i in range(self.num_joints)]
    #         ef_pos = p.getLinkState(self.robot_id, self.end_effector_idx, physicsClientId=self.cid)[4]
            
    #         # 计算距离
    #         dist_str = "Target N/A"
    #         dist_val = 999.0
    #         if self.target_pos:
    #             dist_val = np.linalg.norm(np.array(ef_pos) - np.array(self.target_pos))
    #             dist_str = f"{dist_val:.4f} m"
            
    #         # 绘制标题
    #         title_color = (0, 150, 0) if dist_val < 0.05 else (200, 0, 0)
    #         draw.text((20, 20), "SIMULATION STATUS", fill=(0,0,0))
    #         draw.text((20, 45), f"Dist Error: {dist_str}", fill=title_color)
            
    #         # 绘制关节数据和进度条
    #         y_start = 90
    #         for i, angle in enumerate(current_joints):
    #             # 归一化角度到 0-1 之间 (范围约 -3 到 3)
    #             norm_val = (angle + 3.0) / 6.0
    #             bar_width = 200
    #             fill_len = int(norm_val * bar_width)
    #             fill_len = max(0, min(bar_width, fill_len)) # 限制范围
                
    #             # 文字
    #             label = f"J{i+1}: {angle:6.3f} rad"
    #             draw.text((20, y_start), label, fill=(0,0,0))
                
    #             # 进度条背景
    #             bar_x = 160
    #             bar_y = y_start + 2
    #             draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + 10], outline=(100,100,100), fill=(255,255,255))
                
    #             # 进度条前景 (中点在中间)
    #             center_x = bar_x + (bar_width // 2)
    #             # 简单画法：从左到右
    #             draw.rectangle([bar_x, bar_y, bar_x + fill_len, bar_y + 10], fill=(50, 100, 200))
                
    #             # 标记 0 位
    #             draw.line([center_x, bar_y-2, center_x, bar_y+12], fill=(0,0,0), width=1)
                
    #             y_start += 40

    #     except Exception as e:
    #         draw.text((20, 100), f"Data Error: {str(e)}", fill=(255,0,0))

    #     # 将PIL Image转回numpy array并加入列表
    #     rgb_arrays.append(np.array(info_img))
        
    #     # 3. 拼接所有图像
    #     border_thickness = 10 
    #     border = np.zeros((h, border_thickness, 3), dtype=np.uint8) # 黑色分割线

    #     images_to_stack = []
    #     num_images = len(rgb_arrays)
    #     for i, img_arr in enumerate(rgb_arrays):
    #         images_to_stack.append(img_arr)
    #         if i < num_images - 1:
    #             images_to_stack.append(border)

    #     combined_array = np.hstack(images_to_stack)

    #     filename = f"{self.img_counter:03d}_{suffix}.png"
    #     filepath = os.path.join(self.visual_path, filename)
        
    #     img = Image.fromarray(combined_array)
    #     img.save(filepath)
    #     self.img_counter += 1

    def clean_obstacles(self):
        num_bodies = p.getNumBodies(physicsClientId=self.cid)
        all_ids = [p.getBodyUniqueId(i, physicsClientId=self.cid) for i in range(num_bodies)]
        for body_id in all_ids:
            if body_id != self.robot_id:
                p.removeBody(body_id, physicsClientId=self.cid)

    def reproduce_scene(self, case_config: Dict[str, Any]):
        """根据传入的配置参数重现场景"""
        self.clean_obstacles()
        
        # --- 保存目标位置以便可视化 ---
        # self.target_pos = case_config.get('target')
        
        if 'obstacles' in case_config:
            for obs in case_config['obstacles']:
                col_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=obs['half_extents'], physicsClientId=self.cid)
                vis_shape = p.createVisualShape(p.GEOM_BOX, halfExtents=obs['half_extents'], rgbaColor=[0.8, 0.2, 0.2, 1], physicsClientId=self.cid)
                p.createMultiBody(baseMass=0, baseCollisionShapeIndex=col_shape, baseVisualShapeIndex=vis_shape, basePosition=obs['pos'], physicsClientId=self.cid)
        
        target_pos = case_config.get('target')
        if target_pos:
             vis_target = p.createVisualShape(p.GEOM_SPHERE, radius=0.05, rgbaColor=[0, 1, 0, 0.6], physicsClientId=self.cid)
             p.createMultiBody(baseMass=0, baseVisualShapeIndex=vis_target, basePosition=target_pos, physicsClientId=self.cid)

        zeros = [0.0] * self.num_joints
        self.reset_joint_states(zeros, capture=False) 
        p.performCollisionDetection(physicsClientId=self.cid)

    def generate_static_case_data(self, init_obs, joint_angles) -> Dict[str, Any]:
        """
        生成不与目标解冲突、且不与初始姿态冲突的场景数据。
        """
        self.clean_obstacles()

        start_angles = [0.0] * self.num_joints  # 定义机器人的起始姿态（通常是全0）

        while True:
            # 1. --- 随机生成一个合法的目标姿态 ---
            gold_angles = [random.uniform(joint_angles[0], joint_angles[1]) for i in range(self.num_joints)]
            self.reset_joint_states(gold_angles, capture=False) 
            p.performCollisionDetection(physicsClientId=self.cid)
            
            # 检查自身碰撞 
            contact_self = p.getContactPoints(bodyA=self.robot_id, bodyB=self.robot_id, physicsClientId=self.cid)
            if len(contact_self) > 0: continue 
            
            # 获取末端位置作为目标点
            link_state = p.getLinkState(self.robot_id, self.end_effector_idx, physicsClientId=self.cid)
            target_pos = list(link_state[4])
            
            # 过滤掉目标位置太低的情况（防止生成在地板下或紧贴地板）
            if target_pos[2] < 0.1: continue 

            # 2. --- 尝试生成障碍物 ---
            valid_obstacles = []
            temp_obs_ids = [] # 记录物理引擎中临时生成的障碍物ID，函数结束前需删除
            
            # 尝试生成 15 个障碍物，能存活几个算几个
            for _ in range(init_obs):
                obs_pos = [random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8), random.uniform(0.1, 0.8)]
                half_extents = [random.uniform(0.05, 0.15) for _ in range(3)]
                
                col_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_extents, physicsClientId=self.cid)
                obs_id = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=col_shape, basePosition=obs_pos, physicsClientId=self.cid)
                
                is_valid = True
                
                # [Check A] 检查与"终点姿态"的碰撞
                # 此时机器人处于 gold_angles
                self.reset_joint_states(gold_angles) 
                p.performCollisionDetection(physicsClientId=self.cid)
                if len(p.getContactPoints(bodyA=self.robot_id, bodyB=obs_id, physicsClientId=self.cid)) > 0:
                    is_valid = False

                # [Check B] 检查与"起点姿态"的碰撞 (关键新增步骤)
                # 如果这一步不检查，生成的障碍物可能会直接把起点的机器人卡住
                if is_valid:
                    self.reset_joint_states(start_angles)
                    p.performCollisionDetection(physicsClientId=self.cid)
                    if len(p.getContactPoints(bodyA=self.robot_id, bodyB=obs_id, physicsClientId=self.cid)) > 0:
                        is_valid = False

                # [Check C] 检查与其他已生成障碍物的碰撞
                if is_valid:
                    for existing_id in temp_obs_ids:
                        if len(p.getContactPoints(bodyA=obs_id, bodyB=existing_id, physicsClientId=self.cid)) > 0:
                            is_valid = False; break

                # [Check D] 检查是否覆盖了目标点 (距离太近)
                if is_valid:
                    dist_to_target = np.linalg.norm(np.array(obs_pos) - np.array(target_pos))
                    max_radius = np.linalg.norm(half_extents)
                    # 留出 5cm 的安全余量
                    if dist_to_target <= (max_radius + 0.05):
                        is_valid = False

                # --- 结算 ---
                if is_valid:
                    valid_obstacles.append({"pos": obs_pos, "half_extents": half_extents})
                    temp_obs_ids.append(obs_id) 
                else:
                    p.removeBody(obs_id, physicsClientId=self.cid) 
            
            # 3. --- 清理现场 ---
            # 因为这只是生成数据，不需要真的把物体留在场景里，reproduce_scene 会根据数据重新画
            for obs_id in temp_obs_ids: 
                p.removeBody(obs_id, physicsClientId=self.cid)
            
            # 至少要有2个障碍物才算合格的复杂场景，否则重试
            if len(valid_obstacles) < 2: continue
            
            # 恢复机器人到初始状态，保持函数无副作用
            self.reset_joint_states(start_angles)

            case_id = str(uuid.uuid4())
            while os.path.exists(f"{PATH}/libraries/{case_id}.json"):
                case_id = str(uuid.uuid4())

            with open(f"{PATH}/libraries/{case_id}.json", 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        "target": target_pos, 
                        "obstacles": valid_obstacles,
                        "gold_angles": gold_angles}, 
                    f, 
                    ensure_ascii=False, 
                    indent=2)

            return {
                "case_id": case_id,
                "target": target_pos, 
                "obstacles": valid_obstacles,
                "gold_angles": gold_angles 
            }

    def reset_joint_states(self, angles, capture=False):
        for i in range(min(len(angles), self.num_joints)):
            p.resetJointState(self.robot_id, i, angles[i], physicsClientId=self.cid)
        
        if capture:
            self.capture_frame(suffix="move")
            
    def perform_collision_check(self):
        p.performCollisionDetection(physicsClientId=self.cid)
        contact_points = p.getContactPoints(bodyA=self.robot_id, physicsClientId=self.cid)
        return len(contact_points) > 0

    def get_current_ef_pos(self):
        link_state = p.getLinkState(self.robot_id, self.end_effector_idx, physicsClientId=self.cid)
        return list(link_state[4])

    def close(self):
        if p.isConnected(self.cid):
            p.disconnect(self.cid)


class SimulationRegistry:
    """
    基于 Redis 的会话注册表，支持多进程部署。
    
    Redis 中以 Hash 存储每个会话的元数据（steps / timestamp / case_id），
    PyBullet 仿真实例（进程本地资源）缓存在 _local_sims 中。
    当某个 worker 进程收到请求但本地无对应仿真实例时，
    会根据 Redis 中记录的 case_id 从 JSON 配置文件重建场景。
    """
    _instance = None

    REDIS_PREFIX = "sim_registry:"
    TIMEOUT_SECONDS = 30 * 60

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._r = redis.Redis(
            host=os.environ.get('REDIS_HOST'), port=6379, db=3, password='bc',
            decode_responses=True
        )
        self._local_sims: Dict[str, SimulationContext] = {}
        self._lock = threading.Lock()

    def _rkey(self, lbl: str) -> str:
        """返回某个会话在 Redis 中的 Hash key"""
        return f"{self.REDIS_PREFIX}{lbl}"

    def _remove_unlocked(self, lbl: str):
        """内部方法：在已持有锁的情况下删除，不再加锁"""
        if lbl in self._local_sims:
            self._local_sims[lbl].close()
            del self._local_sims[lbl]
        self._r.delete(self._rkey(lbl))

    def _cleanup_expired_sims(self):
        """内部方法：必须在已持有锁的上下文中调用"""
        current_time = time.time()
        prefix_len = len(self.REDIS_PREFIX)
        # 扫描 Redis 中所有会话，清理超时的
        for key in self._r.scan_iter(match=f"{self.REDIS_PREFIX}*"):
            lbl = key[prefix_len:]
            ts = self._r.hget(key, "timestamp")
            if ts and current_time - float(ts) > self.TIMEOUT_SECONDS:
                self._remove_unlocked(lbl)
                print(f"Game {lbl} has expired and was removed.")
        # 清理本地残留（可能已被其他进程从 Redis 中删除）
        for lbl in list(self._local_sims.keys()):
            if not self._r.exists(self._rkey(lbl)):
                self._local_sims[lbl].close()
                del self._local_sims[lbl]

    def register(self, env: SimulationContext, lbl: str, case_id: str):
        with self._lock:
            self._cleanup_expired_sims()
            self._local_sims[lbl] = env
            self._r.hset(self._rkey(lbl), mapping={
                "steps": 0,
                "timestamp": time.time(),
                "case_id": case_id,
            })

    def get(self, lbl: str) -> Optional[SimulationContext]:
        with self._lock:
            self._cleanup_expired_sims()
            rkey = self._rkey(lbl)
            if not self._r.exists(rkey):
                return None
            # 如果本进程没有该仿真实例，从配置文件重建
            if lbl not in self._local_sims:
                case_id = self._r.hget(rkey, "case_id")
                if case_id is None:
                    return None
                filepath = f"{PATH}/libraries/{case_id}.json"
                if not os.path.exists(filepath):
                    return None
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                sim_ctx = SimulationContext()
                sim_ctx.reproduce_scene(content)
                self._local_sims[lbl] = sim_ctx
            return self._local_sims.get(lbl)

    def remove(self, lbl: str):
        with self._lock:
            self._remove_unlocked(lbl)  # ← 公共入口也用同一个内部方法

    def list_all(self) -> List[str]:
        with self._lock:
            self._cleanup_expired_sims()
            prefix_len = len(self.REDIS_PREFIX)
            labels = []
            for key in self._r.scan_iter(match=f"{self.REDIS_PREFIX}*"):
                labels.append(key[prefix_len:])
            return labels

    def move(self, lbl: str):
        with self._lock:
            self._cleanup_expired_sims()
            rkey = self._rkey(lbl)
            if self._r.exists(rkey):
                self._r.hincrby(rkey, "steps", 1)

    def move_count(self, lbl: str) -> int:
        with self._lock:
            self._cleanup_expired_sims()
            val = self._r.hget(self._rkey(lbl), "steps")
            if val is None:
                return -1
            return int(val)


registry = SimulationRegistry.get_instance()


@app.route('/create_session', methods=['POST'])
def create_session():
    data = request.get_json()
    case_id = data.get('case_id')

    filepath = f"{PATH}/libraries/{case_id}.json"

    if not os.path.exists(filepath):
        return jsonify({
                "success": False, 
                "info": f"库中未记录 case_id={case_id} 的场景设置，请检查是否输入有误"})
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)

    number = random.randint(0, 999999)
    pin = str(number).zfill(6)

    sim_ctx = SimulationContext()
    sim_ctx.reproduce_scene(content)

    registry.register(sim_ctx, f"{case_id}-{pin}", case_id)

    return jsonify({
            "success": True,
            "info": f"场景(case_id={case_id})初始化成功，通行证 pin={pin}"})


@app.route('/check_collision', methods=['POST'])
def check_collision():
    data = request.get_json()
    case_id, pin, joint_angles = data["case_id"], data["pin"], data["joint_angles"]

    lbl = f"{case_id}-{pin}"
    if lbl in registry.list_all():
        sim = registry.get(lbl)
        registry.move(lbl)

        try:
            sim.reset_joint_states(joint_angles, capture=False)
            is_col = sim.perform_collision_check()
            pos = sim.get_current_ef_pos()
            return jsonify({
                "success": True,
                "is_collision": is_col, 
                "coord": [round(x, 4) for x in pos]})
        except Exception as e:
            feedback = f"执行异常: {str(e)}"
    else:
        feedback = "case_id或pin输入有误"
        
    return jsonify({
        "success": False,
        "feedback": feedback})


@app.route('/remove_game', methods=['POST'])
def remove_game():
    data = request.get_json()
    case_id, pin = data.get('case_id'), data.get('pin')
    lbl = f"{case_id}-{pin}"
    if lbl in registry.list_all():
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
        "workers": multiprocessing.cpu_count() * 2 + 1,  # 已通过 Redis 支持多进程
        "threads": 32,               # 每个 worker 内的线程数
        "worker_class": "gthread",  # 多线程模式需要指定
    }
    StandaloneApplication(app, options).run()