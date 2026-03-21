import os
print("🚀 PRODUCTION PM AGENT STARTING...")
os.system("python rag_system/index_docs.py")
os.system("python wrapper_agent.py")
