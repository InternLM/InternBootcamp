"""
FEniCS Bootcamp API Server - 热传导仿真服务器 (方案C: 进程隔离版)
每次仿真在独立 spawn 子进程中运行，进程退出后 OS 自动回收全部内存。
Flask/Gunicorn 层不 import 任何 FEniCS 模块，因此可以安全使用多 worker。
"""
import os
import sys
import json
import socket
import traceback
import threading
import multiprocessing
from typing import Dict, Any, Tuple

import numpy as np
from flask import Flask, jsonify, request

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

PATH = current_dir

# ============================================================
# 注意：这里故意不 import FEniCS / MPI / PETSc
# 所有 FEniCS 相关代码只在 spawn 的子进程内部 import
# ============================================================

# spawn 上下文（不能用 fork，否则 MPI 状态会被复制）
_mp_ctx = multiprocessing.get_context("spawn")

# 每个 gunicorn worker 内部的并发控制
# 限制同时运行的仿真子进程数量，防止 OOM
_MAX_CONCURRENT_PER_WORKER = int(os.environ.get("MAX_CONCURRENT_PER_WORKER", "2"))
_worker_semaphore = threading.Semaphore(_MAX_CONCURRENT_PER_WORKER)

# 仿真超时时间（秒）
SIMULATION_TIMEOUT = int(os.environ.get("SIMULATION_TIMEOUT", "120"))


# ============================================================
# 仿真 Worker 函数（在独立子进程中执行）
# ============================================================
def _simulation_worker(config, flux_left, flux_bottom,
                       monitor_coords_1, monitor_coords_2, result_queue):
    """
    在完全独立的子进程中执行热传导仿真。
    
    关键设计：
    - 所有 FEniCS/MPI/PETSc 的 import 都在函数内部
    - 每次调用都是全新的 MPI_Init → 计算 → MPI_Finalize
    - 进程退出后，OS 回收所有内存（包括 PETSc 内存池、JIT 缓存等）
    """
    import shutil

    # ========== 关键修复：隔离 JIT 缓存 ==========
    # 每个子进程使用独立的缓存目录，避免并发写入导致 FFCx 编译缓存损坏
    cache_dir = os.path.join(PATH, "cache", f"dolfinx_cache_{os.getpid()}")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ["XDG_CACHE_HOME"] = cache_dir

    try:
        # ---- 在子进程内部 import FEniCS 全家桶 ----
        import ufl
        from mpi4py import MPI
        from petsc4py import PETSc
        from dolfinx import mesh, fem, default_scalar_type, geometry
        from dolfinx.fem import petsc as fem_petsc

        # ---- 解析参数 ----
        L = config['length']
        W = config['width']
        k_base = default_scalar_type(config['kappa_base'])
        alpha = default_scalar_type(config['alpha'])
        source_amp = config['source_amp']
        boundary_temp = 293.0

        # ---- 输入安全检查 ----
        if np.isnan(flux_left) or np.isnan(flux_bottom):
            result_queue.put({
                "success": False,
                "error": "输入的热通量包含 NaN (非数字)。请检查您的计算公式。"
            })
            return
        if np.isinf(flux_left) or np.isinf(flux_bottom):
            result_queue.put({
                "success": False,
                "error": "输入的热通量包含 Inf (无穷大)。数值过大导致溢出。"
            })
            return

        # ---- 定义导热系数（非线性） ----
        def kappa(u):
            t_ref = default_scalar_type(boundary_temp)
            denom = default_scalar_type(1.0) + alpha * (u - t_ref)
            denom_safe = ufl.conditional(ufl.lt(denom, 0.1), 0.1, denom)
            return k_base / denom_safe

        comm = MPI.COMM_WORLD
        snes = None
        b = None
        A = None

        try:
            # ========== 1. 创建网格 ==========
            msh = mesh.create_rectangle(
                comm=comm,
                points=((0.0, 0.0), (L, W)),
                n=(30, 30),
                cell_type=mesh.CellType.triangle,
            )
            V = fem.functionspace(msh, ("Lagrange", 1))

            # ========== 2. 边界条件 ==========
            fdim = msh.topology.dim - 1
            tol = 1e-6

            # --- Dirichlet BC（右边界 + 上边界固定温度） ---
            def dirichlet_boundary(x):
                return np.logical_or(x[0] >= L - tol, x[1] >= W - tol)

            dirichlet_facets = mesh.locate_entities_boundary(msh, fdim, dirichlet_boundary)
            bcs = []
            if len(dirichlet_facets) > 0:
                dofs = fem.locate_dofs_topological(V=V, entity_dim=fdim, entities=dirichlet_facets)
                bc = fem.dirichletbc(
                    value=default_scalar_type(boundary_temp), dofs=dofs, V=V
                )
                bcs = [bc]

            # --- Neumann BC（左边界 + 下边界热通量） ---
            def left_boundary(x):
                return x[0] <= tol

            def bottom_boundary(x):
                return x[1] <= tol

            left_facets = mesh.locate_entities_boundary(msh, fdim, left_boundary)
            bottom_facets = mesh.locate_entities_boundary(msh, fdim, bottom_boundary)

            indices, values = [], []
            if len(left_facets) > 0:
                indices.append(left_facets)
                values.append(np.full(len(left_facets), 1, dtype=np.int32))
            if len(bottom_facets) > 0:
                indices.append(bottom_facets)
                values.append(np.full(len(bottom_facets), 2, dtype=np.int32))

            ds = ufl.Measure("ds", domain=msh)
            if len(indices) > 0:
                marked_facets = np.hstack(indices).astype(np.int32)
                marked_values = np.hstack(values).astype(np.int32)
                facet_tags = mesh.meshtags(msh, fdim, marked_facets, marked_values)
                ds = ufl.Measure("ds", domain=msh, subdomain_data=facet_tags)

            # ========== 3. 定义变分形式 ==========
            u = fem.Function(V)
            v = ufl.TestFunction(V)
            x = ufl.SpatialCoordinate(msh)

            source_term = (
                source_amp
                * ufl.sin(2 * np.pi * x[0] / L)
                * ufl.sin(2 * np.pi * x[1] / W)
            )

            F = (
                ufl.inner(kappa(u) * ufl.grad(u), ufl.grad(v)) * ufl.dx
                - source_term * v * ufl.dx
            )
            if len(indices) > 0:
                F -= flux_left * v * ds(1)
                F -= flux_bottom * v * ds(2)

            J = ufl.derivative(F, u)

            # ========== 4. PETSc 组装对象 ==========
            F_form = fem.form(F)
            J_form = fem.form(J)

            b = fem_petsc.create_vector(fem.extract_function_spaces(F_form))
            A = fem_petsc.create_matrix(J_form)

            # ========== 5. SNES 残差与 Jacobian 回调 ==========
            def _F_func(_snes, x_vec, F_vec):
                try:
                    x_vec.copy(u.x.petsc_vec)
                    u.x.scatter_forward()
                    with F_vec.localForm() as f_local:
                        f_local.set(0.0)
                    fem_petsc.assemble_vector(F_vec, F_form)
                    fem_petsc.apply_lifting(
                        F_vec, [J_form], [bcs], x0=[x_vec], alpha=-1.0
                    )
                    F_vec.ghostUpdate(
                        addv=PETSc.InsertMode.ADD,
                        mode=PETSc.ScatterMode.REVERSE,
                    )
                    fem_petsc.set_bc(F_vec, bcs, x_vec, -1.0)
                except Exception as e:
                    print(f"[Subprocess {os.getpid()}] Error in _F_func: {e}", flush=True)
                    traceback.print_exc()

            def _J_func(_snes, x_vec, A_mat, P_mat):
                try:
                    x_vec.copy(u.x.petsc_vec)
                    u.x.scatter_forward()
                    A_mat.zeroEntries()
                    fem_petsc.assemble_matrix(A_mat, J_form, bcs=bcs)
                    A_mat.assemble()
                except Exception as e:
                    print(f"[Subprocess {os.getpid()}] Error in _J_func: {e}", flush=True)
                    traceback.print_exc()

            # ========== 6. 创建并配置 SNES 求解器 ==========
            snes = PETSc.SNES().create(comm)
            snes.setFunction(_F_func, b)
            snes.setJacobian(_J_func, A)
            snes.setType("newtonls")
            snes.setTolerances(rtol=1e-5, atol=1e-9, max_it=50)

            try:
                snes.getLineSearch().setType("bt")
            except (AttributeError, RuntimeError):
                pass

            ksp = snes.getKSP()
            ksp.setType("preonly")
            pc = ksp.getPC()
            pc.setType("lu")
            pc.setFactorSolverType("mumps")

            # ========== 7. 求解 ==========
            snes.solve(None, u.x.petsc_vec)
            u.x.scatter_forward()

            # 检查收敛性
            reason = snes.getConvergedReason()
            if reason <= 0:
                reason_map = {
                    -1: "迭代次数超限 (Max iterations exceeded)",
                    -3: "线性求解器失败 (Linear solve failed)",
                    -4: "非线性求解发散 (Diverged)",
                    -6: "线搜索失败 (Line search failed)",
                }
                reason_str = reason_map.get(reason, "未知错误")
                result_queue.put({
                    "success": False,
                    "error": (
                        f"仿真不收敛 (Reason code {reason}: {reason_str})。"
                        f"可能原因：输入通量过大导致温度剧烈变化，或非线性过强。"
                    ),
                })
                return

            # ========== 8. 提取结果 ==========
            points = np.array(
                [
                    [monitor_coords_1[0], monitor_coords_1[1], 0.0],
                    [monitor_coords_2[0], monitor_coords_2[1], 0.0],
                ],
                dtype=default_scalar_type,
            )

            bb_tree = geometry.bb_tree(msh, msh.topology.dim)
            cell_candidates = geometry.compute_collisions_points(bb_tree, points)
            colliding_cells = geometry.compute_colliding_cells(
                msh, cell_candidates, points
            )

            temps = [None, None]
            for i in range(2):
                if len(colliding_cells.links(i)) > 0:
                    cell = np.array(
                        [colliding_cells.links(i)[0]], dtype=np.int32
                    )
                    temps[i] = u.eval(points[i], cell)[0]

            max_temp = comm.allreduce(np.max(u.x.array), op=MPI.MAX)

            result_queue.put({
                "success": True,
                "temp_monitor1": float(temps[0]) if temps[0] is not None else None,
                "temp_monitor2": float(temps[1]) if temps[1] is not None else None,
                "max_temp": float(max_temp),
            })

        finally:
            # 清理 PETSc 对象（加速释放，进程退出后 OS 也会兜底）
            if snes is not None:
                try:
                    _ksp = snes.getKSP()
                    if _ksp is not None:
                        _pc = _ksp.getPC()
                        if _pc is not None:
                            _pc.destroy()
                        _ksp.destroy()
                except Exception:
                    pass
                snes.destroy()
            if b is not None:
                b.destroy()
            if A is not None:
                A.destroy()

    except Exception as e:
        result_queue.put({
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
        })
    finally:
        # 子进程结束时清理独立的 JIT 缓存目录，减少 /tmp 占用
        shutil.rmtree(cache_dir, ignore_errors=True)


# ============================================================
# 进程隔离调度函数
# ============================================================
def run_simulation_isolated(config, flux_left, flux_bottom, m1, m2,
                            timeout=SIMULATION_TIMEOUT):
    """
    在独立 spawn 子进程中执行仿真，返回结果。
    
    - 子进程独立初始化 MPI/PETSc，与主进程完全隔离
    - 子进程退出后 OS 回收全部内存
    - 支持超时自动 kill
    """
    result_queue = _mp_ctx.Queue()
    p = _mp_ctx.Process(
        target=_simulation_worker,
        args=(config, flux_left, flux_bottom, m1, m2, result_queue),
    )
    p.start()
    p.join(timeout=timeout)

    # 超时处理
    if p.is_alive():
        p.kill()
        p.join(timeout=5)
        raise TimeoutError(f"仿真超时 (>{timeout}秒)，已强制终止子进程")

    # 异常退出处理
    if p.exitcode != 0:
        # 尝试从队列获取错误信息
        try:
            result = result_queue.get_nowait()
            if not result["success"]:
                raise RuntimeError(result["error"])
        except RuntimeError:
            raise
        except Exception:
            pass
        raise RuntimeError(
            f"仿真子进程异常退出 (exit code: {p.exitcode})，"
            f"可能原因：段错误、内存不足或 MPI 异常"
        )

    # 正常退出，获取结果
    try:
        result = result_queue.get_nowait()
    except Exception:
        raise RuntimeError("仿真子进程正常退出但未返回结果")

    if not result["success"]:
        raise RuntimeError(result["error"])

    return result["temp_monitor1"], result["temp_monitor2"], result["max_temp"]


# ============================================================
# Flask 应用
# ============================================================
app = Flask(__name__)


@app.route('/run_thermal_simulation', methods=['POST'])
def run_thermal_simulation():
    """
    执行热传导仿真（进程隔离版）
    
    请求体与返回格式与原版完全一致。
    """
    try:
        data = request.get_json()

        # 1. 参数验证
        required_keys = [
            "length", "width", "kappa_base", "alpha", "source_amp",
            "flux_left", "flux_bottom",
            "monitor1_x", "monitor1_y", "monitor2_x", "monitor2_y",
        ]

        missing_params = [k for k in required_keys if k not in data]
        if missing_params:
            return jsonify({
                "success": False,
                "message": f"缺少参数: {', '.join(missing_params)}",
            }), 400

        # 2. 构建配置
        try:
            config = {
                "length": float(data["length"]),
                "width": float(data["width"]),
                "kappa_base": float(data["kappa_base"]),
                "alpha": float(data["alpha"]),
                "source_amp": float(data["source_amp"]),
            }
            flux_left = float(data["flux_left"])
            flux_bottom = float(data["flux_bottom"])
            m1 = (float(data["monitor1_x"]), float(data["monitor1_y"]))
            m2 = (float(data["monitor2_x"]), float(data["monitor2_y"]))
        except (ValueError, TypeError) as e:
            return jsonify({
                "success": False,
                "message": f"参数类型错误: {str(e)}",
            }), 400

        # 3. 在信号量保护下执行仿真（限制每个 worker 的并发子进程数）
        acquired = _worker_semaphore.acquire(timeout=SIMULATION_TIMEOUT)
        if not acquired:
            return jsonify({
                "success": False,
                "message": "服务器繁忙，仿真排队超时，请稍后重试",
            }), 503

        try:
            t1, t2, max_t = run_simulation_isolated(
                config, flux_left, flux_bottom, m1, m2
            )
        finally:
            _worker_semaphore.release()

        return jsonify({
            "success": True,
            "temp_monitor1": t1,
            "temp_monitor2": t2,
            "max_temp": max_t,
            "message": "仿真成功",
        })

    except TimeoutError as e:
        return jsonify({
            "success": False,
            "message": str(e),
        }), 504

    except Exception as e:
        print(f"[Server] Error in run_thermal_simulation: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"仿真失败: {str(e)}",
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "FEniCS Thermal Simulation Server (Process Isolated)",
        "max_concurrent_per_worker": _MAX_CONCURRENT_PER_WORKER,
        "simulation_timeout": SIMULATION_TIMEOUT,
    })


# ============================================================
# Gunicorn 启动
# ============================================================
from gunicorn.app.base import BaseApplication


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
    from internbootcamp.utils.tool_server.utils import find_available_port

    # 获取可用端口
    port = find_available_port("0.0.0.0", 49152)

    # 获取本机 IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # 保存 IP 供客户端使用
    with open("ip.py", "w", encoding="utf-8") as f:
        f.write(f'ips = ["http://{ip}:{port}"]\n')

    # Gunicorn 配置
    # 现在可以安全地开多 worker：
    #   - Master 进程不 import FEniCS（模块顶层没有 MPI/PETSc）
    #   - 仿真在 spawn 子进程中独立运行，与 worker 进程隔离
    #   - 每个 worker 用信号量限制并发仿真数
    options = {
        "bind": f"0.0.0.0:{port}",
        "workers": multiprocessing.cpu_count() * 2 + 1,
        "threads": 32,                # 每个 worker 2 个线程处理请求
        "worker_class": "gthread",   # 多线程模式
        "max_requests": 200,         # 定期重启 worker（清理 Python 层内存）
        "max_requests_jitter": 50,   # 抖动，避免同时重启
        "preload_app": False,        # 不预加载，每个 worker 独立 import
    }

    StandaloneApplication(app, options).run()
