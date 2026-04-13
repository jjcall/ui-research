#!/usr/bin/env python3
"""Batch capture OG images and screenshots for design research gallery."""
import asyncio
import json
import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse

CACHE_DIR = Path.home() / ".cache" / "design-research" / "screenshots"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

URLS = [
    # Dribbble shots
    "https://dribbble.com/shots/24044559-AI-Chatbot-Interface-ChatGpt-Redesign",
    "https://dribbble.com/shots/25686873-AI-Chatbot-UI-Smart-Intuitive-Conversational-Design",
    "https://dribbble.com/shots/25992289-Nobi-AI-AI-Assistant-Dashboard",
    # Behance galleries
    "https://www.behance.net/gallery/169460271/ChatGPT-UIUX-Redesign-Case-Study",
    "https://www.behance.net/gallery/229153639/AI-Assistant-App-Full-UIUX-Case-Study-",
    "https://www.behance.net/gallery/237026811/Cortex-AI-Chatbot-SaaS-Platform",
    "https://www.behance.net/gallery/242682339/ChatVision-AI-Chat-Creator-Mobile-App",
    "https://www.behance.net/gallery/217888627/Ello-AI-Assistant-Mobile-App-UXUI-Design",
    # Mobbin screens/flows
    "https://mobbin.com/explore/screens/4d616906-d745-4ecb-9567-69be9e28b10a",
    "https://mobbin.com/explore/screens/2cae89fc-8f1d-45e2-8ee5-8f0252d949c1",
    "https://mobbin.com/explore/screens/a7287159-9ca1-4805-bccb-9bcd3c11f634",
    "https://mobbin.com/explore/flows/933e3742-9001-4116-972a-7e9b9a20af8b",
    "https://mobbin.com/explore/flows/7626da46-a288-433a-8f75-bfa387218d27",
    "https://mobbin.com/explore/flows/fc516ed9-ec8b-4ab8-bee5-e9da198a0992",
    "https://mobbin.com/explore/flows/fb0a7b5b-02e9-464b-b3de-3c49bc44bfb3",
    "https://mobbin.com/explore/flows/98e69d00-b9be-4e8c-a6b2-4a4ef85d9f76",
    # Figma Community files
    "https://www.figma.com/community/file/1373386017446585785/customizable-ai-chat-interface-ui-design-for-mobile-and-web-applications-free-download",
    "https://www.figma.com/community/file/1283418411426693463/ai-conversational-agent-chat-interface-ux-ui-kit-beta-2",
    "https://www.figma.com/community/file/1226866936281840601/chatgpt-ui-kit-ai-chat",
    "https://www.figma.com/community/file/1496647384826493443/figma-ui-kit-for-ai-agent-chat-apps-freemium-version",
    "https://www.figma.com/community/file/1546988096312619997/sundust-vibe-coding-ai-chatbot-ui-kit-free",
    "https://www.figma.com/community/file/1480293580970193440/sparkgpt-premium-ai-chatbot-ui-kit-like-chatgpt",
    "https://www.figma.com/community/file/1487281155452321751/chappy-ai-chat-bot-ui-kit-freebies",
    "https://www.figma.com/community/file/1251682862878798756/ai-smart-chat-ui-kit",
    # v0.dev
    "https://v0.dev/chat/community/ai-chat-interface-6VLiqkGu5vw",
    "https://v0.dev/chat/ai-chat-ui-5Q0PZQ4eFH0",
    "https://v0.dev/chat/chat-interface-design-xukRZfjWAIS",
    "https://v0.dev/chat/chatbot-ui-design-xAByUcnl0vP",
    "https://v0.dev/chat/8exklu5PQNz",
    "https://v0.dev/chat/vercel-chatbot-ui-SH4AEUt4glC",
    "https://v0.dev/chat/next-js-chatbot-ui-WzUi8fPWiRa",
    "https://v0.dev/t/0R5eEmfNCSx",
    "https://v0.dev/t/q1x9K1kwGrv",
    "https://v0.dev/t/SDODJZUNxhJ",
]

def url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]

def get_cache_path(url: str) -> Path:
    return CACHE_DIR / f"{url_hash(url)}.png"

async def capture_url(page, url: str, semaphore) -> dict:
    """Capture OG image or screenshot for a URL."""
    cached = get_cache_path(url)
    if cached.exists() and cached.stat().st_size > 1000:
        print(f"  [CACHE] {urlparse(url).netloc}")
        return {"url": url, "img": f"file://{cached}", "status": "cached"}

    async with semaphore:
        try:
            print(f"  [FETCH] {urlparse(url).netloc}...", end="", flush=True)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1.5)  # Let images load

            # Try OG image first
            og_img = await page.evaluate("""() => {
                const og = document.querySelector('meta[property="og:image"]');
                if (og && og.content) return og.content;
                const tw = document.querySelector('meta[name="twitter:image"]');
                if (tw && tw.content) return tw.content;
                return null;
            }""")

            if og_img and len(og_img) > 10:
                print(f" OG:{og_img[:60]}")
                return {"url": url, "img": og_img, "status": "og"}

            # Fallback: take screenshot
            await page.screenshot(path=str(cached), full_page=False)
            print(f" SCREENSHOT")
            return {"url": url, "img": f"file://{cached}", "status": "screenshot"}

        except Exception as e:
            print(f" FAILED: {str(e)[:50]}")
            return {"url": url, "img": None, "status": f"error: {str(e)[:80]}"}

async def main():
    from playwright.async_api import async_playwright

    print(f"Capturing {len(URLS)} URLs...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        semaphore = asyncio.Semaphore(5)  # 5 concurrent pages

        # Process in batches of 5
        for i in range(0, len(URLS), 5):
            batch = URLS[i:i+5]
            tasks = []
            for url in batch:
                page = await context.new_page()
                tasks.append(capture_url(page, url, semaphore))
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in batch_results:
                if isinstance(r, Exception):
                    results.append({"url": "unknown", "img": None, "status": f"error: {str(r)}"})
                else:
                    results.append(r)
            # Close pages
            for page in context.pages[1:]:  # Keep first page
                await page.close()

        await browser.close()

    # Output results
    output_path = Path(__file__).parent / "capture_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    success = sum(1 for r in results if r["img"])
    failed = sum(1 for r in results if not r["img"])
    print(f"\nDone: {success} captured, {failed} failed")
    print(f"Results: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
