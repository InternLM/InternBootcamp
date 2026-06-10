"""
可视化工具 - 使用 Plotly 创建交互式图表
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any


def create_score_distribution_chart(samples: List[Dict[str, Any]]):
    """创建分数分布图（直方图）"""
    scores = [s.get("score", 0) for s in samples if s.get("success", False) and s.get("score") is not None]
    
    if not scores:
        return None
    
    fig = px.histogram(
        x=scores,
        nbins=20,
        labels={"x": "分数", "y": "样本数"},
        title="分数分布"
    )
    fig.update_layout(
        showlegend=False,
        height=400,
    )
    return fig


def create_token_usage_chart(samples: List[Dict[str, Any]]):
    """创建 Token 使用情况柱状图"""
    data = []
    for s in samples:
        if s.get("success", False):
            data.append({
                "类型": "Prompt Tokens",
                "数量": s.get("prompt_tokens", 0)
            })
            data.append({
                "类型": "Completion Tokens",
                "数量": s.get("completion_tokens", 0)
            })
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    fig = px.bar(
        df,
        x="类型",
        y="数量",
        title="Token 使用统计",
        labels={"数量": "Token 数量"}
    )
    fig.update_layout(height=400)
    return fig


def create_turns_distribution_chart(samples: List[Dict[str, Any]]):
    """创建轮次分布图"""
    assistant_turns = [s.get("assistant_turns", 0) for s in samples if s.get("success", False)]
    tool_calls = [s.get("tool_calls", 0) for s in samples if s.get("success", False)]
    
    if not assistant_turns:
        return None
    
    df = pd.DataFrame({
        "Assistant 轮次": assistant_turns,
        "工具调用次数": tool_calls,
    })
    
    fig = go.Figure()
    fig.add_trace(go.Box(y=df["Assistant 轮次"], name="Assistant 轮次"))
    fig.add_trace(go.Box(y=df["工具调用次数"], name="工具调用次数"))
    
    fig.update_layout(
        title="轮次与工具调用分布",
        yaxis_title="次数",
        height=400,
    )
    return fig


def create_error_type_pie_chart(errors: List[Dict[str, Any]]):
    """创建错误类型饼图"""
    if not errors:
        return None
    
    # 统计错误类型
    error_counts = {}
    for error in errors:
        error_msg = error.get("error", "Unknown")[:50]  # 截取前50个字符
        error_counts[error_msg] = error_counts.get(error_msg, 0) + 1
    
    df = pd.DataFrame({
        "错误类型": list(error_counts.keys()),
        "数量": list(error_counts.values())
    })
    
    fig = px.pie(
        df,
        values="数量",
        names="错误类型",
        title="错误类型分布"
    )
    fig.update_layout(height=400)
    return fig


def create_data_source_comparison_chart(data_sources: List[Dict[str, Any]]):
    """创建数据源对比图"""
    if not data_sources:
        return None
    
    df = pd.DataFrame(data_sources)
    
    fig = go.Figure()
    
    # 添加平均分
    fig.add_trace(go.Bar(
        x=df["data_source"],
        y=df["avg_score"],
        name="平均分",
        yaxis="y1"
    ))
    
    # 添加成功率
    fig.add_trace(go.Scatter(
        x=df["data_source"],
        y=df["success_rate"],
        name="成功率",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="red", width=2)
    ))
    
    fig.update_layout(
        title="数据源对比",
        xaxis=dict(title="数据源"),
        yaxis=dict(title="平均分", side="left"),
        yaxis2=dict(title="成功率", side="right", overlaying="y", range=[0, 1]),
        height=400,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig


def create_score_boxplot(data_sources: List[Dict[str, Any]]):
    """创建分数箱线图"""
    if not data_sources:
        return None
    
    fig = go.Figure()
    
    for ds in data_sources:
        # 为每个数据源创建一个箱线图
        # 注意：这里我们只有统计数据，没有原始分数，所以用统计数据模拟
        fig.add_trace(go.Box(
            y=[ds["min_score"], ds["avg_score"], ds["max_score"]],
            name=ds["data_source"],
            boxmean='sd'
        ))
    
    fig.update_layout(
        title="分数分布（按数据源）",
        yaxis_title="分数",
        height=400,
    )
    
    return fig

