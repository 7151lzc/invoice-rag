"""
向量数据库管理
使用ChromaDB + 本地Embedding模型存储文档向量
"""

import os
# 设置国内镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import chromadb
from typing import List, Dict
from sentence_transformers import SentenceTransformer


class LocalEmbeddingFunction:
    def __init__(self, model_name: str = 'shibing624/text2vec-base-chinese'):
        """
        初始化本地embedding模型（使用国内镜像可下载的中文模型）
        """
        print(f"正在加载本地Embedding模型: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("模型加载完成。")

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        embeddings = self.model.encode(input).tolist()
        return embeddings


class VectorStore:
    """向量数据库管理类"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # 使用本地embedding函数
        self.embedding_fn = LocalEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=self.embedding_fn
        )
    
    def add_documents(self, documents: List[Dict]):
        if not documents:
            print("没有文档需要添加")
            return
        
        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"已添加 {len(documents)} 个文档到向量库")
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        documents = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                doc = {
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i] if results['documents'] else "",
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                }
                documents.append(doc)
        
        return documents
    
    def count(self) -> int:
        return self.collection.count()
    
    def delete_all(self):
        self.client.delete_collection("documents")
        self.collection = self.client.create_collection(
            name="documents",
            embedding_function=self.embedding_fn
        )
        print("已清空向量库")


if __name__ == "__main__":
    store = VectorStore()
    print(f"当前文档数量: {store.count()}")