from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.vector_store import VectorEmbedding
from app.models.project_model import Project
from app.models.skill_model import Skill
from app.models.experience_model import Experience
from app.models.review_model import Review
from app.models.user_model import User
from app.utils.llm_factory import LLMFactory
import os

class VectorService:
    def __init__(self, db: Session):
        self.db = db
        # Initialize Embeddings Model via Factory
        self.embeddings_model = LLMFactory.create_embeddings_model("gemini")

    def generate_embedding(self, text_content: str) -> List[float]:
        """Generate embedding vector for a given text."""
        return self.embeddings_model.embed_query(text_content)

    def search(self, query_text: str, limit: int = 5, filters: List[str] = None) -> List[VectorEmbedding]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query_text: The search query.
            limit: Maximum number of results.
            filters: Optional list of source_types to include (e.g. ['project', 'skill']).
        """
        query_vector = self.generate_embedding(query_text)
        
        # Start building the query
        query = self.db.query(VectorEmbedding)
        
        # Apply filters if provided
        if filters:
            query = query.filter(VectorEmbedding.source_type.in_(filters))
        
        # pgvector L2 distance operator is <->
        results = query.order_by(
            VectorEmbedding.embedding.l2_distance(query_vector)
        ).limit(limit).all()
        
        return results

    def clear_all_vectors(self):
        """Delete all existing vectors to ensure a clean sync."""
        self.db.query(VectorEmbedding).delete()
        self.db.commit()

    def sync_all_data(self):
        """
        Universal Context Sync:
        Fetches all data from Projects, Skills, Experience, Reviews, and Users.
        Serializes them into text.
        Generates embeddings and stores them.
        """
        self.clear_all_vectors()
        total_count = 0

        # 1. Projects
        projects = self.db.query(Project).filter(Project.is_visible == True).all()
        for p in projects:
            # Create a rich text representation
            content = f"Project: {p.title}. Type: {p.type}. Description: {p.description or ''}. Tags: {', '.join(p.tags or [])}."
            if p.additional_data:
                 # If we have README content or extra data, append it (truncated if massive)
                 readme_summary = str(p.additional_data)[:500] 
                 content += f" Details: {readme_summary}"
            
            self._save_vector(content, "project", p.id)
            total_count += 1

        # 2. Skills
        skills = self.db.query(Skill).join(Skill.skill_group).filter(Skill.is_visible == True).all()
        for s in skills:
            content = f"Skill: {s.name}. Proficiency: {s.proficiency}/5. Group: {s.skill_group.name}."
            self._save_vector(content, "skill", s.id)
            total_count += 1
            
        # 3. Experience & Education
        experiences = self.db.query(Experience).filter(Experience.is_visible == True).all()
        for e in experiences:
            type_str = "Education" if e.type == "education" else "Work Experience"
            content = f"{type_str}: {e.title} at {e.organization}. {e.start_date} to {e.end_date or 'Present'}. {e.description or ''}"
            self._save_vector(content, "experience", e.id)
            total_count += 1

        # 4. Reviews
        reviews = self.db.query(Review).filter(Review.is_visible == True).all()
        for r in reviews:
            content = f"Review from {r.name} ({r.where_known_from or 'Client'}): '{r.content}'. Rating: {r.rating}/5."
            self._save_vector(content, "review", r.id)
            total_count += 1

        # 5. User Profile (Basic Info)
        users = self.db.query(User).all() # Assuming usually just one user
        for u in users:
            content = f"About Me (Daryl Fernandes): {u.title or 'Developer'}. Location: {u.location}. Bio: {u.about or ''}. Contact: {u.email}."
            if u.social_links:
                content += f" Socials: {u.social_links}."
            self._save_vector(content, "user", u.id)
            total_count += 1
            
        return {"status": "success", "vectors_synced": total_count}

    def _save_vector(self, content: str, source_type: str, source_id: Any):
        """Helper to compute embedding and save record."""
        vector = self.generate_embedding(content)
        embedding_record = VectorEmbedding(
            content=content,
            embedding=vector,
            source_type=source_type,
            source_id=source_id,
            metadata_json={"source": source_type}
        )
        self.db.add(embedding_record)
        self.db.commit()
