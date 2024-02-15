# pylint: disable=E0611,C0103,C0303
"""
"""
import gradio as gr
from src.llm import LLM  # 确保这个路径正确
from src.config import load_config, update_config, configUpdater

# 假设LLM类不依赖于任何PyQt5组件
llm = LLM()


async def process_input(user_text):
    """
    处理用户输入并返回LLM的响应。
    这里简化了从getLLMAnswer函数获取答案的逻辑。
    """
    load_config()  # 确保这个函数可以在不依赖PyQt的情况下工作
    rag_status = "enabled"  # 假设一个默认值，或者通过其他方式设置
    llm_answers = await llm.get_answer_async(user_text, rag_status)

    # 简化响应，只返回纯RAG的回答（如果可用）
    return llm_answers.get("pure")


# 创建Gradio界面
iface = gr.Interface(
    fn=process_input,
    inputs=gr.Textbox(lines=2, placeholder="Input your questions..."),
    outputs="text",
    title="DST-GPT",
    description="请输入您的问题，系统将自动回答。",
)

# 启动Gradio界面
if __name__ == "__main__":
    iface.launch()
