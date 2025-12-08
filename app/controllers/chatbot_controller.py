from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.services.vector_service import VectorService
from app.utils.llm_factory import LLMFactory
from app.repositories.chat_repository import ChatRepository
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from typing import List, Optional
import logging

from app.config.settings import Settings

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)

logger = logging.getLogger(__name__)
settings = Settings()

@router.post("/sync")
def sync_context(db: Session = Depends(get_db)):
    """
    Triggers a manual refresh of the Vector Store.
    Fetches all Projects, Skills, etc., and re-generates embeddings.
    """
    service = VectorService(db)
    try:
        result = service.sync_all_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
def get_chat_sessions(
    limit: int = 50, 
    offset: int = 0, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all chat sessions for the admin dashboard.
    Returns session details including message count and last active time.
    """
    repo = ChatRepository(db)
    results = repo.get_all_sessions(limit, offset)
    
    # Format the response
    sessions = []
    for session, count, last_active in results:
        sessions.append({
            "id": str(session.id),
            "created_at": session.created_at,
            "message_count": count,
            "last_active": last_active
        })
        
    return sessions

@router.get("/sessions/{session_id}/messages")
def get_session_messages(
    session_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all messages for a specific chat session.
    """
    repo = ChatRepository(db)
    messages = repo.get_session_messages(session_id)
    
    if not messages:
        # Check if session exists at least
        session = repo.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return []

    return [
        {
            "id": str(m.id),
            "sender": m.sender,
            "content": m.content,
            "created_at": m.created_at
        } 
        for m in messages
    ]

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    
    service = VectorService(db)
    # Instantiate the LLM (Gemini by default)
    try:
        llm = LLMFactory.create_chat_model("gemini")
    except Exception as e:
        await websocket.send_text(f"Error initializing LLM: {str(e)}")
        await websocket.close()
        return

    chat_repo = ChatRepository(db)
    
    # 0. Handle Session & History
    session_id = websocket.query_params.get("session_id")
    
    # Check if session actually exists first (explicit check as requested)
    existing_session = chat_repo.get_session(session_id)
    
    recent_msgs = []
    if existing_session:
        recent_msgs = chat_repo.get_recent_messages(session_id)
    
    # Send history to frontend
    history_payload = [{"sender": m.sender, "text": m.content} for m in recent_msgs]
    if history_payload:
        await websocket.send_json({"type": "history", "payload": history_payload})
    
    # Reconstruct LangChain history
    chat_history = []
    for m in recent_msgs:
        if m.sender == 'user':
            chat_history.append(HumanMessage(content=m.content))
        else:
            chat_history.append(AIMessage(content=m.content))
    
    try:
        while True:
            # 1. Receive User Message
            data = await websocket.receive_text()
            
            # Save User Message
            chat_repo.add_message(session_id, "user", data)
            
            # 1.5. Intent Classification (Filter Logic)
            # Heuristic map to identify filters from query keywords.
            # This is faster than an LLM call and effective for explicit requests.
            filters = []
            lower_query = data.lower()
            
            if "project" in lower_query or "work" in lower_query or "built" in lower_query:
                filters.append("project")
            if "skill" in lower_query or "stack" in lower_query or "tech" in lower_query:
                filters.append("skill")
            if "experience" in lower_query or "job" in lower_query or "career" in lower_query:
                filters.append("experience")
            if "education" in lower_query or "degree" in lower_query or "college" in lower_query:
                filters.append("experience") # Education is stored under experience type
            if "review" in lower_query or "testimonial" in lower_query:
                filters.append("review")
                
            # If no specific filter detected, or if query is generic like "tell me everything", 
            # we default to NO filter (search all), OR we can be selective.
            # Let's default to ALL (None) if empty, to be safe.
            if not filters:
                filters = None

            print(f"DEBUG: Detected Filters: {filters}")

            # 2. Retrieve Context (RAG)
            # Find top relevant documents (Increased to 100 to fit "all" docs for Gemini Context)
            relevant_docs = service.search(data, limit=100, filters=filters)
            
            # DEBUG LOGGING
            if settings.DEBUG:
                logger.info(f"\n--- User Query: {data} ---")
                logger.info(f"--- Retrieved {len(relevant_docs)} Docs ---")
                for i, doc in enumerate(relevant_docs):
                    logger.info(f"Doc {i+1}: {doc.content[:100]}...")
                logger.info("--------------------------------\n")

            context_text = "\n\n".join([doc.content for doc in relevant_docs])
            
            # 3. Construct Prompt with Context
            system_prompt = f"""You are a helpful portfolio assistant for Daryl Fernandes.
            Use the following context to answer the user's question.
            If the answer is not in the context, just say you don't know, but be friendly.
            
            CONTEXT:
            {context_text}
            """
            
            # 4. Stream Response from LLM
            # We use the LangChain invoke/stream method
            # Reconstruct messages with History
            messages = [SystemMessage(content=system_prompt)] + chat_history + [HumanMessage(content=data)]
            
            full_response = ""
            async for chunk in llm.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    # Send JSON structure
                    await websocket.send_json({"type": "content", "payload": chunk.content})
            
            # Send End of Stream signal
            await websocket.send_json({"type": "end"})
            
            # Save Bot Message
            chat_repo.add_message(session_id, "bot", full_response)
            
            # 5. Update History (In-Memory)
            # Keep only last 20 turns for context window
            chat_history.append(HumanMessage(content=data))
            chat_history.append(AIMessage(content=full_response))
            if len(chat_history) > 20: 
                chat_history = chat_history[-20:]
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in websocket: {e}")
        try:
            await websocket.send_json({"type": "error", "payload": str(e)})
        except:
            pass
