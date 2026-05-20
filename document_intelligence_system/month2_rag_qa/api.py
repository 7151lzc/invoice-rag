"""
FastAPI接口
提供HTTP服务
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from qa_chain import QaChain


app = FastAPI(title="发票知识库问答API", description="基于RAG的发票查询系统")


class Question(BaseModel):
    """问题模型"""
    question: str
    top_k: Optional[int] = 3


class AnswerResponse(BaseModel):
    """答案响应模型"""
    answer: str
    sources: List[dict]
    success: bool


# 全局问答链实例
qa_chain = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化知识库"""
    global qa_chain
    qa_chain = QaChain()
    qa_chain.init_knowledge_base()


@app.get("/")
async def root():
    return {"message": "发票知识库问答API", "status": "running"}


@app.get("/health")
async def health():
    """健康检查"""
    if qa_chain:
        return {"status": "ok", "doc_count": qa_chain.vector_store.count()}
    return {"status": "initializing"}


@app.post("/ask", response_model=AnswerResponse)
async def ask(question: Question):
    """问答接口"""
    if not qa_chain:
        raise HTTPException(status_code=503, detail="服务正在初始化")
    
    result = qa_chain.answer(question.question)
    
    return AnswerResponse(
        answer=result["answer"],
        sources=result["sources"],
        success=True
    )


@app.get("/search")
async def search(q: str, top_k: int = 3):
    """检索接口"""
    if not qa_chain:
        raise HTTPException(status_code=503, detail="服务正在初始化")
    
    results = qa_chain.search(q, top_k)
    return {"results": results}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)