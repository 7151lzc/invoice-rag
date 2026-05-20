"""
启动入口
可以选择启动API服务或Gradio界面
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description="发票知识库问答系统")
    parser.add_argument("--mode", choices=["api", "web", "init"], default="web",
                        help="启动模式: api(API服务), web(网页界面), init(仅初始化)")
    parser.add_argument("--port", type=int, default=8000,
                        help="API服务端口，默认8000")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        print("启动API服务...")
        import uvicorn
        from api import app
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    
    elif args.mode == "web":
        print("启动网页界面...")
        from app import demo
        demo.launch(share=True)
    
    elif args.mode == "init":
        print("初始化知识库...")
        from qa_chain import QaChain
        qa = QaChain()
        qa.init_knowledge_base()
        print("初始化完成！")


if __name__ == "__main__":
    main()