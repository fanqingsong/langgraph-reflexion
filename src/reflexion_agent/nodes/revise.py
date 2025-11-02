"""答案修订节点实现。

本模块定义了 revise 节点的实现，该节点负责基于新信息修订答案。
该模块自包含所有需要的逻辑，不依赖其他链模块。
"""

from langchain_core.messages import BaseMessage

from reflexion_agent.infra import (
    REVISE_INSTRUCTIONS,
    create_actor_prompt_template,
    get_llm_instance,
)
from reflexion_agent.nodes.execute_tools import revise_answer_tool


def _create_revisor_chain():
    """创建答案修订链。
    
    这个链用于基于新信息和批评修订初始答案，包括：
    - 添加重要信息（带引用）
    - 移除多余信息
    - 确保答案不超过 250 字
    - 添加引用部分
    
    Returns:
        Runnable: 配置好的链，可以处理消息并返回修订后的答案
    """
    # 获取 LLM 实例
    llm = get_llm_instance()
    
    # 获取提示模板
    actor_prompt_template = create_actor_prompt_template()
    
    # 创建答案修订链
    # 绑定 revise_answer_tool 工具（使用 @tool 装饰器定义的带执行逻辑的工具函数）
    # 这样 LLM 会调用这个工具，工具会自动执行搜索查询
    revisor = actor_prompt_template.partial(
        first_instruction=REVISE_INSTRUCTIONS
    ) | llm.bind_tools(tools=[revise_answer_tool], tool_choice="ReviseAnswer")
    
    return revisor


# 创建链实例（延迟初始化，避免在导入时创建）
_revisor_chain = None


def _get_revisor_chain():
    """获取 revisor 链实例（单例模式）。
    
    Returns:
        Runnable: revisor 链实例
    """
    global _revisor_chain
    if _revisor_chain is None:
        _revisor_chain = _create_revisor_chain()
    return _revisor_chain


def revise_node(state: dict) -> dict:
    """答案修订节点。
    
    这个节点使用 revisor 链来基于新信息修订初始答案。
    修订后的答案会包含引用和改进后的内容。
    
    Args:
        state: 当前状态字典，包含 messages 键（消息列表）
        
    Returns:
        dict: 包含修订后答案的状态更新
    """
    # 从状态中提取消息列表
    messages = state.get("messages", [])
    
    # 获取 revisor 链
    revisor = _get_revisor_chain()
    
    # revisor 是一个 LangChain Runnable，用于修订答案
    # 它会基于之前的答案、反思和新搜索到的信息生成修订版本
    # 注意：当使用 init_chat_model 时，invoke 返回的是单个 AIMessage 对象
    response = revisor.invoke(messages)
    
    # 确保返回的是消息对象列表
    # response 应该是一个 AIMessage 对象，需要包装在列表中
    from langchain_core.messages import BaseMessage
    
    # 处理返回值：确保是消息对象列表
    # 根据 LangChain 文档，链的 invoke 方法应该返回单个消息对象或消息列表
    if isinstance(response, BaseMessage):
        # 单个消息对象，直接包装在列表中
        messages = [response]
    elif isinstance(response, list):
        # 如果已经是列表，确保所有元素都是消息对象
        messages = [msg for msg in response if isinstance(msg, BaseMessage)]
        # 如果过滤后列表为空，说明列表中的元素不是消息对象，抛出错误
        if not messages and response:
            raise ValueError(f"Response list contains non-message objects: {[type(x).__name__ for x in response]}")
    else:
        # 其他类型，尝试作为单个消息处理（可能不应该发生）
        # 但为了兼容性，尝试转换
        messages = [response]
    
    # StateGraph 期望的返回值格式：{"messages": [Message, ...]}
    return {"messages": messages}
