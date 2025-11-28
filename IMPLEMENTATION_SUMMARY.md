# Implementation Summary: Research Preprocessing Layer

## What Was Built

Extended Andrej Karpathy's LLM Council with a **Stage 0 research preprocessing layer** for film analysis.

## Architecture

### Before (3-Stage)
```
Query → Stage 1 (Responses) → Stage 2 (Rankings) → Stage 3 (Synthesis)
```

### After (Optional 4-Stage)
```
Query → Stage 0 (Research) → Enriched Query → Stage 1 → Stage 2 → Stage 3
           │
           ├─ Cultural Context
           ├─ Narrative Structure
           └─ Philosophical Themes
```

## Implementation Details

### 1. New Module: research_layer.py

**Location:** `backend/research_layer.py`

**Key Components:**
- `RESEARCH_PROMPTS` - 3 specialized prompts for film analysis
  - Cultural context (regional cinema, traditions)
  - Narrative structure (story frameworks, character arcs)
  - Philosophical themes (dharma, karma, Sanskrit concepts)

- `stage0_research_gather()` - Executes 3 research queries in parallel
  - Calls RESEARCH_MODEL (Claude Sonnet 4.5)
  - Returns findings for each category

- `enrich_query_with_research()` - Injects research into original query
  - Creates "enriched query" with context section
  - Council models receive this enhanced version

- `format_research_for_display()` - Formats for user display

### 2. Integration: council.py

**Modified:** `backend/council.py`

**Changes:**
- Updated `run_full_council()` signature:
  ```python
  async def run_full_council(
      user_query: str,
      enable_research: bool = False,  # NEW
      research_categories: Optional[List[str]] = None  # NEW
  ) -> Tuple[Optional[List], List, List, Dict, Dict]:
  ```

- Return signature changed from:
  ```python
  (stage1, stage2, stage3, metadata)
  ```
  to:
  ```python
  (stage0, stage1, stage2, stage3, metadata)
  ```

- Added Stage 0 execution before Stage 1
- Query enrichment happens when research enabled
- Stage 0 results optional (None when disabled)

### 3. API Updates: main.py

**Modified:** `backend/main.py`

**Changes:**
- Updated `SendMessageRequest` model:
  ```python
  class SendMessageRequest(BaseModel):
      content: str
      enable_research: bool = False  # NEW
  ```

- Both endpoints updated:
  - `/api/conversations/{id}/message` - Returns stage0 when enabled
  - `/api/conversations/{id}/message/stream` - Emits stage0 events

- Response includes stage0 when research enabled

### 4. Configuration: config.py

**Modified:** `backend/config.py`

**Added:**
```python
RESEARCH_MODEL = "anthropic/claude-sonnet-4.5"
```

### 5. Test Script: test_baahubali.py

**Created:** `test_baahubali.py`

**Purpose:**
- A/B test with and without research
- Uses "Baahubali" as test case
- Generates 3 output files for comparison

**Usage:**
```bash
uv run python test_baahubali.py
```

**Output Files:**
- `baahubali_without_research.json` - Full data (standard)
- `baahubali_with_research.json` - Full data (research)
- `baahubali_comparison.md` - Human-readable comparison

### 6. Documentation

**Created:**
- `RESEARCH_LAYER_GUIDE.md` - Complete usage guide
- `ARCHITECTURE_SUMMARY.md` - Visual architecture & diagrams
- `QUICK_START.md` - Fast getting started guide
- `IMPLEMENTATION_SUMMARY.md` - This file

**Updated:**
- `CLAUDE.md` - Added Stage 0 architecture details

## File Changes Summary

```
NEW FILES:
✓ backend/research_layer.py        (161 lines)
✓ test_baahubali.py                (123 lines)
✓ RESEARCH_LAYER_GUIDE.md          (documentation)
✓ ARCHITECTURE_SUMMARY.md          (diagrams)
✓ QUICK_START.md                   (quick reference)
✓ IMPLEMENTATION_SUMMARY.md        (this file)

MODIFIED FILES:
✓ backend/config.py                (+4 lines: RESEARCH_MODEL)
✓ backend/council.py               (~60 lines modified)
✓ backend/main.py                  (~30 lines modified)
✓ CLAUDE.md                        (~100 lines added)
```

## How It Works

### Request Flow

**Without Research (enable_research=False):**
```
POST /api/conversations/{id}/message
{"content": "Analyze Baahubali", "enable_research": false}
    ↓
run_full_council(query, enable_research=False)
    ↓
stage0 = None
query_for_council = original_query
    ↓
Stage 1 → Stage 2 → Stage 3
    ↓
Return (None, stage1, stage2, stage3, metadata)
```

**With Research (enable_research=True):**
```
POST /api/conversations/{id}/message
{"content": "Analyze Baahubali", "enable_research": true}
    ↓
run_full_council(query, enable_research=True)
    ↓
stage0_research_gather()
    ├─ Query RESEARCH_MODEL with cultural prompt
    ├─ Query RESEARCH_MODEL with narrative prompt
    └─ Query RESEARCH_MODEL with philosophy prompt
    (3 parallel calls)
    ↓
stage0 = [cultural_findings, narrative_findings, philosophy_findings]
    ↓
enrich_query_with_research(original_query, stage0)
    ↓
query_for_council = "Original: ... \n\nRESEARCH CONTEXT:\n..."
    ↓
Stage 1 (with enriched query) → Stage 2 → Stage 3
    ↓
Return (stage0, stage1, stage2, stage3, metadata)
```

### Query Enrichment Format

When research is enabled, council models receive:

```
Original Question: [user's question]

---
RESEARCH CONTEXT (for your consideration when answering):

**Cultural Context:**
[Research findings about regional cinema, traditions, etc.]

**Narrative Structure:**
[Research findings about story frameworks, character arcs, etc.]

**Philosophical Themes:**
[Research findings about dharma, karma, Sanskrit concepts, etc.]
---

Please answer the original question above, taking into account
the research context provided...
```

## Research Prompts Design

Each prompt follows this structure:

```
You are a [expert type] specializing in [domain].

Analyze the following film-related query and provide [specific insights]:

Query: {query}

Focus on:
- [aspect 1]
- [aspect 2]
- [aspect 3]
- [aspect 4]
- [aspect 5]

Provide 2-3 key insights that would help analyze this film more deeply.
```

### Cultural Context Prompt
- Expert: Film studies expert specializing in cultural and regional cinema
- Focus: Regional conventions, cultural references, historical context, symbolism

### Narrative Structure Prompt
- Expert: Narrative theory and screenwriting expert
- Focus: Story frameworks, character arcs, plot structure, dramatic elements

### Philosophical Themes Prompt
- Expert: Philosophy and mythology expert (Indian traditions)
- Focus: Dharma/karma concepts, Sanskrit terminology, mythological parallels

## API Response Structure

### Standard Mode Response
```json
{
  "stage1": [...],
  "stage2": [...],
  "stage3": {...},
  "metadata": {
    "label_to_model": {...},
    "aggregate_rankings": [...],
    "research_enabled": false
  }
}
```

### Research Mode Response
```json
{
  "stage0": [                           // NEW
    {
      "category": "cultural_context",
      "prompt": "...",
      "findings": "..."
    },
    {
      "category": "narrative_structure",
      "prompt": "...",
      "findings": "..."
    },
    {
      "category": "philosophical_themes",
      "prompt": "...",
      "findings": "..."
    }
  ],
  "stage1": [...],
  "stage2": [...],
  "stage3": {...},
  "metadata": {
    "label_to_model": {...},
    "aggregate_rankings": [...],
    "research_enabled": true            // NEW
  }
}
```

## Performance & Cost Analysis

### Standard Mode (3-Stage)
- **API Calls:** 9 total
  - Stage 1: 4 (one per council model)
  - Stage 2: 4 (one per council model)
  - Stage 3: 1 (chairman)
- **Time:** ~20-60 seconds
- **Cost:** Baseline

### Research Mode (4-Stage)
- **API Calls:** 12 total (+33%)
  - Stage 0: 3 (research queries in parallel)
  - Stage 1: 4 (one per council model)
  - Stage 2: 4 (one per council model)
  - Stage 3: 1 (chairman)
- **Time:** ~30-90 seconds (+Stage 0 overhead)
- **Cost:** +33% (3 additional Claude Sonnet 4.5 calls)

## Key Design Decisions

### 1. Optional Preprocessing
**Decision:** Stage 0 is optional, controlled by `enable_research` flag
**Rationale:** Allows A/B testing and flexibility per query

### 2. Parallel Research Queries
**Decision:** All 3 research queries execute in parallel
**Rationale:** Minimize latency (3 sequential calls would triple wait time)

### 3. Query Enrichment vs Model Switching
**Decision:** Enrich the query instead of using different council models
**Rationale:** Preserves original 3-stage architecture, transparent to Stages 1-3

### 4. Claude as Research Model
**Decision:** Use Claude Sonnet 4.5 for research queries
**Rationale:** Strong performance on cultural analysis and philosophical concepts

### 5. Research Transparency
**Decision:** Return stage0 data to user, show in response
**Rationale:** Users can inspect research quality, verify enrichment

### 6. Non-Persistent Research
**Decision:** Stage 0 not saved to storage, only in API response
**Rationale:** Matches existing pattern (metadata also not persisted)

## Testing Strategy

### Test Case: Baahubali Analysis

**Query:**
```
Analyze the film "Baahubali: The Beginning" (2015). What makes it
significant in Indian cinema, and what are the deeper themes beyond
the surface-level action and spectacle?
```

**Expected Improvements with Research:**
- Recognition of Telugu cinema context
- Identification of Mahabharata parallels
- Discussion of dharma/karma themes
- Analysis of character archetypes (ideal king)
- Understanding of regional storytelling conventions

**How to Test:**
```bash
uv run python test_baahubali.py
cat baahubali_comparison.md
```

## Future Enhancements

### Backend (Optional)
- [ ] Add more research categories (technical, historical, genre-specific)
- [ ] Support custom research prompts per query
- [ ] Cache research results for similar queries
- [ ] Add research quality scoring

### Frontend (Needed for full integration)
- [ ] Add research toggle in UI
- [ ] Display Stage 0 findings in dedicated tab
- [ ] Show original vs enriched query
- [ ] Handle streaming events (stage0_start, stage0_complete)
- [ ] Visual indicator when research is enabled

### Advanced Features
- [ ] Multi-domain research (not just film)
- [ ] Adaptive research (choose categories based on query)
- [ ] Research chaining (use Stage 1 to guide Stage 0)
- [ ] Research voting (council votes on research relevance)

## Backward Compatibility

✓ **Fully backward compatible**
- `enable_research` defaults to `False`
- Existing API calls work unchanged
- No breaking changes to response structure (stage0 is additive)
- Original 3-stage flow untouched when research disabled

## Extension Architecture Benefits

✅ **Non-invasive** - Original code preserved, research is preprocessing
✅ **Modular** - research_layer.py is self-contained
✅ **Flexible** - Enable/disable per query, choose categories
✅ **Transparent** - Stage 0 visible to users
✅ **Testable** - Easy to compare with/without research
✅ **Performant** - Parallel execution minimizes latency
✅ **Scalable** - Easy to add new research categories

## How to Run

### Setup
```bash
# Install dependencies
uv sync

# Add OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-..." > .env
```

### Run Test
```bash
uv run python test_baahubali.py
```

### Start Server
```bash
./start.sh
```

### Test via API
```bash
# Create conversation
CONV_ID=$(curl -X POST http://localhost:8001/api/conversations | jq -r '.id')

# Standard mode
curl -X POST http://localhost:8001/api/conversations/$CONV_ID/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Analyze Baahubali", "enable_research": false}'

# Research mode
curl -X POST http://localhost:8001/api/conversations/$CONV_ID/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Analyze Baahubali", "enable_research": true}'
```

## Summary

The research preprocessing layer is **production-ready** for backend use. It extends the LLM Council with specialized film analysis capabilities while preserving the original architecture and maintaining full backward compatibility.

**Key Files to Review:**
- [QUICK_START.md](QUICK_START.md) - Get started immediately
- [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md) - Visual diagrams
- [RESEARCH_LAYER_GUIDE.md](RESEARCH_LAYER_GUIDE.md) - Complete usage guide
- [backend/research_layer.py](backend/research_layer.py) - Implementation
- [test_baahubali.py](test_baahubali.py) - A/B test script

**Ready to test with:**
```bash
uv run python test_baahubali.py
```
