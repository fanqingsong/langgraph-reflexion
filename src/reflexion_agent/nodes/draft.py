"""初始答案生成节点实现。

本模块定义了 draft 节点的实现，该节点负责生成用户的初始答案。
该模块自包含所有需要的逻辑，不依赖其他链模块。
"""

from langchain_core.messages import BaseMessage

from reflexion_agent.infra import create_actor_prompt_template, get_llm_instance
from reflexion_agent.nodes.execute_tools import answer_question_tool


def _create_first_responder_chain():
    """创建初始响应生成链。
    
    这个链用于生成用户的初始答案，包括：
    - 约 250 字的详细答案
    - 自我反思和批评
    - 用于改进的搜索查询建议
    
    Returns:
        Runnable: 配置好的链，可以处理消息并返回结构化答案
    """
    # 获取 LLM 实例
    llm = get_llm_instance()
    
    # 获取提示模板
    actor_prompt_template = create_actor_prompt_template()
    
    # 创建初始响应生成链
    # 绑定 answer_question_tool 工具（使用 @tool 装饰器定义的带执行逻辑的工具函数）
    # 这样 LLM 会调用这个工具，工具会自动执行搜索查询
    first_responder = actor_prompt_template.partial(
        first_instruction="Provide a detailed ~250 word answer."
    ) | llm.bind_tools(tools=[answer_question_tool], tool_choice="AnswerQuestion")
    
    return first_responder


# 创建链实例（延迟初始化，避免在导入时创建）
_first_responder_chain = None


def _get_first_responder_chain():
    """获取 first_responder 链实例（单例模式）。
    
    Returns:
        Runnable: first_responder 链实例
    """
    global _first_responder_chain
    if _first_responder_chain is None:
        _first_responder_chain = _create_first_responder_chain()
    return _first_responder_chain


def draft_node(state: dict) -> dict:
    """初始答案生成节点。
    
    这个节点使用 first_responder 链来生成用户的初始答案。
    它会生成包含答案、反思和搜索查询建议的结构化响应。
    
    Args:
        state: 当前状态字典，包含 messages 键（消息列表）
        
    Returns:
        dict: 包含新消息的状态更新
    """
    # 从状态中提取消息列表
    messages = state.get("messages", [])
    
    # 获取 first_responder 链
    first_responder = _get_first_responder_chain()
    
    # first_responder 是一个 LangChain Runnable，可以直接调用
    # 它会处理消息列表并返回包含工具调用的消息
    # 注意：当使用 init_chat_model 时，invoke 返回的是单个 AIMessage 对象
    response = first_responder.invoke(messages)
    
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
