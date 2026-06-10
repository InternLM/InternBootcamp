import re
import math
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.finance_bootcamp.finance_tools import calculate_metrics


class FinanceRewardCalculator(BaseRewardCalculator):
    """示例奖励管理器，用于评估算术运算任务"""
    
    @staticmethod
    def extract_output(output_str: str) -> Optional[Dict[str, Any]]:
        if not output_str:
            return None

        # 模式 1: 匹配 Markdown 代码块 ```json ... ```
        # re.DOTALL 让 . 可以匹配换行符
        code_block_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(code_block_pattern, output_str, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            # 模式 2: 如果没有代码块，尝试寻找第一个 { 和最后一个 } 之间的内容
            # 这种方式比较激进，假设整个字符串中最大的 { ... } 块就是 JSON
            brace_pattern = r"\{.*\}"
            match = re.search(brace_pattern, output_str, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                return None

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
        
    @classmethod
    def _verify_correction(cls, extracted_output, identity: dict, **kwargs) -> float:
        """
        验证用户输出并计算得分
        
        Args:
            extracted_output: 提取的运算信息
            identity (dict): 任务信息，包含期望的运算和结果
            score_max (float): 最高分数
            score_min (float): 最低分数
            
        Returns:
            float: 得分
        """
        try:
            if not extracted_output:
                return 0.0

            gt = {
                "EBITDA": [], "毛利率": [], "销售净利润率": [], "EBITDA/营业收入": [], 
                "经营活动现金净流量/营业收入": [], "资本支出/收入": [], "资本支出/经营活动现金净流量": [], "付息债务": [], 
                "短期债务": [], "资产负债率": [], "短期债务/总债务": [], "流动比率": [], 
                "速动比率": [], "现金/短期债务": [], "(现金 + EBITDA) / 短期债务": []
            }
            
            for year in ["2021", "2022", "2023"]:
                # 构造临时 data dict 用于计算指标
                temp_data = {k: v for k, v in zip(identity["titles"], identity["data"][year])}
                metrics = calculate_metrics(temp_data)
                for k, v in metrics.items():
                    if v is not None:
                        gt[k].append(v)
            
            # 计算预测数据的指标
            metrics = calculate_metrics(extracted_output)

            # 提取计算结果
            val_ebitda = metrics["EBITDA"]
            val_gross_margin = metrics["毛利率"]
            val_net_margin = metrics["销售净利润率"]
            val_ebitda_margin = metrics["EBITDA/营业收入"]
            val_cfo_margin = metrics["经营活动现金净流量/营业收入"]
            val_capex_rev = metrics["资本支出/收入"]
            val_capex_cfo = metrics["资本支出/经营活动现金净流量"]
            val_debt_interest = metrics["付息债务"]
            val_debt_short = metrics["短期债务"]
            val_liab_ratio = metrics["资产负债率"]
            val_short_debt_ratio = metrics["短期债务/总债务"]
            val_current_ratio = metrics["流动比率"]
            val_quick_ratio = metrics["速动比率"]
            val_cash_short = metrics["现金/短期债务"]
            val_cash_ebitda_short = metrics["(现金 + EBITDA) / 短期债务"]

            # 判定逻辑 (1代表满足条件，0代表不满足)
            results = []
            
            # 辅助函数：安全比较
            def safe_compare(val, history, mode="max"):
                clean_hist = [h for h in history if h is not None]
                if not clean_hist:  # 历史缺失的信息，不予判错 
                    return True
                if not val: 
                    return False
                if mode == "max": 
                    return val >= max(clean_hist)
                if mode == "min": 
                    return val <= min(clean_hist)
                return False

            results.append(safe_compare(val_ebitda, gt["EBITDA"], "max"))
            results.append(safe_compare(val_gross_margin, gt["毛利率"], "max"))
            results.append(safe_compare(val_net_margin, gt["销售净利润率"], "max"))
            results.append(safe_compare(val_ebitda_margin, gt["EBITDA/营业收入"], "max"))
            results.append(safe_compare(val_cfo_margin, gt["经营活动现金净流量/营业收入"], "max"))

            results.append(safe_compare(val_capex_rev, gt["资本支出/收入"], "min"))
            results.append(safe_compare(val_capex_cfo, gt["资本支出/经营活动现金净流量"], "min"))
            results.append(safe_compare(val_debt_interest, gt["付息债务"], "min"))
            results.append(safe_compare(val_debt_short, gt["短期债务"], "min"))
            
            # 资产负债率特殊逻辑
            cond = val_liab_ratio >= 0.3
            clean_hist = [h for h in gt["资产负债率"] if (h is not None and h >= 0.3)]
            if clean_hist:
                cond *= val_liab_ratio <= min(clean_hist)
            results.append(cond)

            results.append(safe_compare(val_short_debt_ratio, gt["短期债务/总债务"], "min"))
            
            # 流动比率特殊逻辑
            cond = val_current_ratio <= 2.5
            clean_hist = [h for h in gt["流动比率"] if (h is not None and h <= 2.5)]
            if clean_hist:
                cond *= val_current_ratio >= max(clean_hist)
            results.append(cond)
                
            # 速动比率特殊逻辑
            cond = val_quick_ratio <= 1.5
            clean_hist = [h for h in gt["速动比率"] if (h is not None and h <= 1.5)]
            if clean_hist:
                cond *= val_quick_ratio >= max(clean_hist)
            results.append(cond)

            results.append(safe_compare(val_cash_short, gt["现金/短期债务"], "max"))
            results.append(safe_compare(val_cash_ebitda_short, gt["(现金 + EBITDA) / 短期债务"], "max"))

            # 如果所有条件都满足，返回 1.0，否则返回 0.0
            # if all(results):
            #     return 1.0
            # else:
            #     return 0.0
            
            # 返回满足的比例
            return sum(results) / len(results)
            
        except Exception as e:
            print(f"[DEBUG FinanceRewardManager] 验证时出错: {str(e)}")
            import traceback
            print(f"[DEBUG FinanceRewardManager] 异常堆栈:\n{traceback.format_exc()}")
            return 0.0
