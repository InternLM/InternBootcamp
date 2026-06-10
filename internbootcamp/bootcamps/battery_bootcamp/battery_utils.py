import pybamm

import numpy as np
from scipy import integrate

from typing import Dict, Any


def execute_pybamm_logic(pos_thickness: float, pos_porosity: float, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    PyBaMM 仿真核心逻辑 (静态方法，无状态)
    """
    try:
        # 1. 加载基础参数
        param = pybamm.ParameterValues(context["chemistry"])

        # 2. 定义固定几何参数 (物理约束)
        fixed_sep_thickness = 25e-6
        fixed_neg_thickness = 100e-6 
        
        # 获取原始参数并计算容量缩放
        original_pos_thickness = param["Positive electrode thickness [m]"]
        original_pos_porosity = param["Positive electrode porosity"]
        original_capacity = param["Nominal cell capacity [A.h]"]
        
        # 物理修正：容量 = 原始容量 * (新厚度/旧厚度) * (新活性物质占比 / 旧活性物质占比)
        ratio_thickness = pos_thickness / original_pos_thickness
        ratio_active_material = (1 - pos_porosity) / (1 - original_pos_porosity)
        new_capacity = original_capacity * ratio_thickness * ratio_active_material

        # 3. 注入所有几何参数
        env_updates = {
            "Nominal cell capacity [A.h]": new_capacity,
            "Ambient temperature [K]": context["ambient_temp"],
            "Initial temperature [K]": context["initial_temp"],
            "Total heat transfer coefficient [W.m-2.K-1]": context["heat_transfer_coeff"],
            "Positive electrode thickness [m]": pos_thickness,
            "Positive electrode porosity": pos_porosity,
            "Separator thickness [m]": fixed_sep_thickness,
            "Negative electrode thickness [m]": fixed_neg_thickness,
        }
        param.update(env_updates)

        # 4. 构建模型与求解
        model = pybamm.lithium_ion.DFN(options={"thermal": "lumped"})
        experiment = pybamm.Experiment([f"Discharge at {context['c_rate']} until 2.5V"])
        
        # 使用更宽松一点的公差以提高成功率，或者保持高精度
        solver = pybamm.IDAKLUSolver(atol=1e-6, rtol=1e-6)
        sim = pybamm.Simulation(model, parameter_values=param, experiment=experiment, solver=solver)
        sol = sim.solve(calc_esoh=False)

        # 5. 结果提取
        discharge_time = sol["Time [s]"].entries[-1]
        max_temp = np.max(sol["Cell temperature [K]"].entries)
        
        voltage = sol["Terminal voltage [V]"].entries
        current = sol["Current [A]"].entries
        time = sol["Time [s]"].entries / 3600  # 转换为小时
        
        # 使用 scipy 计算积分
        discharge_energy_wh = integrate.trapezoid(voltage * current, time)

        # 6. 严谨的质量计算 (用于计算 Wh/kg)
        # 重新获取参数确保一致性
        l_pos = param["Positive electrode thickness [m]"]
        l_neg = param["Negative electrode thickness [m]"]
        l_sep = param["Separator thickness [m]"]
        l_cc_pos = param["Positive current collector thickness [m]"]
        l_cc_neg = param["Negative current collector thickness [m]"]
        
        eps_pos = param["Positive electrode porosity"]
        eps_neg = param["Negative electrode porosity"]
        eps_sep = param["Separator porosity"]

        rho_pos = param["Positive electrode density [kg.m-3]"]
        rho_neg = param["Negative electrode density [kg.m-3]"]
        rho_sep = param["Separator density [kg.m-3]"]
        rho_cc_pos = param["Positive current collector density [kg.m-3]"]
        rho_cc_neg = param["Negative current collector density [kg.m-3]"]
        rho_elyte = 1200

        # 计算各部分质量
        mass_solid_pos = rho_pos * l_pos * (1 - eps_pos)
        mass_solid_neg = rho_neg * l_neg * (1 - eps_neg)
        mass_solid_sep = rho_sep * l_sep * (1 - eps_sep)
        mass_cc = (rho_cc_pos * l_cc_pos) + (rho_cc_neg * l_cc_neg)

        vol_elyte_pos = l_pos * eps_pos
        vol_elyte_neg = l_neg * eps_neg
        vol_elyte_sep = l_sep * eps_sep
        mass_elyte = rho_elyte * (vol_elyte_pos + vol_elyte_neg + vol_elyte_sep)

        total_mass_per_area = mass_solid_pos + mass_solid_neg + mass_solid_sep + mass_cc + mass_elyte
        
        electrode_area = param["Electrode height [m]"] * param["Electrode width [m]"]
        total_mass_kg = total_mass_per_area * electrode_area

        specific_energy = discharge_energy_wh / total_mass_kg

        return {
            "status": "success",
            "discharge_time": float(discharge_time),
            "max_temp": float(max_temp),
            "specific_energy": float(specific_energy),
            "mass_kg": float(total_mass_kg)
        }

    except Exception as e:
        # 捕获求解器错误或其他物理异常
        return {"status": "error", "message": str(e)}