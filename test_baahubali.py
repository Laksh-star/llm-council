#!/usr/bin/env python3
"""
Test script for comparing LLM Council results with and without Stage 0 research layer.
Use case: Analyzing "Baahubali"
"""

import asyncio
import json
from backend.council import run_full_council


async def test_baahubali_analysis():
    """
    Compare council responses for Baahubali analysis with and without research layer.
    """
    # Test query about Baahubali
    query = """Analyze the film "Baahubali: The Beginning" (2015). What makes it significant
in Indian cinema, and what are the deeper themes beyond the surface-level action and spectacle?"""

    print("=" * 80)
    print("BAAHUBALI ANALYSIS TEST")
    print("=" * 80)
    print(f"\nQuery: {query}\n")
    print("=" * 80)

    # Test 1: WITHOUT research layer (standard 3-stage)
    print("\n[TEST 1] Running WITHOUT research layer (standard mode)...")
    print("-" * 80)

    stage0_without, stage1_without, stage2_without, stage3_without, metadata_without = \
        await run_full_council(query, enable_research=False)

    print("\n✓ Stage 1: Collected responses from council models")
    print(f"  - Number of responses: {len(stage1_without)}")

    print("\n✓ Stage 2: Collected rankings")
    print(f"  - Number of rankings: {len(stage2_without)}")

    print("\n✓ Stage 3: Chairman synthesis")
    print(f"  - Chairman model: {stage3_without['model']}")
    print(f"  - Response length: {len(stage3_without['response'])} chars")

    print("\n" + "=" * 80)

    # Test 2: WITH research layer (4-stage with Stage 0)
    print("\n[TEST 2] Running WITH research layer (research mode)...")
    print("-" * 80)

    stage0_with, stage1_with, stage2_with, stage3_with, metadata_with = \
        await run_full_council(query, enable_research=True)

    print("\n✓ Stage 0: Research gathering")
    if stage0_with:
        for research in stage0_with:
            category = research['category'].replace('_', ' ').title()
            print(f"  - {category}: {len(research['findings'])} chars")

    print("\n✓ Stage 1: Collected responses from council models (with enriched query)")
    print(f"  - Number of responses: {len(stage1_with)}")

    print("\n✓ Stage 2: Collected rankings")
    print(f"  - Number of rankings: {len(stage2_with)}")

    print("\n✓ Stage 3: Chairman synthesis")
    print(f"  - Chairman model: {stage3_with['model']}")
    print(f"  - Response length: {len(stage3_with['response'])} chars")

    print("\n" + "=" * 80)

    # Save results to files for detailed comparison
    print("\n[SAVING RESULTS]")
    print("-" * 80)

    # Save WITHOUT research
    result_without = {
        "mode": "standard_3stage",
        "query": query,
        "stage1": stage1_without,
        "stage2": stage2_without,
        "stage3": stage3_without,
        "metadata": metadata_without
    }

    with open("baahubali_without_research.json", "w") as f:
        json.dump(result_without, f, indent=2)
    print("✓ Saved: baahubali_without_research.json")

    # Save WITH research
    result_with = {
        "mode": "research_4stage",
        "query": query,
        "stage0": stage0_with,
        "stage1": stage1_with,
        "stage2": stage2_with,
        "stage3": stage3_with,
        "metadata": metadata_with
    }

    with open("baahubali_with_research.json", "w") as f:
        json.dump(result_with, f, indent=2)
    print("✓ Saved: baahubali_with_research.json")

    # Save readable comparison
    with open("baahubali_comparison.md", "w") as f:
        f.write("# Baahubali Analysis Comparison\n\n")
        f.write(f"**Query:** {query}\n\n")
        f.write("---\n\n")

        f.write("## Mode 1: Standard (3-Stage) - WITHOUT Research\n\n")
        f.write("### Final Answer (Stage 3)\n\n")
        f.write(stage3_without['response'])
        f.write("\n\n---\n\n")

        f.write("## Mode 2: Research-Enhanced (4-Stage) - WITH Stage 0\n\n")

        if stage0_with:
            f.write("### Stage 0: Research Findings\n\n")
            for research in stage0_with:
                category = research['category'].replace('_', ' ').title()
                f.write(f"#### {category}\n\n")
                f.write(research['findings'])
                f.write("\n\n")

        f.write("### Final Answer (Stage 3)\n\n")
        f.write(stage3_with['response'])
        f.write("\n\n---\n\n")

        f.write("## Comparison Notes\n\n")
        f.write("Compare the depth and cultural understanding between the two approaches.\n")
        f.write("Look for:\n")
        f.write("- Cultural context and regional cinema understanding\n")
        f.write("- Narrative structure analysis\n")
        f.write("- Philosophical themes (dharma, karma, etc.)\n")

    print("✓ Saved: baahubali_comparison.md")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nReview the generated files:")
    print("  1. baahubali_without_research.json - Full data (standard mode)")
    print("  2. baahubali_with_research.json - Full data (research mode)")
    print("  3. baahubali_comparison.md - Readable side-by-side comparison")
    print("\n")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_baahubali_analysis())
