import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


def calculate_metrics(parameters):
    # 提取变量
    A = parameters["营业收入"]
    B = parameters["营业利润"]
    C = parameters["净利润"]
    D = parameters["固定资产折旧、油气资产折耗、生产性生物资产折旧"]
    E = parameters["无形资产摊销"]
    F = parameters["营业成本"]
    H = parameters["经营活动现金净流量"]
    I = parameters["资本支出"]
    J = parameters["短期借款"]
    K = parameters["长期借款"]
    L = parameters["应付债券"]
    M = parameters["租赁负债"]
    N = parameters["一年内到期的非流动负债"]
    O = parameters["应付短期融资款"]
    P = parameters["总资产"]
    Q = parameters["所有者权益"]
    R = parameters["负债与所有者权益合计"]
    S = parameters["流动资产合计"]
    T = parameters["流动负债合计"]
    U = parameters["存货净额"]
    V = parameters["货币资金"]

    result = {}

    # 预计算中间变量
    ebitda = B + D + E
    short_term_debt = J + N + O
    interest_bearing_debt = J + K + L + M
    total_liabilities = R - Q 

    # 计算指标
    result["EBITDA"] = ebitda
    
    if A == 0:
        result["毛利率"] = None
        result["销售净利润率"] = None
        result["EBITDA/营业收入"] = None
        result["经营活动现金净流量/营业收入"] = None
        result["资本支出/收入"] = None
    else:
        result["毛利率"] = (A - F) / A
        result["销售净利润率"] = C / A
        result["EBITDA/营业收入"] = ebitda / A
        result["经营活动现金净流量/营业收入"] = H / A
        result["资本支出/收入"] = I / A

    if H == 0:
        result["资本支出/经营活动现金净流量"] = None
    else:
        result["资本支出/经营活动现金净流量"] = I / H

    result["付息债务"] = interest_bearing_debt
    result["短期债务"] = short_term_debt
    
    if P == 0:
        result["资产负债率"] = None
    else:
        result["资产负债率"] = total_liabilities / P

    if total_liabilities == 0:
        result["短期债务/总债务"] = None
    else:
        result["短期债务/总债务"] = short_term_debt / total_liabilities

    if T == 0:
        result["流动比率"] = None
        result["速动比率"] = None
    else:
        result["流动比率"] = S / T
        result["速动比率"] = (S - U) / T

    if short_term_debt == 0:
        result["现金/短期债务"] = None
        result["(现金 + EBITDA) / 短期债务"] = None
    else:
        result["现金/短期债务"] = V / short_term_debt
        result["(现金 + EBITDA) / 短期债务"] = (V + ebitda) / short_term_debt
    return result


class MetCalTool(BaseTool):
    """一个简单的算术工具，支持基本的加减乘除运算"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        

    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "history": [],
            "operation_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行算术运算"""
        try:
            missed = []
            for para in ["营业收入", "营业利润", "净利润", "固定资产折旧、油气资产折耗、生产性生物资产折旧", "无形资产摊销", "营业成本", "经营活动现金净流量", "资本支出", "短期借款", "长期借款", "应付债券", "租赁负债", "一年内到期的非流动负债", "应付短期融资款", "总资产", "所有者权益", "负债与所有者权益合计", "流动资产合计", "流动负债合计", "存货净额", "货币资金"]:
                if para not in parameters:
                    missed.append(para)
            if len(missed):
                return f"错误: 参数缺失 {missed}", -0.1, {} 

            result = calculate_metrics(parameters)

            metrics = parameters.copy()
            metrics["result"] = result
            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            self._instance_dict[instance_id]["history"].append(metrics)
            
            # 构建响应
            response = json.dumps(result, ensure_ascii=False)
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics["operation_count"] = self._instance_dict[instance_id]["operation_count"]
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"MetCalTool执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}
