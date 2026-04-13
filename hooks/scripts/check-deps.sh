#!/bin/bash
# Check dependencies for UI Research plugin

# Check if Playwright is available for Tier 0 screenshots
if command -v playwright &> /dev/null; then
    echo "✓ Playwright CLI available — Tier 0 screenshots enabled"
elif python3 -c "import playwright" 2>/dev/null; then
    echo "✓ Playwright Python package available — Tier 0 screenshots enabled"
else
    echo "ℹ Playwright not found — install with: pip install playwright && playwright install chromium"
    echo "  Without Playwright, screenshots will not be available (Tier 1 mode)"
fi

# Check for BeautifulSoup (optional, for better HTML parsing)
if python3 -c "from bs4 import BeautifulSoup" 2>/dev/null; then
    echo "✓ BeautifulSoup available — enhanced HTML parsing enabled"
else
    echo "ℹ BeautifulSoup not found — install with: pip install beautifulsoup4"
    echo "  Falling back to regex-based parsing"
fi

# Check research directory
RESEARCH_DIR="$HOME/Documents/UIResearch"
if [ -d "$RESEARCH_DIR" ]; then
    GALLERY_COUNT=$(ls -1 "$RESEARCH_DIR/galleries" 2>/dev/null | wc -l | tr -d ' ')
    echo "✓ Research directory exists: $RESEARCH_DIR ($GALLERY_COUNT galleries)"
else
    echo "ℹ Research directory will be created at: $RESEARCH_DIR"
fi
