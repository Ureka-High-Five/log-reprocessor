import asyncpg
from typing import List

async def get_genres_by_content_id(pool: asyncpg.Pool, content_id: int) -> List[str]:
    query = """
        SELECT mi.name
        FROM leadme.meta_info_contents mic
        JOIN leadme.meta_info mi ON mic.meta_info_id = mi.id
        WHERE mic.content_id = $1 and mi.type = 'GENRE'
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, content_id)
        return list({row["name"] for row in rows})