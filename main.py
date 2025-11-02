"""旧版入口点 - 重定向到新的包结构。

此文件保留用于向后兼容。
新代码应使用: from reflexion_agent.graph import create_reflexion_graph
"""

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from langchain_core.messages import HumanMessage

from reflexion_agent.graph import create_reflexion_graph

if __name__ == "__main__":
    # 创建 Reflexion Agent 图
    graph = create_reflexion_graph()

    # 生成图的可视化（保存为 PNG 图片）
    # 这有助于理解 Agent 的工作流程
    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
    print("Graph visualization saved to graph.png")

    # 示例使用：回答关于 AI-Powered SOC 的问题
    # StateGraph 需要传入状态字典，包含 messages 键
    query = "Write about AI-Powered SOC / autonomous soc  problem domain, list startups that do that and raised capital."
    res = graph.invoke({"messages": [HumanMessage(content=query)]})

    # 提取并打印答案
    # StateGraph 返回状态字典，包含 messages 键
    messages = res.get("messages", [])
    if messages and len(messages) > 0:
        last_message = messages[-1]
        # 检查响应是否包含工具调用结果
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            print("\nAnswer:")
            # 从工具调用的参数中提取答案
            print(last_message.tool_calls[0]["args"]["answer"])
    
    # 打印完整响应（用于调试）
    print("\nFull response:")
    print(res)
