# Backend

FastAPI chịu trách nhiệm cho API, tutor agent, RAG, citation, upload và long-term learning memory.

Luồng chính đi từ `api/routes/chat.py` → `services/chat_service.py` → `agent/tutor_agent.py` → các tool trong `agent/tools/`.

