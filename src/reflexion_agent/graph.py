"""Reflexion Agent 的图定义。

本模块定义了 Reflexion Agent 的核心图结构，实现了一个自我反思和迭代改进的工作流。
图的工作流程：
1. draft: 生成初始答案
2. execute_tools: 执行搜索工具获取更多信息
3. revise: 基于新信息修订答案
4. 条件循环：根据迭代次数决定是继续改进还是结束
"""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

# 直接从 nodes 包导入节点函数
from reflexion_agent.nodes import (
    create_event_loop,
    draft_node,
    execute_tools_node,
    revise_node,
)


# 定义状态结构
class ReflexionState(TypedDict):
    """Reflexion Agent 的状态定义。
    
    状态包含消息列表，用于在节点之间传递消息历史。
    """
    messages: Annotated[list[BaseMessage], add_messages]


# 最大迭代次数：限制反思循环的执行次数，避免无限循环
MAX_ITERATIONS = 2


def create_reflexion_graph(max_iterations: int = MAX_ITERATIONS):
    """创建 Reflexion Agent 的工作流图。
    
    构建一个包含以下节点的图：
    - draft: 初始答案生成节点
    - execute_tools: 工具执行节点（搜索）
    - revise: 答案修订节点
    
    图的流程：
    1. 从 draft 节点开始，生成初始答案
    2. draft -> execute_tools：执行工具调用获取更多信息
    3. execute_tools -> revise：基于工具结果修订答案
    4. 在 revise 后，根据迭代次数决定：
       - 如果未达到最大迭代次数，返回 execute_tools 继续改进
       - 如果达到最大迭代次数，结束流程
    
    Args:
        max_iterations: 反思循环的最大迭代次数，默认为 2
        
    Returns:
        Compiled StateGraph: 编译后的图对象，可以直接调用 invoke 方法
    """
    # 创建状态图构建器
    # StateGraph 是 LangGraph 框架提供的一种结构化工作流管理方式。
    # 它使用自定义状态结构来管理节点之间的数据传递。
    # 在这个实现中，我们定义 ReflexionState 来包含消息列表，使用 add_messages 来合并消息。
    builder = StateGraph(ReflexionState)

    # 添加三个主要节点
    # draft: 初始答案生成节点，使用 draft_node 函数
    builder.add_node("draft", draft_node)
    # execute_tools: 工具执行节点，执行搜索查询
    builder.add_node("execute_tools", execute_tools_node)
    # revise: 答案修订节点，使用 revise_node 函数
    builder.add_node("revise", revise_node)

    # 创建事件循环条件函数
    # 这个函数会根据迭代次数决定是继续执行还是结束流程
    event_loop = create_event_loop(max_iterations=max_iterations)

    # 添加边连接节点
    # START -> draft: 从入口点开始，执行初始答案生成
    builder.add_edge(START, "draft")
    # draft -> execute_tools：生成初始答案后执行工具调用
    builder.add_edge("draft", "execute_tools")
    # execute_tools -> revise：搜索完成后修订答案
    builder.add_edge("execute_tools", "revise")
    # revise -> (条件判断) -> execute_tools 或 END：根据迭代次数决定继续还是结束
    builder.add_conditional_edges("revise", event_loop)

    # 编译并返回图
    # 注意：使用 add_edge(START, "draft") 会自动设置入口点，无需再调用 set_entry_point
    return builder.compile()



