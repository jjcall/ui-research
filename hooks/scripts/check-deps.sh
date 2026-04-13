#!/bin/bash
# Check dependencies for Design Research plugin
# Note: No required dependencies - all core functionality uses Python standard library

echo "Design Research Plugin — Dependency Check"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✓ Python3 available"
else
    echo "✗ Python3 not found — required"
    exit 1
fi

# Check for BeautifulSoup (optional, for better HTML parsing)
if python3 -c "from bs4 import BeautifulSoup" 2>/dev/null; then
    echo "✓ BeautifulSoup available — enhanced HTML parsing"
else
    echo "○ BeautifulSoup not installed — using regex fallback (works fine)"
fi

# Check if Playwright is available for Tier 0 screenshots
if python3 -c "import playwright" 2>/dev/null; then
    echo "✓ Playwright available — Tier 0 screenshots enabled"
else
    echo "○ Playwright not installed — Tier 0 screenshots unavailable"
fi

# Check research directory
RESEARCH_DIR="$HOME/Documents/UIResearch"
if [ -d "$RESEARCH_DIR" ]; then
    GALLERY_COUNT=$(ls -1 "$RESEARCH_DIR/galleries" 2>/dev/null | wc -l | tr -d ' ')
    echo "✓ Research directory: $RESEARCH_DIR ($GALLERY_COUNT galleries)"
else
    echo "○ Research directory will be created at: $RESEARCH_DIR"
fi

echo ""
echo "Ready to use — no pip install required!"
