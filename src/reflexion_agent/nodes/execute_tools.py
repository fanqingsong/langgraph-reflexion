"""工具执行节点实现。

本模块定义了 execute_tools 节点的实现，该节点负责执行搜索工具。
该模块自包含所有需要的逻辑，不依赖其他工具模块。
"""

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.messages import BaseMessage
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import ToolNode

from reflexion_agent.infra import AnswerQuestion, ReviseAnswer


def _create_search_tool():
    """创建 Tavily 搜索工具。
    
    Returns:
        TavilySearchResults: 配置好的搜索工具实例
    """
    # 初始化 Tavily 搜索 API 包装器
    # Tavily 是一个专业的搜索 API，用于获取高质量的搜索结果
    search = TavilySearchAPIWrapper()
    # 创建 Tavily 搜索工具，限制最多返回 5 个结果
    tavily_tool = TavilySearchResults(api_wrapper=search, max_results=5)
    return tavily_tool


def _execute_search_queries_internal(search_queries: list[str]) -> list:
    """内部搜索执行函数。
    
    实际的搜索逻辑实现，由工具函数调用。
    
    Args:
        search_queries: 要执行的搜索查询列表
        
    Returns:
        list: 搜索结果列表，每个元素对应一个查询的结果
    """
    # 获取搜索工具实例
    tavily_tool = _create_search_tool()
    
    # 批量执行搜索查询
    # 将查询列表转换为字典列表格式，供 Tavily 工具使用
    return tavily_tool.batch([{"query": query} for query in search_queries])


def _answer_question_tool_function(
    answer: str,
    reflection: dict,
    search_queries: list[str],
) -> list:
    """AnswerQuestion 工具的执行函数。
    
    这是一个带执行逻辑的工具函数。当 LLM 调用此工具时：
    1. LLM 会按照 AnswerQuestion Schema 提供参数（answer, reflection, search_queries）
    2. 工具会执行 search_queries 中的搜索查询
    3. 返回搜索结果
    
    这个工具对应 draft 节点中 LLM 调用的 AnswerQuestion 工具。
    
    Args:
        answer: 约250字的详细答案（工具调用参数，实际不用于搜索）
        reflection: 对初始答案的反思（工具调用参数，实际不用于搜索）
        search_queries: 要执行的搜索查询列表（这是真正会被使用的参数）
        
    Returns:
        list: 搜索结果列表，每个元素对应一个查询的结果
    """
    # 执行搜索查询（忽略其他参数，只使用 search_queries）
    return _execute_search_queries_internal(search_queries)


# args_schema 用于指定工具（tool）参数的 Pydantic 数据模型（schema）。
# 这样可以对 LLM 工具调用时输入参数进行校验和类型约束，确保参数结构正确。
# 本例中，AnswerQuestion 是一个继承自 BaseModel 的 schema，定义了 answer、reflection、search_queries 等字段。
# LLM 在调用工具时，会按该 schema 格式传递并校验参数。
# 使用 StructuredTool.from_function 可以显式设置工具名称为 "AnswerQuestion"
answer_question_tool = StructuredTool.from_function(
    func=_answer_question_tool_function,
    name="AnswerQuestion",
    description="执行搜索查询以获取信息，用于回答问题和生成初始答案。",
    args_schema=AnswerQuestion,
)


def _revise_answer_tool_function(
    answer: str,
    reflection: dict,
    search_queries: list[str],
    references: list[str],
) -> list:
    """ReviseAnswer 工具的执行函数。
    
    这是一个带执行逻辑的工具函数。当 LLM 调用此工具时：
    1. LLM 会按照 ReviseAnswer Schema 提供参数（answer, reflection, search_queries, references）
    2. 工具会执行 search_queries 中的搜索查询
    3. 返回搜索结果
    
    这个工具对应 revise 节点中 LLM 调用的 ReviseAnswer 工具。
    
    Args:
        answer: 修订后的答案（工具调用参数，实际不用于搜索）
        reflection: 对初始答案的反思（工具调用参数，实际不用于搜索）
        search_queries: 要执行的搜索查询列表（这是真正会被使用的参数）
        references: 引用列表（工具调用参数，实际不用于搜索）
        
    Returns:
        list: 搜索结果列表，每个元素对应一个查询的结果
    """
    # 执行搜索查询（忽略其他参数，只使用 search_queries）
    return _execute_search_queries_internal(search_queries)


# 使用 StructuredTool.from_function 可以显式设置工具名称为 "ReviseAnswer"
revise_answer_tool = StructuredTool.from_function(
    func=_revise_answer_tool_function,
    name="ReviseAnswer",
    description="执行搜索查询以获取信息，用于修订和改进答案。",
    args_schema=ReviseAnswer,
)


def _create_tool_node():
    """创建工具节点。
    
    显式注册所有可用的工具。每个工具都是使用 StructuredTool.from_function 创建的，
    包含实际的执行逻辑。工具名称通过 name 参数显式设置为 Schema 类名。
    这样当 LLM 调用工具时，ToolNode 可以根据工具名称找到对应的工具并执行。
    
    注册的工具：
    - answer_question_tool: 用于初始答案生成时的搜索（显式名称: "AnswerQuestion"）
    - revise_answer_tool: 用于答案修订时的搜索（显式名称: "ReviseAnswer"）
    
    Returns:
        ToolNode: 配置好的工具节点实例
    """
    # 使用 StructuredTool.from_function 创建的工具实例
    # 工具名称通过 name="..." 参数显式设置为 Schema 类名（"AnswerQuestion" 和 "ReviseAnswer"）
    # ToolNode 内部会创建一个 {tool.name: tool} 的映射字典，用于匹配工具调用
    tool_node = ToolNode(
        [
            answer_question_tool,  # 工具名称: "AnswerQuestion"（通过 StructuredTool.from_function 显式设置）
            revise_answer_tool,    # 工具名称: "ReviseAnswer"（通过 StructuredTool.from_function 显式设置）
        ]
    )
    
    return tool_node


# 创建工具节点实例（延迟初始化，避免在导入时创建）
_tool_node_instance = None


def _get_tool_node():
    """获取工具节点实例（单例模式）。
    
    Returns:
        ToolNode: 工具节点实例
    """
    global _tool_node_instance
    if _tool_node_instance is None:
        _tool_node_instance = _create_tool_node()
    return _tool_node_instance


def execute_tools_node(state: dict) -> dict:
    """工具执行节点。
    
    这个节点执行 LLM 生成的搜索查询，使用 Tavily 搜索工具
    来获取相关信息以改进答案。
    
    Args:
        state: 当前状态字典，包含 messages 键（消息列表）
        
    Returns:
        dict: 包含工具执行结果的状态更新
    """
    # 从状态中提取消息列表
    messages = state.get("messages", [])
    
    # 获取工具节点实例
    tool_node = _get_tool_node()
    
    # tool_node 是一个 ToolNode 实例，它会：
    # 1. 检测消息中的工具调用
    # 2. 执行对应的工具（这里是搜索查询）
    # 3. 返回工具执行结果（消息列表）
    # 注意：ToolNode.invoke() 在 StateGraph 节点中调用时，需要传入消息列表
    result = tool_node.invoke(messages)
    
    # ToolNode 返回的是消息列表，我们需要包装成 StateGraph 期望的格式
    # 确保 result 是列表格式
    if isinstance(result, list):
        return {"messages": result}
    elif isinstance(result, dict) and "messages" in result:
        # 如果已经是字典格式，直接返回
        return result
    else:
        # 其他情况，包装成列表
        from langchain_core.messages import BaseMessage
        if isinstance(result, BaseMessage):
            return {"messages": [result]}
        return {"messages": []}
