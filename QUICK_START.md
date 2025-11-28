# Quick Start: Research Layer Extension

## What Was Added

Your LLM Council repo now has a **Stage 0 research preprocessing layer** for film analysis.

### New Files
- `backend/research_layer.py` - Stage 0 implementation
- `test_baahubali.py` - Comparison test script
- `RESEARCH_LAYER_GUIDE.md` - Full usage guide
- `ARCHITECTURE_SUMMARY.md` - Visual architecture
- `QUICK_START.md` - This file

### Modified Files
- `backend/config.py` - Added RESEARCH_MODEL
- `backend/council.py` - Added Stage 0 integration
- `backend/main.py` - Added enable_research parameter
- `CLAUDE.md` - Updated with architecture docs

## How Research Layer Works

```
WITHOUT RESEARCH (Standard 3-Stage):
User Query → Stage 1 (Responses) → Stage 2 (Rankings) → Stage 3 (Synthesis)

WITH RESEARCH (4-Stage):
User Query → Stage 0 (Research) → Enriched Query → Stage 1 → Stage 2 → Stage 3
                    ↓
            ┌───────┴────────┐
            │ Cultural       │
            │ Narrative      │  ← 3 specialized queries in parallel
            │ Philosophical  │
            └────────────────┘
```

## Test It Now

### Step 1: Setup (if not done)
```bash
# Install dependencies
uv sync

# Create .env file with your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env
```

### Step 2: Run Comparison Test
```bash
uv run python test_baahubali.py
```

This will:
1. Run Baahubali analysis **WITHOUT** research (standard mode)
2. Run Baahubali analysis **WITH** research (research mode)
3. Generate 3 comparison files:
   - `baahubali_without_research.json`
   - `baahubali_with_research.json`
   - `baahubali_comparison.md` ← **Read this one!**

### Step 3: Compare Results
```bash
# Read the human-friendly comparison
cat baahubali_comparison.md

# Or open in your editor
code baahubali_comparison.md
```

Look for differences in:
- Cultural understanding of Telugu cinema
- Recognition of mythological parallels
- Analysis of dharma/karma themes
- Depth of character archetype discussion

## How to Use in Your Code

### Python API
```python
from backend.council import run_full_council

# Standard mode (no research)
stage0, stage1, stage2, stage3, metadata = await run_full_council(
    "Analyze the film Baahubali",
    enable_research=False
)
# stage0 will be None

# Research mode (with Stage 0)
stage0, stage1, stage2, stage3, metadata = await run_full_council(
    "Analyze the film Baahubali",
    enable_research=True
)
# stage0 contains cultural, narrative, and philosophical research
```

### HTTP API
```bash
# Start the server
./start.sh

# Standard mode
curl -X POST http://localhost:8001/api/conversations/{id}/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Analyze Baahubali", "enable_research": false}'

# Research mode
curl -X POST http://localhost:8001/api/conversations/{id}/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Analyze Baahubali", "enable_research": true}'
```

## Configuration

Edit `backend/config.py`:

```python
# Which model does the research (3 parallel calls)
RESEARCH_MODEL = "anthropic/claude-sonnet-4.5"  # Current default

# Council members (answer the enriched query)
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]
```

## Customize Research Prompts

Edit `backend/research_layer.py` to modify the `RESEARCH_PROMPTS` dictionary:

```python
RESEARCH_PROMPTS = {
    "cultural_context": "Your prompt about cultural aspects...",
    "narrative_structure": "Your prompt about narrative...",
    "philosophical_themes": "Your prompt about philosophy...",
    # Add new categories as needed
}
```

## Cost & Performance

### Standard Mode (3-Stage)
- 9 API calls total
- ~20-60 seconds
- Lower cost

### Research Mode (4-Stage with Stage 0)
- 12 API calls total (+3 for research)
- ~30-90 seconds (+Stage 0 research time)
- ~33% more cost

## Architecture Diagram

See [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md) for full visual architecture.

Key files:
- **research_layer.py** - Stage 0 logic (new)
- **council.py** - Orchestration (modified to add Stage 0)
- **main.py** - API endpoints (modified to accept enable_research)
- **config.py** - Configuration (added RESEARCH_MODEL)

## Research Categories

The three default research categories for film analysis:

1. **Cultural Context**
   - Regional cinema conventions (Telugu, South Indian, etc.)
   - Cultural references, traditions, symbolism
   - Historical industry context
   - Audience expectations

2. **Narrative Structure**
   - Story frameworks (hero's journey, three-act, etc.)
   - Character arcs and archetypes
   - Dramatic elements and plot structure
   - Narrative techniques

3. **Philosophical Themes**
   - Indian philosophy (dharma, karma, maya, moksha)
   - Sanskrit concepts and terminology
   - Mythological parallels (Mahabharata, Ramayana)
   - Ethical and moral dimensions

## Next Steps

### Backend (Done ✓)
- [x] Create research_layer.py
- [x] Integrate with council.py
- [x] Update API endpoints
- [x] Add configuration
- [x] Create test script

### Frontend (TODO)
- [ ] Add research toggle checkbox in UI
- [ ] Create Stage0.jsx component to display research
- [ ] Handle streaming events (stage0_start, stage0_complete)
- [ ] Show original vs enriched query (transparency)

## Questions?

- Full guide: [RESEARCH_LAYER_GUIDE.md](RESEARCH_LAYER_GUIDE.md)
- Architecture: [ARCHITECTURE_SUMMARY.md](ARCHITECTURE_SUMMARY.md)
- Original docs: [CLAUDE.md](CLAUDE.md)
- Main README: [README.md](README.md)

## Quick Test

```bash
# Just run this:
uv run python test_baahubali.py

# Then read the comparison:
cat baahubali_comparison.md
```

That's it! The research layer is ready to use. 🎬
