"""Stage 0: Research preprocessing layer for film analysis.

This module gathers specialized research by calling models with different
prompts focused on cultural context, narrative structure, and philosophy.
The research findings are then used to enrich the user's query before
sending it to the main council (Stages 1-3).
"""

from typing import List, Dict, Any
from .openrouter import query_models_parallel, query_model
from .config import RESEARCH_MODEL


# Specialized research prompts for film analysis
RESEARCH_PROMPTS = {
    "cultural_context": """You are a film studies expert specializing in cultural and regional cinema.

Analyze the following film-related query and provide relevant cultural context that would be important for understanding it:

Query: {query}

Focus on:
- Regional cinema conventions (especially if Telugu/South Indian cinema is relevant)
- Cultural references, traditions, and regional storytelling patterns
- Historical context of the film industry in that region
- Audience expectations and cultural resonance
- Language-specific nuances and symbolism

Provide 2-3 key cultural insights that would help analyze this film more deeply.""",

    "narrative_structure": """You are a narrative theory and screenwriting expert.

Analyze the following film-related query and provide insights about narrative structure and storytelling:

Query: {query}

Focus on:
- Story frameworks that might be at play (hero's journey, three-act structure, etc.)
- Character arc patterns and archetypes
- Plot structure and narrative techniques
- Dramatic elements (conflict, stakes, turning points)
- How the narrative serves thematic goals

Provide 2-3 key narrative insights that would help analyze this film's storytelling.""",

    "philosophical_themes": """You are a philosophy and mythology expert with deep knowledge of Indian philosophical traditions.

Analyze the following film-related query and identify relevant philosophical themes:

Query: {query}

Focus on:
- Core philosophical concepts (dharma, karma, maya, moksha, etc.)
- Sanskrit terminology and its significance
- Mythological parallels and archetypal patterns
- Ethical and moral dimensions
- Universal vs. culture-specific philosophical themes
- How philosophy manifests in character choices and plot

Provide 2-3 key philosophical insights that would help analyze this film's deeper meaning."""
}


async def stage0_research_gather(
    user_query: str,
    research_categories: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Stage 0: Gather specialized research by querying models with different prompts.

    Args:
        user_query: The user's original question
        research_categories: List of research categories to gather (defaults to all)

    Returns:
        List of dicts with 'category', 'prompt', and 'findings' keys
    """
    if research_categories is None:
        research_categories = list(RESEARCH_PROMPTS.keys())

    # Build prompts for each research category
    research_tasks = {}
    for category in research_categories:
        if category in RESEARCH_PROMPTS:
            prompt = RESEARCH_PROMPTS[category].format(query=user_query)
            research_tasks[category] = prompt

    # Query the research model with all prompts in parallel
    # We'll create a "fake" model list where each model identifier includes the category
    # This allows us to use query_models_parallel while tracking which response is which
    models_with_category = [f"{RESEARCH_MODEL}#{category}" for category in research_tasks.keys()]
    messages_list = [[{"role": "user", "content": prompt}] for prompt in research_tasks.values()]

    # We need to call each one separately since they have different prompts
    import asyncio
    tasks = []
    for category, prompt in research_tasks.items():
        messages = [{"role": "user", "content": prompt}]
        tasks.append(query_model(RESEARCH_MODEL, messages))

    # Execute all research queries in parallel
    responses = await asyncio.gather(*tasks)

    # Format results
    stage0_results = []
    for category, response in zip(research_tasks.keys(), responses):
        if response is not None:
            stage0_results.append({
                "category": category,
                "prompt": research_tasks[category],
                "findings": response.get('content', '')
            })

    return stage0_results


def enrich_query_with_research(
    original_query: str,
    research_findings: List[Dict[str, Any]]
) -> str:
    """
    Enrich the user's query with research findings.

    Args:
        original_query: The user's original question
        research_findings: Results from stage0_research_gather

    Returns:
        Enriched query string that includes research context
    """
    if not research_findings:
        return original_query

    # Build research context section
    research_context = []
    for finding in research_findings:
        category_name = finding['category'].replace('_', ' ').title()
        research_context.append(f"**{category_name}:**\n{finding['findings']}")

    research_text = "\n\n".join(research_context)

    # Construct enriched query
    enriched_query = f"""Original Question: {original_query}

---
RESEARCH CONTEXT (for your consideration when answering):

{research_text}
---

Please answer the original question above, taking into account the research context provided. The research is meant to enrich your analysis, but you should still form your own conclusions based on your knowledge and reasoning."""

    return enriched_query


def format_research_for_display(research_findings: List[Dict[str, Any]]) -> str:
    """
    Format research findings for user display.

    Args:
        research_findings: Results from stage0_research_gather

    Returns:
        Formatted markdown string for display
    """
    if not research_findings:
        return "No research findings available."

    sections = []
    for finding in research_findings:
        category_name = finding['category'].replace('_', ' ').title()
        sections.append(f"### {category_name}\n\n{finding['findings']}")

    return "\n\n".join(sections)
