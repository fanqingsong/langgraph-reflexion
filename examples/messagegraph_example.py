"""MessageGraph 基础示例和详细讲解。

本示例演示如何使用 LangGraph 的 MessageGraph 构建一个简单的工作流，
并详细解释每一步的执行过程。
"""

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessageGraph, END, START

# 初始化 LLM（用于演示）
llm = ChatOpenAI(model="gpt-4", temperature=0)


def create_simple_message_graph():
    """创建一个简单的 MessageGraph 示例。
    
    这个图包含三个节点：
    1. greet - 打招呼节点
    2. respond - 响应节点
    3. farewell - 告别节点
    
    工作流程：
    START -> greet -> respond -> farewell -> END
    """
    # ==========================================
    # 步骤 1: 创建 MessageGraph 构建器
    # ==========================================
    # MessageGraph 是 LangGraph 提供的图构建器
    # 它专门用于处理基于消息的工作流（如聊天机器人）
    builder = MessageGraph()
    
    # ==========================================
    # 步骤 2: 定义节点函数
    # ==========================================
    
    def greet_node(state):
        """打招呼节点。
        
        Args:
            state: 当前状态，包含消息列表
            
        Returns:
            dict: 包含新消息的状态更新
        """
        # MessageGraph 中的 state 是消息列表
        # 我们添加一条 AI 消息作为打招呼
        return {"messages": [AIMessage(content="你好！我是 AI 助手。")]}
    
    def respond_node(state):
        """响应节点：处理用户消息并生成回复。
        
        Args:
            state: 当前状态，包含所有消息（包括用户的消息）
            
        Returns:
            dict: 包含 AI 回复消息的状态更新
        """
        # 获取最后一条用户消息
        user_message = state[-1]
        
        # 使用 LLM 生成回复
        # 这里我们简化处理，直接生成一个响应
        response = llm.invoke(state)
        
        # 返回新消息
        return {"messages": [response]}
    
    def farewell_node(state):
        """告别节点。
        
        Args:
            state: 当前状态
            
        Returns:
            dict: 包含告别消息的状态更新
        """
        return {"messages": [AIMessage(content="再见！很高兴为您服务。")]}
    
    # ==========================================
    # 步骤 3: 添加节点到图中
    # ==========================================
    # 节点是图中的执行单元，每个节点对应一个函数
    builder.add_node("greet", greet_node)
    builder.add_node("respond", respond_node)
    builder.add_node("farewell", farewell_node)
    
    # ==========================================
    # 步骤 4: 添加边（连接节点）
    # ==========================================
    # 边定义了节点的执行顺序
    
    # START 是特殊节点，表示图的入口点
    # START -> greet: 从入口点直接到打招呼节点
    builder.add_edge(START, "greet")
    
    # greet -> respond: 打招呼后进入响应节点
    builder.add_edge("greet", "respond")
    
    # respond -> farewell: 响应后进入告别节点
    builder.add_edge("respond", "farewell")
    
    # farewell -> END: 告别后结束流程
    # END 是特殊节点，表示图的结束点
    builder.add_edge("farewell", END)
    
    # ==========================================
    # 步骤 5: 编译图
    # ==========================================
    # 编译后的图可以执行
    graph = builder.compile()
    
    return graph


def create_conditional_message_graph():
    """创建一个带条件边的 MessageGraph 示例。
    
    这个图演示了如何使用条件边来决定执行路径。
    
    工作流程：
    START -> check_message -> (条件判断) -> happy_path 或 sad_path -> END
    """
    builder = MessageGraph()
    
    def check_message_node(state):
        """检查消息节点：分析消息内容。
        
        Args:
            state: 当前状态
            
        Returns:
            dict: 添加分析结果消息
        """
        last_message = state[-1]
        content = last_message.content.lower()
        
        # 检查消息的情感倾向
        if "happy" in content or "good" in content or "great" in content:
            result = "positive"
        elif "sad" in content or "bad" in content or "terrible" in content:
            result = "negative"
        else:
            result = "neutral"
        
        return {"messages": [AIMessage(content=f"检测到消息情感: {result}")]}
    
    def happy_path_node(state):
        """积极路径节点。
        
        Args:
            state: 当前状态
            
        Returns:
            dict: 添加积极回复
        """
        return {"messages": [AIMessage(content="太好了！我很高兴听到这个消息！")]}
    
    def sad_path_node(state):
        """消极路径节点。
        
        Args:
            state: 当前状态
            
        Returns:
            dict: 添加安慰回复
        """
        return {"messages": [AIMessage(content="我理解你的感受。如果需要，我可以帮助你。")]}
    
    # 添加节点
    builder.add_node("check_message", check_message_node)
    builder.add_node("happy_path", happy_path_node)
    builder.add_node("sad_path", sad_path_node)
    
    # 添加边
    builder.add_edge(START, "check_message")
    
    # 定义条件函数
    def route_condition(state):
        """条件路由函数：根据消息内容决定下一步。
        
        Args:
            state: 当前状态（消息列表）
            
        Returns:
            str: 下一个节点的名称，或 END
        """
        # 获取最后一条消息
        last_message = state[-1]
        content = last_message.content.lower()
        
        # 根据内容决定路由
        if "positive" in content:
            return "happy_path"
        elif "negative" in content:
            return "sad_path"
        else:
            # 中性消息，直接结束
            return END
    
    # 添加条件边
    # 条件边允许根据状态动态决定下一个节点
    builder.add_conditional_edges("check_message", route_condition)
    
    # 添加从路径节点到结束的边
    builder.add_edge("happy_path", END)
    builder.add_edge("sad_path", END)
    
    # 编译图
    graph = builder.compile()
    
    return graph


def explain_execution_process():
    """详细讲解 MessageGraph 的执行过程。"""
    print("=" * 80)
    print("MessageGraph 执行过程详解")
    print("=" * 80)
    print()
    
    print("1. 图的结构")
    print("-" * 80)
    print("""
    MessageGraph 是一个有向无环图（DAG），由以下部分组成：
    
    - 节点（Nodes）: 执行具体任务的函数
      * 每个节点接收一个状态（消息列表）
      * 节点函数返回一个字典，包含要添加到状态中的新消息
      
    - 边（Edges）: 连接节点的路径
      * 普通边：无条件连接，总是执行
      * 条件边：根据状态动态决定路径
      
    - 特殊节点：
      * START: 图的入口点
      * END: 图的结束点
    """)
    
    print("2. 状态管理")
    print("-" * 80)
    print("""
    MessageGraph 的状态是消息列表（List[Message]）：
    
    - 初始状态：包含用户的初始消息（HumanMessage）
    - 节点执行：每个节点可以添加新消息到状态
    - 状态传递：状态自动在节点之间传递
    
    消息类型：
    - HumanMessage: 用户消息
    - AIMessage: AI 回复消息
    - SystemMessage: 系统消息
    - ToolMessage: 工具调用结果消息
    """)
    
    print("3. 执行流程")
    print("-" * 80)
    print("""
    当调用 graph.invoke(initial_message) 时：
    
    步骤 1: 初始化状态
    ┌─────────────────────────────────────┐
    │ state = [HumanMessage("...")]       │
    └─────────────────────────────────────┘
    
    步骤 2: 从 START 开始
    ┌─────────────────────────────────────┐
    │ 根据边的定义，找到第一个节点          │
    └─────────────────────────────────────┘
    
    步骤 3: 执行节点函数
    ┌─────────────────────────────────────┐
    │ node_function(state)               │
    │ → 返回: {"messages": [new_message]} │
    │ → 状态更新: state += new_message   │
    └─────────────────────────────────────┘
    
    步骤 4: 根据边决定下一个节点
    ┌─────────────────────────────────────┐
    │ 如果是普通边：直接跳转               │
    │ 如果是条件边：执行条件函数决定路径    │
    └─────────────────────────────────────┘
    
    步骤 5: 重复步骤 3-4，直到到达 END
    ┌─────────────────────────────────────┐
    │ 遇到 END → 返回最终状态              │
    └─────────────────────────────────────┘
    """)
    
    print("4. 节点函数的编写规则")
    print("-" * 80)
    print("""
    节点函数必须遵循以下规则：
    
    1. 接收参数：
       def node_function(state: List[Message])
       - state 是消息列表
       
    2. 返回值：
       return {"messages": [Message, ...]}
       - 返回一个字典，包含 "messages" 键
       - 值是新消息的列表（会被添加到状态中）
       
    3. 状态更新：
       - 返回的消息会自动追加到状态列表末尾
       - 后续节点会看到所有历史消息
    """)
    
    print("5. 条件边的使用")
    print("-" * 80)
    print("""
    条件边允许根据状态动态决定执行路径：
    
    builder.add_conditional_edges(
        source_node,      # 源节点
        condition_func    # 条件函数
    )
    
    条件函数规则：
    - 接收参数: state (List[Message])
    - 返回值: 字符串（下一个节点名称）或 END
    
    示例：
    def route(state):
        if some_condition(state):
            return "node_a"
        else:
            return "node_b"
    """)


def run_simple_example():
    """运行简单示例。"""
    print("\n" + "=" * 80)
    print("简单示例：线性工作流")
    print("=" * 80 + "\n")
    
    # 创建图
    graph = create_simple_message_graph()
    
    # 定义初始消息
    initial_message = [HumanMessage(content="你好")]
    
    print(f"输入: {initial_message[0].content}")
    print("\n执行流程:")
    print("  START -> greet -> respond -> farewell -> END\n")
    
    # 执行图
    result = graph.invoke(initial_message)
    
    print("输出消息:")
    for i, msg in enumerate(result, 1):
        print(f"  [{i}] {msg.type}: {msg.content}")
    print()


def run_conditional_example():
    """运行条件边示例。"""
    print("\n" + "=" * 80)
    print("条件边示例：动态路由")
    print("=" * 80 + "\n")
    
    # 创建图
    graph = create_conditional_message_graph()
    
    # 测试用例 1: 积极消息
    print("测试用例 1: 积极消息")
    print("-" * 80)
    message1 = [HumanMessage(content="I'm feeling happy today!")]
    print(f"输入: {message1[0].content}")
    result1 = graph.invoke(message1)
    print("执行路径: START -> check_message -> happy_path -> END")
    print("\n输出:")
    for msg in result1:
        print(f"  {msg.type}: {msg.content}")
    print()
    
    # 测试用例 2: 消极消息
    print("测试用例 2: 消极消息")
    print("-" * 80)
    message2 = [HumanMessage(content="I'm feeling sad today.")]
    print(f"输入: {message2[0].content}")
    result2 = graph.invoke(message2)
    print("执行路径: START -> check_message -> sad_path -> END")
    print("\n输出:")
    for msg in result2:
        print(f"  {msg.type}: {msg.content}")
    print()


if __name__ == "__main__":
    # 打印详细讲解
    explain_execution_process()
    
    # 运行简单示例
    run_simple_example()
    
    # 运行条件边示例
    # run_conditional_example()  # 取消注释以运行条件边示例

