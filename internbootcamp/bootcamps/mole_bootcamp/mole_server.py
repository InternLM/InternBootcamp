"""
Mole Bootcamp API Server - 分子能量景观环境管理服务器
通过 Flask API 管理 OpenMM 仿真环境
"""
import os
import sys
import time
import random
from typing import Dict, Optional, List
import json
import uuid

import numpy as np
import openmm.openmm as mm
import openmm.unit as unit
from PIL import Image, ImageDraw

import threading
import redis

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import socket
from flask import Flask, jsonify, request

PATH = current_dir


# ==========================================
# LandscapeEnv2D 类定义（服务器端本地使用）
# ==========================================
class LandscapeEnv2D:
    """
    2D 势能面环境管理器。
    定义域: x, y in [0, 10] nm
    """
    def __init__(self, params: Dict[str, any], plot_dir=None, env_id: str = None):
        self.env_id = env_id if env_id else str(uuid.uuid4())
        self.params = params
        self.history = []

        self.system = mm.System()
        self.system.addParticle(1.0)  # 虚拟质量 1.0 amu

        # --- 构建 2D 复杂势能面公式 ---
        expression = "1000 * (max(0, -x)^2 + max(0, x-10)^2 + max(0, -y)^2 + max(0, y-10)^2)"
        expression += " + B * sin(k * x) * cos(k * y)"

        for i in range(params['n_gaussians']):
            expression += f" + A{i} * exp( -a{i}*(x-mu_x{i})^2 - 2*b{i}*(x-mu_x{i})*(y-mu_y{i}) - c{i}*(y-mu_y{i})^2 )"

        self.force = mm.CustomExternalForce(expression)

        self.force.addGlobalParameter("B", params['noise_amp'])
        self.force.addGlobalParameter("k", params['noise_freq'])

        for i, g in enumerate(params['gaussians']):
            sin_t = np.sin(g['theta'])
            cos_t = np.cos(g['theta'])
            sig_x2 = g['sigma_x'] ** 2
            sig_y2 = g['sigma_y'] ** 2

            a = (cos_t**2 / (2*sig_x2)) + (sin_t**2 / (2*sig_y2))
            b = -(sin_t * cos_t) / (2*sig_x2) + (sin_t * cos_t) / (2*sig_y2)
            c = (sin_t**2 / (2*sig_x2)) + (cos_t**2 / (2*sig_y2))

            self.force.addGlobalParameter(f"A{i}", g['A'])
            self.force.addGlobalParameter(f"mu_x{i}", g['mu_x'])
            self.force.addGlobalParameter(f"mu_y{i}", g['mu_y'])
            self.force.addGlobalParameter(f"a{i}", a)
            self.force.addGlobalParameter(f"b{i}", b)
            self.force.addGlobalParameter(f"c{i}", c)

        self.force.addParticle(0, [])
        self.system.addForce(self.force)

        self.integrator = mm.VerletIntegrator(0.001)
        self.context = mm.Context(self.system, self.integrator)

        # 可视化配置
        self.plot_dir = plot_dir
        if self.plot_dir:
            os.makedirs(self.plot_dir, exist_ok=True)
            self.step_counter = 0

    def _clip_coords(self, x: float, y: float):
        return max(0.01, min(9.99, x)), max(0.01, min(9.99, y))

    def measure_point(self, x: float, y: float):
        """测量指定点的能量和受力"""
        x, y = self._clip_coords(x, y)
        self.context.setPositions([[x, y, 0]])

        state = self.context.getState(getEnergy=True, getForces=True)
        pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
        forces = state.getForces(asNumpy=True)[0]
        fx = forces[0].value_in_unit(unit.kilojoules_per_mole/unit.nanometer)
        fy = forces[1].value_in_unit(unit.kilojoules_per_mole/unit.nanometer)

        result = {
            "action": "measure",
            "coords": [round(x, 4), round(y, 4)],
            "energy": round(pe, 2),
            "force_vector": [round(fx, 2), round(fy, 2)]
        }
        self.history.append(result)

        return result

    def run_local_minimization(self, start_x: float, start_y: float):
        """从指定点开始进行局部能量最小化"""
        start_x, start_y = self._clip_coords(start_x, start_y)
        self.context.setPositions([[start_x, start_y, 0]])

        try:
            mm.LocalEnergyMinimizer.minimize(self.context, tolerance=0.1, maxIterations=2000)

            state = self.context.getState(getPositions=True, getEnergy=True)
            pos = state.getPositions(asNumpy=True)[0]
            pe = state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)

            final_x = pos[0].value_in_unit(unit.nanometer)
            final_y = pos[1].value_in_unit(unit.nanometer)

            result = {
                "action": "minimize",
                "start": [round(start_x, 4), round(start_y, 4)],
                "final_coords": [round(final_x, 4), round(final_y, 4)],
                "final_energy": round(pe, 2)
            }
            self.history.append(result)

            return result
        except Exception as e:
            return {"error": str(e)}


# ==========================================
# 环境注册表（Redis 版本，支持多进程）
# ==========================================
class EnvRegistry:
    """
    单例模式的环境注册表（服务器端）
    使用 Redis 存储会话元数据，本地缓存 LandscapeEnv2D 实例
    使用 env_id-pin 作为键实现会话隔离
    """
    _instance = None

    # 设置超时时间为 30 分钟
    TIMEOUT_SECONDS = 30 * 60
    REDIS_PREFIX = "mole:session:"
    REDIS_SET_KEY = "mole:active_sessions"

    def __init__(self):
        self._redis_client = None
        self._pid = None
        self._local_envs: Dict[str, LandscapeEnv2D] = {}
        self._local_locks: Dict[str, threading.Lock] = {}

    @property
    def _redis(self):
        """
        惰性获取 Redis 连接，并在检测到 fork（PID 变化）时
        重建连接和清空本地缓存，确保多进程安全
        """
        current_pid = os.getpid()
        if self._redis_client is None or self._pid != current_pid:
            if self._pid is not None and self._pid != current_pid:
                # fork 后的子进程：清空从父进程继承的本地缓存
                self._local_envs = {}
                self._local_locks = {}
            self._redis_client = redis.Redis(
                host=os.environ.get('REDIS_HOST'), port=6379, db=1, password='bc',
                decode_responses=True
            )
            self._pid = current_pid
        return self._redis_client

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _session_key(self, lbl: str) -> str:
        return f"{self.REDIS_PREFIX}{lbl}"

    def _cleanup_expired_envs(self):
        """
        内部方法：检查并删除过期的环境
        """
        current_time = time.time()
        all_lbls = self._redis.smembers(self.REDIS_SET_KEY)
        expired_lbls = []

        # 找出所有过期的 lbl
        for lbl in all_lbls:
            key = self._session_key(lbl)
            timestamp = self._redis.hget(key, "timestamp")
            if timestamp is not None and current_time - float(timestamp) > self.TIMEOUT_SECONDS:
                expired_lbls.append(lbl)

        # 执行删除
        for lbl in expired_lbls:
            self.remove(lbl)
            print(f"[Server] Session {lbl} has expired and was removed.")

    def register(self, env: LandscapeEnv2D, lbl: str):
        """注册环境实例"""
        # 注册前先清理一次，保持内存整洁
        self._cleanup_expired_envs()

        key = self._session_key(lbl)
        self._redis.hset(key, mapping={
            "params": json.dumps(env.params),
            "env_id": env.env_id,
            "steps": 0,
            "timestamp": str(time.time())
        })
        self._redis.sadd(self.REDIS_SET_KEY, lbl)

        # 本地缓存 env 实例和锁
        self._local_envs[lbl] = env
        self._local_locks[lbl] = threading.Lock()

        print(f"[Server] Session {lbl} registered successfully.")

    def get_lock(self, lbl) -> threading.Lock:
        if lbl not in self._local_locks:
            self._local_locks[lbl] = threading.Lock()
        return self._local_locks[lbl]

    def get(self, lbl: str) -> Optional[LandscapeEnv2D]:
        """获取环境实例"""
        # 获取前先清理，防止返回已经过期的环境
        self._cleanup_expired_envs()

        key = self._session_key(lbl)
        if not self._redis.exists(key):
            # Redis 中不存在，清理本地缓存
            self._local_envs.pop(lbl, None)
            self._local_locks.pop(lbl, None)
            return None

        # 检查本地缓存
        if lbl in self._local_envs:
            return self._local_envs[lbl]

        # 本地缓存不存在（可能是其他 worker 进程创建的会话），从 Redis 加载 params 重建
        data = self._redis.hgetall(key)
        if not data or "params" not in data:
            return None

        params = json.loads(data["params"])
        env_id = data.get("env_id", lbl)
        env = LandscapeEnv2D(params, env_id=env_id)

        self._local_envs[lbl] = env
        self._local_locks[lbl] = threading.Lock()

        return env

    def remove(self, lbl: str):
        """移除并销毁环境"""
        key = self._session_key(lbl)
        self._redis.delete(key)
        self._redis.srem(self.REDIS_SET_KEY, lbl)

        # 清理本地缓存
        self._local_envs.pop(lbl, None)
        self._local_locks.pop(lbl, None)

        print(f"[Server] Session {lbl} removed.")

    def list_all(self) -> List[str]:
        """列出所有活跃的环境"""
        self._cleanup_expired_envs()
        return list(self._redis.smembers(self.REDIS_SET_KEY))

    def move(self, lbl: str):
        """记录操作次数"""
        self._cleanup_expired_envs()

        key = self._session_key(lbl)
        if self._redis.exists(key):
            self._redis.hincrby(key, "steps", 1)

    def move_count(self, lbl: str) -> int:
        """获取操作次数"""
        self._cleanup_expired_envs()
        key = self._session_key(lbl)
        steps = self._redis.hget(key, "steps")
        return int(steps) if steps is not None else -1


# 创建 Flask 应用和注册表实例
app = Flask(__name__)
registry = EnvRegistry.get_instance()


@app.route('/create_session', methods=['POST'])
def create_session():
    """
    创建会话并注册环境
    
    请求体:
    {
        "env_id": "unique_env_id"
    }
    
    返回:
    {
        "success": true/false,
        "info": "场景(env_id=xxx)初始化成功，通行证 pin=xxxxxx"
    }
    """
    try:
        data = request.get_json()
        env_id = data.get('env_id')

        if not env_id:
            return jsonify({
                "success": False,
                "info": "缺少 env_id 参数"
            }), 400

        # 从文件系统加载场景配置
        filepath = f"{PATH}/libraries/{env_id}.json"

        if not os.path.exists(filepath):
            return jsonify({
                "success": False, 
                "info": f"库中未记录 env_id={env_id} 的场景设置，请检查是否输入有误"
            })
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # 生成 6 位随机 PIN 码
        number = random.randint(0, 999999)
        pin = str(number).zfill(6)

        # 创建环境实例
        params = content.get('params')
        env = LandscapeEnv2D(params, env_id=env_id)

        # 使用 env_id-pin 组合作为标签注册
        lbl = f"{env_id}-{pin}"
        registry.register(env, lbl)

        return jsonify({
            "success": True,
            "info": f"场景(env_id={env_id})初始化成功，通行证 pin={pin}"
        })
        
    except Exception as e:
        print(f"[Server] Error creating session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "info": f"错误: {str(e)}"
        }), 500


@app.route('/measure_point', methods=['POST'])
def measure_point():
    """
    测量点能量工具接口
    
    请求体:
    {
        "env_id": "unique_env_id",
        "pin": "123456",
        "x": 5.0,
        "y": 3.2
    }
    
    返回:
    {
        "success": true/false,
        "is_collision": false,
        "coord": [5.0, 3.2],
        "energy": -45.23,
        "force_vector": [2.1, -3.4]
    }
    """
    try:
        data = request.get_json()
        env_id = data.get("env_id")
        pin = data.get("pin")
        x = data.get("x")
        y = data.get("y")
        
        if not env_id or not pin:
            return jsonify({
                "success": False,
                "feedback": "缺少 env_id 或 pin 参数"
            }), 400
        
        if x is None or y is None:
            return jsonify({
                "success": False,
                "feedback": "缺少 x 或 y 参数"
            }), 400
        
        # 使用 env_id-pin 组合查找环境
        lbl = f"{env_id}-{pin}"
        env = registry.get(lbl)
        
        if not env:
            return jsonify({
                "success": False,
                "feedback": "env_id 或 pin 输入有误"
            }), 404
        
        # 记录操作次数
        registry.move(lbl)
        
        # 执行测量
        lock = registry.get_lock(lbl)
        with lock:
            result = env.measure_point(float(x), float(y))
        
        return jsonify({
            "success": True,
            "action": result["action"],
            "coord": result["coords"],
            "energy": result["energy"],
            "force_vector": result["force_vector"]
        })
        
    except Exception as e:
        print(f"[Server] Error in measure_point: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "feedback": f"执行异常: {str(e)}"
        }), 500


@app.route('/run_local_minimization', methods=['POST'])
def run_local_minimization():
    """
    局部优化工具接口
    
    请求体:
    {
        "env_id": "unique_env_id",
        "pin": "123456",
        "start_x": 5.0,
        "start_y": 3.2
    }
    
    返回:
    {
        "success": true/false,
        "start": [5.0, 3.2],
        "final_coords": [4.89, 3.15],
        "final_energy": -52.1
    }
    """
    try:
        data = request.get_json()
        env_id = data.get("env_id")
        pin = data.get("pin")
        start_x = data.get("start_x")
        start_y = data.get("start_y")
        
        if not env_id or not pin:
            return jsonify({
                "success": False,
                "feedback": "缺少 env_id 或 pin 参数"
            }), 400
        
        if start_x is None or start_y is None:
            return jsonify({
                "success": False,
                "feedback": "缺少 start_x 或 start_y 参数"
            }), 400
        
        # 使用 env_id-pin 组合查找环境
        lbl = f"{env_id}-{pin}"
        env = registry.get(lbl)
        
        if not env:
            return jsonify({
                "success": False,
                "feedback": "env_id 或 pin 输入有误"
            }), 404
        
        # 记录操作次数
        registry.move(lbl)
        
        # 执行局部优化
        lock = registry.get_lock(lbl)
        with lock:
            result = env.run_local_minimization(float(start_x), float(start_y))
        
        if "error" in result:
            return jsonify({
                "success": False,
                "feedback": f"优化错误: {result['error']}"
            }), 500
        
        return jsonify({
            "success": True,
            "action": result["action"],
            "start": result["start"],
            "final_coords": result["final_coords"],
            "final_energy": result["final_energy"]
        })
        
    except Exception as e:
        print(f"[Server] Error in run_local_minimization: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "feedback": f"执行异常: {str(e)}"
        }), 500


@app.route('/get_energy', methods=['POST'])
def get_energy():
    """
    获取指定坐标的能量（用于 reward_calculator 验证）
    注意：此接口用于验证答案，从文件加载环境配置临时计算
    
    请求体:
    {
        "env_id": "unique_env_id",
        "x": 5.0,
        "y": 3.2
    }
    
    返回:
    {
        "success": true/false,
        "energy": -45.23,
        "message": "..."
    }
    """
    try:
        data = request.get_json()
        env_id = data.get("env_id")
        x = data.get("x")
        y = data.get("y")
        
        if not env_id:
            return jsonify({
                "success": False,
                "message": "Missing env_id parameter"
            }), 400
        
        if x is None or y is None:
            return jsonify({
                "success": False,
                "message": "Missing x or y parameter"
            }), 400
        
        # 从文件加载环境配置
        filepath = f"{PATH}/libraries/{env_id}.json"
        if not os.path.exists(filepath):
            return jsonify({
                "success": False,
                "message": f"Environment config {env_id} not found"
            }), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        params = content.get('params')
        if not params:
            return jsonify({
                "success": False,
                "message": "Invalid environment config"
            }), 400
        
        # 创建临时环境用于计算能量
        temp_env = LandscapeEnv2D(params, env_id=f"temp_{env_id}_verify")
        
        try:
            # 计算能量
            temp_env.context.setPositions([[float(x), float(y), 0]])
            energy = temp_env.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole)
            
            return jsonify({
                "success": True,
                "energy": float(energy),
                "message": "Energy calculated."
            })
        finally:
            # 清理临时环境
            del temp_env
        
    except Exception as e:
        print(f"[Server] Error in get_energy: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route('/remove_session', methods=['POST'])
def remove_session():
    """
    移除会话
    
    请求体:
    {
        "env_id": "unique_env_id",
        "pin": "123456"
    }
    
    返回:
    {
        "removed": true/false
    }
    """
    try:
        data = request.get_json()
        env_id = data.get('env_id')
        pin = data.get('pin')
        
        if not env_id or not pin:
            return jsonify({"removed": False})
        
        lbl = f"{env_id}-{pin}"
        if lbl in registry.list_all():
            registry.remove(lbl)
            return jsonify({"removed": True})
        return jsonify({"removed": False})
            
    except Exception as e:
        print(f"[Server] Error removing session: {str(e)}")
        return jsonify({"removed": False}), 500


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
        "threads": 32,              # 每个 worker 内的线程数
        "worker_class": "gthread",  # 多线程模式需要指定
    }
    StandaloneApplication(app, options).run()
