# LLM Council + Research Layer Architecture

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER SUBMITS QUERY                             │
│                      "Analyze the film Baahubali"                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │  enable_research flag?   │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
            [FALSE]                          [TRUE]
                 │                               │
                 │                    ┌──────────▼──────────┐
                 │                    │   STAGE 0: RESEARCH  │
                 │                    │   (3 parallel calls) │
                 │                    └──────────┬──────────┘
                 │                               │
                 │                    ┌──────────▼──────────────────────┐
                 │                    │  Research Model (Claude 4.5)    │
                 │                    │  ┌────────────────────────────┐ │
                 │                    │  │ Cultural Context Query     │ │
                 │                    │  ├────────────────────────────┤ │
                 │                    │  │ Narrative Structure Query  │ │
                 │                    │  ├────────────────────────────┤ │
                 │                    │  │ Philosophical Themes Query │ │
                 │                    │  └────────────────────────────┘ │
                 │                    └──────────┬──────────────────────┘
                 │                               │
                 │                    ┌──────────▼──────────┐
                 │                    │  QUERY ENRICHMENT   │
                 │                    │  Inject research    │
                 │                    │  into original query│
                 │                    └──────────┬──────────┘
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                      ┌──────────▼──────────┐
                      │   STAGE 1: INITIAL   │
                      │   (Council models)   │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼────────────────────────┐
                      │ 4 Models Answer in Parallel       │
                      │ ┌───────────────────────────────┐ │
                      │ │ GPT 5.1      │ Gemini 3 Pro  │ │
                      │ │ Claude 4.5   │ Grok 4        │ │
                      │ └───────────────────────────────┘ │
                      └──────────┬────────────────────────┘
                                 │
                      ┌──────────▼──────────┐
                      │  STAGE 2: RANKINGS  │
                      │  (Anonymized review)│
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼────────────────────────┐
                      │ Anonymize: Response A, B, C, D    │
                      │ Each model ranks others' responses│
                      │ Calculate aggregate rankings      │
                      └──────────┬────────────────────────┘
                                 │
                      ┌──────────▼──────────┐
                      │  STAGE 3: SYNTHESIS │
                      │  (Chairman)         │
                      └──────────┬──────────┘
                                 │
                      ┌──────────▼────────────────────────┐
                      │ Chairman (Gemini 3 Pro)           │
                      │ Synthesizes final answer from:    │
                      │ - All Stage 1 responses           │
                      │ - All Stage 2 rankings            │
                      │ - Aggregate ranking results       │
                      └──────────┬────────────────────────┘
                                 │
                      ┌──────────▼──────────┐
                      │  RETURN TO USER     │
                      │  With all stages    │
                      └─────────────────────┘
```

## File Structure

```
backend/
├── config.py              # Model configuration (COUNCIL_MODELS, CHAIRMAN_MODEL, RESEARCH_MODEL)
├── openrouter.py          # OpenRouter API client (query_model, query_models_parallel)
├── research_layer.py      # NEW: Stage 0 research logic
│   ├── RESEARCH_PROMPTS   # Specialized prompts for film analysis
│   ├── stage0_research_gather()
│   ├── enrich_query_with_research()
│   └── format_research_for_display()
├── council.py             # MODIFIED: Main orchestration (added Stage 0 support)
│   ├── run_full_council(enable_research=False)  # NEW PARAMETER
│   ├── stage1_collect_responses()
│   ├── stage2_collect_rankings()
│   ├── stage3_synthesize_final()
│   └── calculate_aggregate_rankings()
├── main.py                # MODIFIED: FastAPI endpoints (added enable_research param)
│   └── POST /api/conversations/{id}/message
│       └── enable_research: bool = False  # NEW
└── storage.py             # Unchanged
```

## API Request/Response Flow

### Request (with research enabled)
```json
POST /api/conversations/{id}/message
{
  "content": "Analyze the film Baahubali",
  "enable_research": true
}
```

### Response Structure
```json
{
  "stage0": [                              // NEW: Only present if enable_research=true
    {
      "category": "cultural_context",
      "prompt": "...",
      "findings": "Telugu cinema conventions..."
    },
    {
      "category": "narrative_structure",
      "prompt": "...",
      "findings": "Hero's journey framework..."
    },
    {
      "category": "philosophical_themes",
      "prompt": "...",
      "findings": "Dharma and karma themes..."
    }
  ],
  "stage1": [
    {
      "model": "openai/gpt-5.1",
      "response": "..."
    },
    // ... 3 more models
  ],
  "stage2": [
    {
      "model": "openai/gpt-5.1",
      "ranking": "Response A provides...\n\nFINAL RANKING:\n1. Response C\n...",
      "parsed_ranking": ["Response C", "Response A", ...]
    },
    // ... 3 more models
  ],
  "stage3": {
    "model": "google/gemini-3-pro-preview",
    "response": "Based on the council's analysis..."
  },
  "metadata": {
    "label_to_model": {
      "Response A": "openai/gpt-5.1",
      "Response B": "google/gemini-3-pro-preview",
      "Response C": "anthropic/claude-sonnet-4.5",
      "Response D": "x-ai/grok-4"
    },
    "aggregate_rankings": [
      {
        "model": "anthropic/claude-sonnet-4.5",
        "average_rank": 1.5,
        "rankings_count": 4
      },
      // ... sorted by average_rank
    ],
    "research_enabled": true              // NEW
  }
}
```

## Key Integration Points

### 1. Backend: council.py
```python
async def run_full_council(
    user_query: str,
    enable_research: bool = False,
    research_categories: Optional[List[str]] = None
) -> Tuple[Optional[List], List, List, Dict, Dict]:
    # Stage 0 (optional)
    if enable_research:
        stage0_results = await stage0_research_gather(user_query, research_categories)
        query_for_council = enrich_query_with_research(user_query, stage0_results)
    else:
        stage0_results = None
        query_for_council = user_query

    # Stages 1-3 use query_for_council
    # ...
```

### 2. Backend: main.py
```python
class SendMessageRequest(BaseModel):
    content: str
    enable_research: bool = False  # NEW

# In endpoint:
stage0, stage1, stage2, stage3, metadata = await run_full_council(
    request.content,
    enable_research=request.enable_research
)
```

### 3. Backend: research_layer.py
```python
RESEARCH_PROMPTS = {
    "cultural_context": "...",
    "narrative_structure": "...",
    "philosophical_themes": "..."
}

async def stage0_research_gather(user_query, categories=None):
    # Call RESEARCH_MODEL with each prompt in parallel
    # Return findings
    pass

def enrich_query_with_research(original_query, research_findings):
    # Inject research context into query
    # Format: Original Question + Research Context + Instructions
    pass
```

## Comparison: With vs Without Research

### Standard Mode (3-Stage)
- **API Calls**: 4 (Stage 1) + 4 (Stage 2) + 1 (Stage 3) = **9 calls**
- **Cost**: Lower
- **Speed**: Faster
- **Depth**: Good, based on models' existing knowledge

### Research Mode (4-Stage with Stage 0)
- **API Calls**: 3 (Stage 0) + 4 (Stage 1) + 4 (Stage 2) + 1 (Stage 3) = **12 calls**
- **Cost**: +33% (3 additional calls)
- **Speed**: +10-30s (Stage 0 research time)
- **Depth**: Better, with specialized cultural/narrative/philosophical context

## Testing

```bash
# Run comparison test
uv run python test_baahubali.py

# Generates:
# - baahubali_without_research.json  (standard mode)
# - baahubali_with_research.json     (research mode)
# - baahubali_comparison.md          (side-by-side)
```

## Next Steps (Frontend Integration)

To fully integrate Stage 0 into the UI:

1. **Add research toggle** in ChatInterface.jsx
2. **Create Stage0.jsx** component to display research findings
3. **Update App.jsx** to handle stage0 data
4. **Handle streaming events** for stage0_start/stage0_complete
5. **Show research impact** - compare original vs enriched query

See [RESEARCH_LAYER_GUIDE.md](RESEARCH_LAYER_GUIDE.md) for usage details.
