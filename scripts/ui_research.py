#!/usr/bin/env python3
"""UI Research CLI — Generate design reference galleries.

Usage:
    python ui_research.py "planning mode UI"
    python ui_research.py --diagnose
    python ui_research.py --mock "kanban board"
    python ui_research.py --history
    python ui_research.py --rerun abc123
"""

import argparse
import json
import sys
import os
import uuid
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib import schema, decompose, search, images, render


def get_research_dir() -> Path:
    """Get the research output directory."""
    return Path.home() / "Documents" / "UIResearch"


def get_history_path() -> Path:
    """Get the path to history.json."""
    return get_research_dir() / "history.json"


def diagnose_environment() -> dict:
    """Check environment capabilities and return tier info."""
    env = schema.EnvironmentInfo()
    
    # Check for Playwright
    try:
        import playwright
        env.playwright_available = True
    except ImportError:
        try:
            result = subprocess.run(
                ["playwright", "--version"],
                capture_output=True, timeout=5
            )
            env.playwright_available = result.returncode == 0
        except Exception:
            env.playwright_available = False
    
    # Determine tier
    if env.playwright_available:
        env.detected_tier = 0
    else:
        env.detected_tier = 1  # CLI without screenshots
    
    return {
        **env.to_dict(),
        "pythonVersion": sys.version,
        "platform": sys.platform,
        "researchDir": str(get_research_dir()),
        "hasHistory": get_history_path().exists()
    }


def load_history() -> list[dict]:
    """Load research history."""
    history_path = get_history_path()
    if history_path.exists():
        with open(history_path, "r") as f:
            data = json.load(f)
            return data.get("researches", [])
    return []


def save_history(researches: list[dict]):
    """Save research history."""
    history_path = get_history_path()
    history_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(history_path, "w") as f:
        json.dump({"researches": researches}, f, indent=2)


def add_to_history(gallery: schema.Gallery, gallery_path: Path) -> str:
    """Add a research to history and return its ID."""
    research_id = str(uuid.uuid4())[:8]
    
    history = load_history()
    history.insert(0, schema.ResearchHistory(
        id=research_id,
        concept=gallery.concept,
        date=datetime.now().isoformat(),
        tier=gallery.tier,
        ref_count=len(gallery.refs),
        gallery_path=str(gallery_path),
        sub_patterns=[sp.name for sp in (gallery.decomposition.sub_patterns if gallery.decomposition else [])]
    ).to_dict())
    
    # Keep last 50 researches
    history = history[:50]
    save_history(history)
    
    return research_id


def print_history():
    """Print research history."""
    history = load_history()
    
    if not history:
        print("No research history found.")
        print(f"History will be saved to: {get_history_path()}")
        return
    
    print(f"\nUI Research History ({len(history)} entries)\n")
    print(f"{'ID':<10} {'Date':<12} {'Refs':<6} {'Concept':<40}")
    print("-" * 70)
    
    for h in history[:20]:
        date_str = h["date"][:10]
        concept = h["concept"][:38] + "..." if len(h["concept"]) > 38 else h["concept"]
        print(f"{h['id']:<10} {date_str:<12} {h['refCount']:<6} {concept:<40}")
    
    if len(history) > 20:
        print(f"\n... and {len(history) - 20} more")


def find_research_by_id(research_id: str) -> Optional[dict]:
    """Find a research by ID."""
    history = load_history()
    for h in history:
        if h["id"] == research_id or h["id"].startswith(research_id):
            return h
    return None


def open_gallery(research_id: str):
    """Open a previous gallery by ID."""
    research = find_research_by_id(research_id)
    if not research:
        print(f"Research '{research_id}' not found in history.")
        sys.exit(1)
    
    gallery_path = Path(research["galleryPath"])
    if not gallery_path.exists():
        print(f"Gallery file not found: {gallery_path}")
        sys.exit(1)
    
    print(f"Opening: {gallery_path}")
    webbrowser.open(f"file://{gallery_path}")


def run_mock_research(concept: str) -> schema.Gallery:
    """Run research with mock data (no network calls)."""
    # Load mock data if available
    mock_path = Path(__file__).parent.parent / "fixtures" / "mock_search.json"
    
    # Create sample sub-patterns
    sub_patterns_data = [
        {
            "name": "Primary Pattern",
            "description": f"Main implementation of {concept}",
            "base_terms": [concept.lower()],
            "tags": ["general"]
        },
        {
            "name": "Secondary Pattern",
            "description": f"Alternative approach to {concept}",
            "base_terms": [concept.lower().split()[0] if " " in concept else concept.lower()],
            "tags": ["alternative"]
        }
    ]
    
    decomposition = decompose.decompose_concept(concept, sub_patterns_data)
    
    # Create mock references
    refs = []
    for i, sp in enumerate(decomposition.sub_patterns):
        refs.append(schema.Reference(
            url=f"https://dribbble.com/shots/mock-{i}",
            title=f"Mock {sp.name} Design",
            description=f"Sample design for {sp.name.lower()}",
            source="dribbble",
            source_label="Dribbble",
            category=sp.name.lower().replace(" ", "-"),
            tags=sp.tags
        ))
        refs.append(schema.Reference(
            url=f"https://mobbin.com/apps/mock-{i}",
            title=f"Mock {sp.name} App",
            description=f"Real app implementation of {sp.name.lower()}",
            source="mobbin",
            source_label="Mobbin",
            category=sp.name.lower().replace(" ", "-"),
            tags=sp.tags
        ))
    
    # Build categories from decomposition
    categories = [
        schema.Category(
            id=sp.name.lower().replace(" ", "-"),
            label=sp.name
        )
        for sp in decomposition.sub_patterns
    ]
    
    # Get sources from refs
    source_ids = set(r.source for r in refs)
    sources = [search.get_source_info(sid) for sid in source_ids]
    sources = [
        schema.Source(id=s.get("id", "unknown"), label=s.get("label", "Unknown"), color=s.get("color", "#666"))
        for s in sources if s
    ]
    
    gallery = schema.Gallery(
        concept=concept,
        categories=categories,
        sources=sources,
        refs=refs,
        tier=1,
        decomposition=decomposition
    )
    gallery.update_counts()
    
    return gallery


def main():
    parser = argparse.ArgumentParser(
        description="Research UI/UX patterns and generate visual galleries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "planning mode UI"        Research a concept
  %(prog)s --diagnose                Check environment
  %(prog)s --mock "kanban board"     Use mock data (testing)
  %(prog)s --history                 Show research history
  %(prog)s --rerun abc123            Re-run previous research
  %(prog)s --open abc123             Open previous gallery
"""
    )
    
    parser.add_argument(
        "concept",
        nargs="?",
        help="UI concept to research (e.g., 'planning mode UI', 'kanban board')"
    )
    
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Check environment and display tier info as JSON"
    )
    
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data instead of real searches (for testing)"
    )
    
    parser.add_argument(
        "--tier",
        type=int,
        choices=[0, 1, 2, 3],
        help="Force a specific tier (0=Playwright, 1=Links, 2=OG images, 3=Chrome)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: ~/Documents/UIResearch/galleries/)"
    )
    
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show research history"
    )
    
    parser.add_argument(
        "--rerun",
        metavar="ID",
        help="Re-run a previous research by ID"
    )
    
    parser.add_argument(
        "--open",
        metavar="ID",
        help="Open a previous gallery by ID"
    )
    
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't open the gallery after generation"
    )
    
    args = parser.parse_args()
    
    # Handle --diagnose
    if args.diagnose:
        print(json.dumps(diagnose_environment(), indent=2))
        return 0
    
    # Handle --history
    if args.history:
        print_history()
        return 0
    
    # Handle --open
    if args.open:
        open_gallery(args.open)
        return 0
    
    # Handle --rerun
    if args.rerun:
        research = find_research_by_id(args.rerun)
        if not research:
            print(f"Research '{args.rerun}' not found in history.")
            return 1
        args.concept = research["concept"]
        print(f"Re-running research: {args.concept}")
    
    # Require concept for research
    if not args.concept:
        parser.print_help()
        print("\nError: concept is required for research", file=sys.stderr)
        return 1
    
    # Run research
    print(f"\nResearching: {args.concept}\n")
    
    if args.mock:
        print("Using mock data (--mock flag)")
        gallery = run_mock_research(args.concept)
    else:
        # Real research would involve Claude/web searches
        # For now, use mock as a fallback
        print("Note: Full research requires Claude integration.")
        print("Using sample decomposition...\n")
        gallery = run_mock_research(args.concept)
    
    # Generate output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = render.get_default_output_path(args.concept)
    
    # Save gallery
    render.save_gallery(gallery, output_path)
    print(f"Gallery saved: {output_path}")
    
    # Add to history
    research_id = add_to_history(gallery, output_path)
    print(f"Research ID: {research_id}")
    
    # Open in browser
    if not args.no_open:
        print("Opening in browser...")
        webbrowser.open(f"file://{output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
