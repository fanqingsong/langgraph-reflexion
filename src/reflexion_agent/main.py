"""Reflexion Agent 的主入口点。

本模块提供 Reflexion Agent 的独立运行入口，
可以用于测试和演示 Agent 的功能。
"""

from dotenv import load_dotenv

# 加载环境变量（包括 Azure OpenAI 配置等）
load_dotenv()

from reflexion_agent.graph import create_reflexion_graph

if __name__ == "__main__":
    # 创建 Reflexion Agent 图
    graph = create_reflexion_graph()

    # 生成图的可视化（保存为 PNG 图片）
    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
    print("Graph visualization saved to graph.png")

    # 示例使用：回答关于 AI-Powered SOC 的问题
    res = graph.invoke(
        "Write about AI-Powered SOC / autonomous soc  problem domain, list startups that do that and raised capital."
    )
    
    # 提取并打印答案
    # 检查响应是否包含工具调用结果
    if res and len(res) > 0 and hasattr(res[-1], "tool_calls") and res[-1].tool_calls:
        print("\nAnswer:")
        # 从工具调用的参数中提取答案
        print(res[-1].tool_calls[0]["args"]["answer"])
    
    # 打印完整响应（用于调试）
    print("\nFull response:")
    print(res)
