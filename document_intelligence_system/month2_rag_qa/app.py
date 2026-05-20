import gradio as gr
from qa_chain import QaChain

# 初始化问答链
qa = QaChain()
qa.init_knowledge_base()

def chat(message, history):
    """聊天函数"""
    if not message:
        return ""
    
    result = qa.answer(message)
    answer = result["answer"]
    
    # 添加来源信息
    if result.get("sources"):
        answer += "\n\n📚 来源："
        for source in result["sources"]:
            meta = source.get("metadata", {})
            if meta.get("source"):
                answer += f"\n- {meta.get('source')}"
    
    return answer

# 去掉 theme 参数，使用默认样式
demo = gr.ChatInterface(
    fn=chat,
    title="🧾 发票知识库问答系统",
    description="基于RAG技术的发票智能查询助手。\n\n**示例问题：**\n- 总共有多少张发票？\n- 金额最大的发票是多少钱？\n- 发票号码是03531988的金额是多少？\n- 销售方是谁？",
    examples=[
        "总共有多少张发票？",
        "金额最大的发票是多少钱？",
        "发票号码是03531988的金额是多少？",
        "销售方是谁？"
    ]
)

if __name__ == "__main__":
    demo.launch(share=True)