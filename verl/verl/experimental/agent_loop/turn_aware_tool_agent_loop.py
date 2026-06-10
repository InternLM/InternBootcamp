import copy
from uuid import uuid4
from typing import Any, List
from verl.experimental.agent_loop.agent_loop import register, AgentLoopOutput
from verl.experimental.agent_loop.tool_agent_loop import ToolAgentLoop, AgentState, AgentData

@register("turn_aware_tool_agent")
class TurnAwareToolAgentLoop(ToolAgentLoop):
    """
    支持记录每轮Context以及单步执行模式的AgentLoop
    """
    
    async def run(self, sampling_params: dict[str, Any], **kwargs) -> AgentLoopOutput:
        # 检查是否开启单步模式 (从kwargs传入)
        self.run_single_turn = kwargs.get("run_single_turn", False)
        
        # [修改] 如果是单步模式，且传入了单步最大长度，直接覆盖 self.response_length
        # 这样最后的 output 构造时，就会使用这个较短的长度进行截断
        if self.run_single_turn:
            max_turn_response_length = kwargs.get("max_turn_response_length", None)
            if max_turn_response_length is not None:
                self.response_length = max_turn_response_length
        # 注意到agentloop是为每条数据专门实例化的，因此不怕修改这里
        
        # 用于记录每一轮开始时的 prompt_ids (即 History Context)
        # 格式: List[List[int]]
        self.turn_history_contexts = []
        self.turn_history_messages = []
        # 调用父类的run逻辑，但我们需要拦截状态机来记录Context
        # 由于父类run方法直接写死了状态机循环，我们需要稍微重写run方法或者利用hook
        # 为了稳健，这里复制并修改run的核心逻辑
        
        messages = list(kwargs["raw_prompt"])
        image_data = copy.deepcopy(kwargs.get("multi_modal_data", {}).get("image", None))
        metrics = {}
        request_id = uuid4().hex # 禁止复用
            
        tools_kwargs = kwargs.get("tools_kwargs", {})
        if "tools_kwargs" in kwargs.get("extra_info", {}):
             tools_kwargs = kwargs["extra_info"]["tools_kwargs"]

        # 初始化 AgentData
        agent_data = AgentData(
            messages=messages,
            image_data=[],
            video_data=[],
            metrics=metrics,
            request_id=request_id,
            tools_kwargs=tools_kwargs,
            interaction=None,
            interaction_kwargs={},
        )

        state = AgentState.PENDING
        while state != AgentState.TERMINATED:
            if state == AgentState.PENDING:
                state = await self._handle_pending_state(agent_data, sampling_params)
                # PENDING之后，prompt_ids已经准备好，这是第0轮的Context
                if not self.run_single_turn:
                    self.turn_history_contexts.append(copy.deepcopy(agent_data.prompt_ids))
                    self.turn_history_messages.append(copy.deepcopy(agent_data.messages))
            elif state == AgentState.GENERATING:
                state = await self._handle_generating_state(agent_data, sampling_params)
            
            elif state == AgentState.PROCESSING_TOOLS:
                # 在处理工具之前，如果是在单步模式下，处理完工具就应该结束
                state = await self._handle_processing_tools_state(agent_data)
                
                if self.run_single_turn:
                    # 单步模式：执行完工具，拿到Reward，直接终止
                    state = AgentState.TERMINATED
                else:
                    # 正常模式：记录下一轮的Context (包含了刚才的工具返回)
                    if state == AgentState.GENERATING: # 如果状态机决定继续生成
                        self.turn_history_contexts.append(copy.deepcopy(agent_data.prompt_ids))
                        self.turn_history_messages.append(copy.deepcopy(agent_data.messages))
            elif state == AgentState.INTERACTING:
                state = await self._handle_interacting_state(agent_data)
            else:
                state = AgentState.TERMINATED

        # 构造输出
        response_ids = agent_data.prompt_ids[-len(agent_data.response_mask) :]
        prompt_ids = agent_data.prompt_ids[: len(agent_data.prompt_ids) - len(agent_data.response_mask)]
        
        output = AgentLoopOutput(
            prompt_ids=prompt_ids,
            response_ids=response_ids[: self.response_length],
            response_mask=agent_data.response_mask[: self.response_length],
            multi_modal_data={"image": agent_data.image_data} if agent_data.image_data is not None else {},
            response_logprobs=agent_data.response_logprobs[: self.response_length] if agent_data.response_logprobs else None,
            num_turns=agent_data.user_turns + agent_data.assistant_turns + 1,
            metrics=agent_data.metrics,
            extra_fields={
                "turn_scores": agent_data.turn_scores,
                "tool_rewards": agent_data.tool_rewards,
                # 将历史Context返回，供Trainer切分使用
                "turn_history_contexts": self.turn_history_contexts,
                "turn_history_messages": self.turn_history_messages
            },
        )
        return output