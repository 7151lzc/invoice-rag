"""
问答链
结合检索和LLM回答问题
"""

import os
from openai import OpenAI
from vector_store import VectorStore
from document_loader import DocumentLoader


class QaChain:
    """RAG问答链"""
    
    def __init__(self):
        """初始化问答链"""
        self.vector_store = VectorStore()
        self.loader = DocumentLoader()
        
        # 初始化LLM客户端
        self.llm = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://aistudio.baidu.com/llm/lmapi/v3"
        )
    
    def init_knowledge_base(self):
        """初始化知识库：加载文档并建立向量索引"""
        print("正在加载文档...")
        documents = self.loader.load_all()
        
        if not documents:
            print("没有找到文档，请先放置发票JSON文件到 data/invoices/")
            return False
        
        print(f"正在建立向量索引...")
        self.vector_store.add_documents(documents)
        print(f"知识库初始化完成，共 {self.vector_store.count()} 个文档")
        return True
    
    def search(self, query: str, top_k: int = 3) -> list:
        """检索相关文档"""
        return self.vector_store.search(query, top_k)
    
    def answer(self, question: str) -> dict:
        """
        回答问题
        :param question: 用户问题
        :return: 包含答案和检索结果的字典
        """
        # 1. 检索相关文档
        relevant_docs = self.search(question)
        
        if not relevant_docs:
            return {
                "answer": "知识库中没有相关信息，请先导入发票数据。",
                "sources": []
            }
        
        # 2. 构建上下文
        context = "\n\n".join([doc["text"] for doc in relevant_docs])
        sources = [{"id": doc["id"], "metadata": doc["metadata"]} for doc in relevant_docs]
        
        # 3. 构建提示词
        prompt = f"""你是一个发票信息查询助手。请根据以下知识库内容回答用户的问题。

知识库内容：
{context}

用户问题：{question}

要求：
1. 只根据提供的知识库内容回答
2. 如果知识库中没有相关信息，就说"未找到相关信息"
3. 回答要简洁、准确
4. 如果是查询金额、日期等数字信息，直接给出数字

回答："""
        
        # 4. 调用LLM
        try:
            response = self.llm.chat.completions.create(
                model="ernie-4.5-turbo-vl",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "sources": sources,
                "context": context
            }
            
        except Exception as e:
            return {
                "answer": f"调用LLM出错: {str(e)}",
                "sources": sources
            }
    
    def add_invoice(self, invoice_data: dict, filename: str):
        """
        动态添加新发票到知识库
        :param invoice_data: 发票提取结果
        :param filename: 文件名
        """
        from document_loader import DocumentLoader
        
        loader = DocumentLoader()
        doc_text = loader._invoice_to_text(invoice_data, filename)
        
        doc = {
            "id": filename.replace('.json', ''),
            "text": doc_text,
            "metadata": {
                "source": filename,
                "type": "invoice",
                "invoice_number": invoice_data.get("invoice_number", ""),
                "amount": invoice_data.get("amount", ""),
                "date": invoice_data.get("date", ""),
                "seller": invoice_data.get("seller", ""),
                "buyer": invoice_data.get("buyer", "")
            }
        }
        
        self.vector_store.add_documents([doc])
        print(f"已添加发票: {filename}")


if __name__ == "__main__":
    # 测试问答链
    qa = QaChain()
    qa.init_knowledge_base()
    
    # 测试问题
    questions = [
        "总共有多少张发票？",
        "金额最大的发票是多少钱？",
        "销售方叫什么的发票有哪些？"
    ]
    
    for q in questions:
        print(f"\n问题: {q}")
        result = qa.answer(q)
        print(f"答案: {result['answer']}")