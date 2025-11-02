"""事件循环条件函数实现。

本模块定义了事件循环条件函数，用于控制图的迭代执行。
"""

from langchain_core.messages import ToolMessage
from langgraph.graph import END


def create_event_loop(max_iterations: int = 2):
    """创建事件循环条件函数。
    
    这个函数返回一个条件函数，用于判断是否继续执行工具调用。
    它通过统计 ToolMessage 的数量来判断已经执行了多少次迭代。
    
    Args:
        max_iterations: 最大迭代次数，默认为 2
        
    Returns:
        function: 条件函数，接收状态并返回下一个节点名称或 END
    """
    def event_loop(state: dict) -> str:
        """事件循环判断函数。
        
        根据当前状态中的工具调用次数决定下一步操作。
        通过统计 ToolMessage 的数量来判断已经执行了多少次迭代。
        
        Args:
            state: 当前状态字典，包含 messages 键（消息列表）
            
        Returns:
            str: 下一步操作的节点名称（"execute_tools"），或 END 表示结束
        """
        # 从状态中提取消息列表
        messages = state.get("messages", [])
        
        # 统计状态中 ToolMessage 的数量
        # ToolMessage 表示工具调用的结果，每执行一次工具就会产生一个 ToolMessage
        # 因此统计 ToolMessage 的数量可以知道已经执行了多少轮工具调用
        count_tool_visits = sum(isinstance(item, ToolMessage) for item in messages)
        num_iterations = count_tool_visits
        
        # 如果超过最大迭代次数，结束流程
        if num_iterations > max_iterations:
            return END
        
        # 否则继续执行工具（进入下一轮改进循环）
        return "execute_tools"
    
    return event_loop
