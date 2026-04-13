#!/usr/bin/env python3
"""UI Research CLI — Generate design reference galleries.

Usage:
    python ui_research.py "planning mode UI"
    python ui_research.py --diagnose
    python ui_research.py --mock "kanban board"
    python ui_research.py --history
    python ui_research.py --rerun abc123
    python ui_research.py --setup          # Install Playwright
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
from lib.screenshots import (
    is_playwright_available,
    capture_screenshots_sync,
    get_cache_stats,
    clear_cache,
    HAS_PLAYWRIGHT
)


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
    env.playwright_available = HAS_PLAYWRIGHT and is_playwright_available()
    
    # Determine tier
    if env.playwright_available:
        env.detected_tier = 0
    else:
        env.detected_tier = 1  # CLI without screenshots
    
    # Get cache stats
    cache_stats = get_cache_stats() if HAS_PLAYWRIGHT else {}
    
    return {
        **env.to_dict(),
        "pythonVersion": sys.version,
        "platform": sys.platform,
        "researchDir": str(get_research_dir()),
        "hasHistory": get_history_path().exists(),
        "playwrightInstalled": HAS_PLAYWRIGHT,
        "screenshotCache": cache_stats
    }


def setup_playwright() -> int:
    """Install Playwright and browsers."""
    print("Setting up Playwright for screenshots...\n")
    
    # Check if playwright package is installed
    try:
        import playwright
        print("✓ playwright package already installed")
    except ImportError:
        print("Installing playwright package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"✗ Failed to install playwright: {result.stderr}")
            return 1
        print("✓ playwright package installed")
    
    # Install browsers
    print("\nInstalling Chromium browser...")
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=False  # Show progress
    )
    if result.returncode != 0:
        print("✗ Failed to install Chromium")
        return 1
    
    print("\n✓ Playwright setup complete!")
    print("\nYou can now capture full screenshots from:")
    print("  - Figma Community (bypasses 403)")
    print("  - Mobbin (handles JS rendering)")
    print("  - Any auth-walled or JS-rendered site")
    
    return 0


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


def open_urls_in_tabs(urls: list[str], delay_ms: int = 100) -> int:
    """
    Open multiple URLs in browser tabs.
    
    Args:
        urls: List of URLs to open
        delay_ms: Delay between opening tabs (prevents browser overwhelm)
    
    Returns:
        Number of tabs opened
    """
    import time
    
    opened = 0
    for url in urls:
        try:
            webbrowser.open_new_tab(url)
            opened += 1
            if delay_ms > 0 and opened < len(urls):
                time.sleep(delay_ms / 1000)
        except Exception as e:
            print(f"  Failed to open: {url} ({e})")
    
    return opened


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
  %(prog)s --open-tabs abc123        Open refs in browser tabs
  %(prog)s --open-tabs abc --limit 10  Open first 10 refs only
  %(prog)s --setup                   Install Playwright for screenshots
  %(prog)s --screenshot URL          Test screenshot capture
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
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Install Playwright and browsers for screenshot capture"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the screenshot cache"
    )
    
    parser.add_argument(
        "--screenshot",
        metavar="URL",
        help="Test screenshot capture for a single URL"
    )
    
    parser.add_argument(
        "--open-tabs",
        metavar="ID",
        help="Open all references from a previous research in browser tabs"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Limit number of tabs to open (default: 20)"
    )
    
    args = parser.parse_args()
    
    # Handle --diagnose
    if args.diagnose:
        print(json.dumps(diagnose_environment(), indent=2))
        return 0
    
    # Handle --setup
    if args.setup:
        return setup_playwright()
    
    # Handle --clear-cache
    if args.clear_cache:
        count = clear_cache()
        print(f"Cleared {count} cached screenshots")
        return 0
    
    # Handle --screenshot (test single URL)
    if args.screenshot:
        if not HAS_PLAYWRIGHT:
            print("Playwright not installed. Run: python ui_research.py --setup")
            return 1
        
        print(f"Capturing screenshot: {args.screenshot}")
        
        def progress(done, total, url):
            print(f"  Progress: {done}/{total}")
        
        results = capture_screenshots_sync(
            [args.screenshot],
            use_cache=False,
            progress_callback=progress
        )
        
        if results.get(args.screenshot):
            # Save to temp file and open
            import tempfile
            import base64
            
            data = results[args.screenshot]
            # Remove data URL prefix
            b64_data = data.split(",")[1]
            img_bytes = base64.b64decode(b64_data)
            
            temp_path = Path(tempfile.gettempdir()) / "uir-screenshot.png"
            with open(temp_path, "wb") as f:
                f.write(img_bytes)
            
            print(f"✓ Screenshot saved: {temp_path}")
            webbrowser.open(f"file://{temp_path}")
        else:
            print("✗ Screenshot capture failed")
            return 1
        
        return 0
    
    # Handle --history
    if args.history:
        print_history()
        return 0
    
    # Handle --open-tabs
    if args.open_tabs:
        research = find_research_by_id(args.open_tabs)
        if not research:
            print(f"Research '{args.open_tabs}' not found in history.")
            return 1
        
        gallery_path = Path(research["galleryPath"])
        if not gallery_path.exists():
            print(f"Gallery file not found: {gallery_path}")
            return 1
        
        # Load gallery and extract URLs
        with open(gallery_path, "r") as f:
            html = f.read()
        
        # Extract URLs from the gallery data
        import re
        data_match = re.search(r'/\*GALLERY_DATA\*/(.+?)/\*END_GALLERY_DATA\*/', html, re.DOTALL)
        if not data_match:
            print("Could not parse gallery data")
            return 1
        
        try:
            gallery_data = json.loads(data_match.group(1))
            urls = [ref["url"] for ref in gallery_data.get("refs", [])]
        except json.JSONDecodeError:
            print("Could not parse gallery JSON")
            return 1
        
        if not urls:
            print("No references found in gallery")
            return 1
        
        # Apply limit
        limit = min(args.limit, len(urls))
        urls_to_open = urls[:limit]
        
        if len(urls) > limit:
            print(f"Opening {limit} of {len(urls)} references (use --limit to change)")
        else:
            print(f"Opening {len(urls_to_open)} references...")
        
        opened = open_urls_in_tabs(urls_to_open)
        print(f"✓ Opened {opened} tabs")
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
