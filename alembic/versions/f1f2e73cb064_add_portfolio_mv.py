"""add portfolio mv

Revision ID: f1f2e73cb064
Revises: 569433338482
Create Date: 2026-03-12 14:21:03.951593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1f2e73cb064'
down_revision: Union[str, None] = '569433338482'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the materialized view using PostgreSQL JSON functions
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS portfolio_mv AS
        SELECT 
            u.id as user_id,
            u.name,
            u.surname,
            u.title,
            u.email,
            u.phone,
            u.location,
            u.availability,
            u.avatar,
            u.social_links,
            u.about,
            u.featured_skill_ids,
            
            -- Aggregate Experiences into a JSON array
            COALESCE((
                SELECT json_agg(
                    json_build_object(
                        'id', e.id, 
                        'type', e.type, 
                        'title', e.title, 
                        'company', e.organization,
                        'start_date', e.start_date,
                        'end_date', e.end_date,
                        'description', e.description
                    )
                ) 
                FROM experiences e 
                WHERE e.is_visible = true
            ), '[]'::json) as experiences,

            -- Aggregate Projects into a JSON array
            COALESCE((
                SELECT json_agg(
                    json_build_object(
                        'id', p.id, 
                        'type', p.type, 
                        'title', p.title, 
                        'description', p.description,
                        'image', p.image,
                        'tags', p.tags,
                        'url', p.url,
                        'additional_data', p.additional_data,
                        'created_at', p.created_at,
                        'project_category_id', p.project_category_id
                    )
                ) 
                FROM projects p 
                WHERE p.is_visible = true
            ), '[]'::json) as projects,

            -- Aggregate Skill Groups and their Skills
            COALESCE((
                SELECT json_agg(
                    json_build_object(
                        'name', sg.name,
                        'skills', (
                            SELECT COALESCE(json_agg(
                                json_build_object(
                                    'id', s.id,
                                    'name', s.name,
                                    'proficiency', s.proficiency,
                                    'color', s.color,
                                    'icon', s.icon
                                )
                            ), '[]'::json)
                            FROM skills s
                            WHERE s.skill_group_id = sg.id AND s.is_visible = true
                        )
                    )
                )
                FROM skill_groups sg 
                WHERE sg.is_visible = true
            ), '[]'::json) as skill_groups,
            
            -- Aggregate Project Categories
            COALESCE((
                SELECT json_agg(
                    json_build_object(
                        'id', pc.id,
                        'name', pc.name,
                        'is_visible', pc.is_visible
                    )
                )
                FROM project_categories pc
                WHERE pc.is_visible = true
            ), '[]'::json) as project_categories,
            
            -- Aggregate Reviews
            COALESCE((
                SELECT json_agg(
                    json_build_object(
                        'id', r.id,
                        'name', r.name,
                        'content', r.content,
                        'rating', r.rating,
                        'where_known_from', r.where_known_from
                    )
                )
                FROM reviews r
                WHERE r.is_visible = true
            ), '[]'::json) as reviews

        FROM users u;
    """)
    
    # 2. Add a unique index so we can refresh it "CONCURRENTLY" later without locking reads
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_portfolio_mv_user_id ON portfolio_mv (user_id);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_portfolio_mv_user_id;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS portfolio_mv;")
