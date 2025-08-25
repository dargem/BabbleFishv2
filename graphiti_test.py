import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY_4")

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = "neo4j"
neo4j_password = os.getenv("NEO4J_PASS")

import asyncio
import json
from datetime import datetime, timezone

from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from graphiti_core.utils.maintenance.graph_data_operations import clear_data


episodes = [
    {
        "name": "The Premiere",
        "content": "A new hero rises, but a shadow looms over the city.",
        "type": EpisodeType.text,
        "description": "The first episode of our epic tale.",
    }
]


async def add_data(episodes, graphiti):
    """Adding episodes to the graph"""
    for episode in episodes:
        if episode["type"] == EpisodeType.json:
            episode["content"] = json.dumps(episode["content"])
        await graphiti.add_episode(
            name=episode["name"],
            episode_body=episode["content"],
            source=episode["type"],
            source_description=episode["description"],
            reference_time=datetime.now(timezone.utc),
        )
        print(f"Added {episode['name']}")


async def workflow():
    graphiti = Graphiti(
        neo4j_uri,
        neo4j_user,
        neo4j_password,
        llm_client=GeminiClient(
            config=LLMConfig(api_key=api_key, model="gemini-2.5-flash-lite")
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=api_key, embedding_model="embedding-001"
            )
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(
                api_key=api_key, model="gemini-2.5-flash-lite-preview-06-17"
            )
        ),
    )

    await clear_data(graphiti.driver)
    await graphiti.build_indices_and_constraints()
    await add_data(episodes, graphiti)


if __name__ == "__main__":
    print("start")
    asyncio.run(workflow())
    print("end")
