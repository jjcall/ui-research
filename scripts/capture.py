#!/usr/bin/env python3
"""Playwright screenshot capture script for UI Research.

This script captures full-page screenshots of design reference URLs
using Playwright's headless Chromium browser.

Usage:
    python capture.py --input refs.json --output ./screenshots --width 1440
    python capture.py --url "https://dribbble.com/shots/123" --output shot.png

Input JSON format:
    [
        {
            "url": "https://dribbble.com/shots/...",
            "filename": "kanban_dribbble_1",
            "category": "kanban",
            "actions": [
                { "type": "dismiss_modal", "selector": "[data-dismiss]" },
                { "type": "scroll_to", "selector": ".feature-planning" }
            ]
        }
    ]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


DEFAULT_WIDTH = 1440
DEFAULT_HEIGHT = 900
TIMEOUT_MS = 15000
MAX_CONCURRENT = 4


async def capture_screenshot(
    page,
    url: str,
    output_path: Path,
    actions: list = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT
) -> dict:
    """
    Capture a screenshot of a URL.
    
    Returns a dict with status and any error message.
    """
    result = {
        "url": url,
        "output": str(output_path),
        "success": False,
        "error": None
    }
    
    try:
        # Navigate to URL
        await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)
        
        # Wait a bit for any animations
        await asyncio.sleep(0.5)
        
        # Execute pre-capture actions
        if actions:
            for action in actions:
                await execute_action(page, action)
        
        # Capture screenshot
        await page.screenshot(
            path=str(output_path),
            full_page=False,  # Viewport only
            type="png"
        )
        
        result["success"] = True
        
    except PlaywrightTimeout:
        result["error"] = "timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return result


async def execute_action(page, action: dict):
    """Execute a pre-capture action on the page."""
    action_type = action.get("type")
    selector = action.get("selector")
    
    if action_type == "dismiss_modal":
        try:
            element = page.locator(selector)
            if await element.count() > 0:
                await element.first.click()
                await asyncio.sleep(0.3)
        except Exception:
            pass  # Ignore if modal not found
    
    elif action_type == "scroll_to":
        try:
            element = page.locator(selector)
            if await element.count() > 0:
                await element.first.scroll_into_view_if_needed()
                await asyncio.sleep(0.3)
        except Exception:
            pass
    
    elif action_type == "wait":
        duration = action.get("duration", 1000)
        await asyncio.sleep(duration / 1000)
    
    elif action_type == "click":
        try:
            element = page.locator(selector)
            if await element.count() > 0:
                await element.first.click()
                await asyncio.sleep(0.3)
        except Exception:
            pass


async def capture_batch(
    refs: list,
    output_dir: Path,
    width: int = DEFAULT_WIDTH,
    max_concurrent: int = MAX_CONCURRENT
) -> list:
    """
    Capture screenshots for a batch of references.
    
    Uses a semaphore to limit concurrent captures.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def capture_with_semaphore(ref):
            async with semaphore:
                context = await browser.new_context(
                    viewport={"width": width, "height": DEFAULT_HEIGHT},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                )
                page = await context.new_page()
                
                filename = ref.get("filename", f"capture_{len(results)}")
                if not filename.endswith(".png"):
                    filename += ".png"
                output_path = output_dir / filename
                
                result = await capture_screenshot(
                    page,
                    ref["url"],
                    output_path,
                    actions=ref.get("actions", []),
                    width=width
                )
                result["filename"] = filename
                result["category"] = ref.get("category", "")
                
                await context.close()
                return result
        
        tasks = [capture_with_semaphore(ref) for ref in refs]
        results = await asyncio.gather(*tasks)
        
        await browser.close()
    
    return results


async def capture_single(
    url: str,
    output_path: Path,
    width: int = DEFAULT_WIDTH
) -> dict:
    """Capture a single URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": width, "height": DEFAULT_HEIGHT}
        )
        page = await context.new_page()
        
        result = await capture_screenshot(page, url, output_path, width=width)
        
        await browser.close()
    
    return result


def main():
    if not HAS_PLAYWRIGHT:
        print("Error: Playwright is not installed.", file=sys.stderr)
        print("Install with: pip install playwright && playwright install chromium")
        return 1
    
    parser = argparse.ArgumentParser(
        description="Capture screenshots of design reference URLs"
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Input JSON file with URLs to capture"
    )
    
    parser.add_argument(
        "--url",
        help="Single URL to capture"
    )
    
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory (for batch) or file path (for single URL)"
    )
    
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"Viewport width (default: {DEFAULT_WIDTH})"
    )
    
    parser.add_argument(
        "--concurrent", "-c",
        type=int,
        default=MAX_CONCURRENT,
        help=f"Max concurrent captures (default: {MAX_CONCURRENT})"
    )
    
    args = parser.parse_args()
    
    if args.url:
        # Single URL capture
        output_path = Path(args.output)
        if output_path.suffix != ".png":
            output_path = output_path.with_suffix(".png")
        
        print(f"Capturing: {args.url}")
        result = asyncio.run(capture_single(args.url, output_path, args.width))
        
        if result["success"]:
            print(f"Saved: {result['output']}")
            return 0
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1
    
    elif args.input:
        # Batch capture
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1
        
        with open(input_path, "r") as f:
            refs = json.load(f)
        
        output_dir = Path(args.output)
        
        print(f"Capturing {len(refs)} URLs to {output_dir}")
        results = asyncio.run(capture_batch(
            refs,
            output_dir,
            width=args.width,
            max_concurrent=args.concurrent
        ))
        
        # Write results
        results_path = output_dir / "results.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        success_count = sum(1 for r in results if r["success"])
        print(f"\nCompleted: {success_count}/{len(results)} successful")
        print(f"Results written to: {results_path}")
        
        return 0 if success_count == len(results) else 1
    
    else:
        parser.print_help()
        print("\nError: Either --url or --input is required", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
