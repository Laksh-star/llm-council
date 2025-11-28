# Research Layer Extension Guide

This guide explains how to use the new Stage 0 research preprocessing layer for film analysis.

## Overview

The research layer is an **optional preprocessing stage** that gathers specialized insights before the main council deliberation. It's designed for film analysis but can be adapted for other domains.

## Architecture

### Without Research (Standard 3-Stage)
```
User Query → Stage 1 (Responses) → Stage 2 (Rankings) → Stage 3 (Synthesis)
```

### With Research (4-Stage with Stage 0)
```
User Query → Stage 0 (Research) → Query Enrichment → Stage 1 (Responses) → Stage 2 (Rankings) → Stage 3 (Synthesis)
```

## How It Works

### Stage 0: Research Gathering
The system calls the research model (Claude Sonnet 4.5) three times in parallel with specialized prompts:

1. **Cultural Context**
   - Regional cinema conventions (e.g., Telugu cinema)
   - Cultural references and traditions
   - Historical industry context
   - Language-specific symbolism

2. **Narrative Structure**
   - Story frameworks (hero's journey, three-act structure)
   - Character arcs and archetypes
   - Dramatic elements and plot structure
   - Narrative techniques

3. **Philosophical Themes**
   - Indian philosophy (dharma, karma, maya, moksha)
   - Sanskrit terminology
   - Mythological parallels
   - Ethical and moral dimensions

### Query Enrichment
The research findings are injected into your original query as context, creating an "enriched query" that the council models receive.

## Usage

### Method 1: Via API

**Standard mode (no research):**
```bash
curl -X POST http://localhost:8001/api/conversations/{id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Analyze the film Baahubali",
    "enable_research": false
  }'
```

**Research mode (with Stage 0):**
```bash
curl -X POST http://localhost:8001/api/conversations/{id}/message \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Analyze the film Baahubali",
    "enable_research": true
  }'
```

### Method 2: Via Test Script

Run the included test script to compare both modes:

```bash
# Make sure you have your .env file with OPENROUTER_API_KEY
uv run python test_baahubali.py
```

This will:
1. Run the query WITHOUT research (standard mode)
2. Run the same query WITH research (research mode)
3. Generate comparison files:
   - `baahubali_without_research.json` - Full data (standard)
   - `baahubali_with_research.json` - Full data (research)
   - `baahubali_comparison.md` - Readable side-by-side comparison

### Method 3: Programmatically

```python
from backend.council import run_full_council

# Without research
stage0, stage1, stage2, stage3, metadata = await run_full_council(
    "Analyze the film Baahubali",
    enable_research=False
)

# With research
stage0, stage1, stage2, stage3, metadata = await run_full_council(
    "Analyze the film Baahubali",
    enable_research=True
)

# stage0 will be None when enable_research=False
# stage0 will contain research findings when enable_research=True
```

## Configuration

Edit [backend/config.py](backend/config.py) to customize:

```python
# Which model performs the research queries
RESEARCH_MODEL = "anthropic/claude-sonnet-4.5"
```

## Customizing Research Prompts

Edit [backend/research_layer.py](backend/research_layer.py) to modify the `RESEARCH_PROMPTS` dictionary:

```python
RESEARCH_PROMPTS = {
    "cultural_context": "Your custom prompt here...",
    "narrative_structure": "Your custom prompt here...",
    "philosophical_themes": "Your custom prompt here...",
    # Add new categories if needed
}
```

You can also select specific research categories:

```python
# Only gather cultural and narrative research
stage0, stage1, stage2, stage3, metadata = await run_full_council(
    "Analyze the film Baahubali",
    enable_research=True,
    research_categories=["cultural_context", "narrative_structure"]
)
```

## Example Output Structure

### With Research Enabled

```json
{
  "stage0": [
    {
      "category": "cultural_context",
      "prompt": "...",
      "findings": "Telugu cinema conventions include..."
    },
    {
      "category": "narrative_structure",
      "prompt": "...",
      "findings": "The hero's journey framework is evident..."
    },
    {
      "category": "philosophical_themes",
      "prompt": "...",
      "findings": "Dharma and karma are central themes..."
    }
  ],
  "stage1": [...],
  "stage2": [...],
  "stage3": {...},
  "metadata": {
    "research_enabled": true,
    "label_to_model": {...},
    "aggregate_rankings": [...]
  }
}
```

## Benefits

✅ **Deeper Analysis** - Council models receive cultural, narrative, and philosophical context
✅ **Transparent** - Stage 0 findings visible to user (not hidden preprocessing)
✅ **Flexible** - Enable/disable per query, choose specific research categories
✅ **Comparable** - Easy A/B testing with and without research
✅ **Non-invasive** - Original 3-stage system unchanged, research is optional preprocessing

## Performance Notes

- **3 extra API calls** when research is enabled (executed in parallel)
- Research queries run before Stage 1, adding ~10-30 seconds to total time
- All research calls happen in parallel to minimize latency
- Consider costs: 3 additional Claude Sonnet 4.5 calls per query

## Frontend Integration (TODO)

The backend is ready, but frontend needs updates to:

1. Add a checkbox/toggle for "Enable Research Layer"
2. Display Stage 0 findings in a separate tab
3. Handle streaming events: `stage0_start` and `stage0_complete`
4. Show research-enriched vs original query (for transparency)

See [CLAUDE.md](CLAUDE.md) for full architecture details.

## Test Case: Baahubali

The included test script analyzes "Baahubali: The Beginning" to compare how the research layer affects the depth of analysis. Look for differences in:

- Understanding of Telugu cinema context
- Recognition of mythological parallels (Mahabharata influence)
- Analysis of dharma and karma themes
- Discussion of character archetypes (Baahubali as ideal king)

Run `uv run python test_baahubali.py` to see the comparison.
