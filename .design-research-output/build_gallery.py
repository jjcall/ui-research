#!/usr/bin/env python3
"""Build gallery HTML from template + captured data."""
import json
from pathlib import Path
from datetime import datetime

TEMPLATE = Path(__file__).parent.parent / "data" / "gallery-template.html"
CAPTURES = Path(__file__).parent / "capture_results.json"
OUTPUT = Path(__file__).parent / "2026-04-12-ai-chat-interfaces.html"

# Load captures into a URL -> img map
with open(CAPTURES) as f:
    captures = json.load(f)
img_map = {c["url"]: c["img"] for c in captures if c.get("img")}

# Filter out generic Mobbin OG placeholder
MOBBIN_GENERIC = "https://mobbin.com/og_image.png?v=4.0"
for url, img in list(img_map.items()):
    if img == MOBBIN_GENERIC:
        img_map[url] = None

data = {
    "concept": "AI Chat Interfaces",
    "categories": [
        {"id": "all", "label": "All", "count": 55},
        {"id": "chat-layout", "label": "Chat Message Layout", "count": 10},
        {"id": "real-apps", "label": "Real App Flows", "count": 8},
        {"id": "code-components", "label": "Code Components", "count": 12},
        {"id": "figma-kits", "label": "Figma UI Kits", "count": 10},
        {"id": "ux-patterns", "label": "UX Patterns & Analysis", "count": 10},
        {"id": "model-canvas", "label": "Model Selector & Canvas", "count": 5},
    ],
    "sources": [
        {"id": "all", "label": "All", "color": "#78716c", "count": 55},
        {"id": "dribbble", "label": "Dribbble", "color": "#ea4c89", "count": 3},
        {"id": "behance", "label": "Behance", "color": "#1769ff", "count": 5},
        {"id": "mobbin", "label": "Mobbin", "color": "#000000", "count": 8},
        {"id": "figma", "label": "Figma", "color": "#f24e1e", "count": 8},
        {"id": "v0", "label": "v0.dev", "color": "#18181b", "count": 10},
        {"id": "articles", "label": "Articles", "color": "#6366f1", "count": 15},
        {"id": "tools", "label": "Tools & Libs", "color": "#10b981", "count": 6},
    ],
    "refs": [
        # === Chat Message Layout ===
        {
            "url": "https://dribbble.com/shots/24044559-AI-Chatbot-Interface-ChatGpt-Redesign",
            "title": "AI Chatbot Interface - ChatGPT Redesign",
            "desc": "Sleek folders system to organize and navigate through conversations",
            "source": "dribbble", "sourceLabel": "Dribbble",
            "cat": "chat-layout", "tags": ["chatgpt", "redesign", "conversation"],
            "img": img_map.get("https://dribbble.com/shots/24044559-AI-Chatbot-Interface-ChatGpt-Redesign"),
            "urlQuality": 1.0
        },
        {
            "url": "https://dribbble.com/shots/25686873-AI-Chatbot-UI-Smart-Intuitive-Conversational-Design",
            "title": "AI Chatbot UI - Smart Conversational Design",
            "desc": "Smart and intuitive conversational interface with clean message bubbles",
            "source": "dribbble", "sourceLabel": "Dribbble",
            "cat": "chat-layout", "tags": ["chatbot", "conversational", "clean"],
            "img": img_map.get("https://dribbble.com/shots/25686873-AI-Chatbot-UI-Smart-Intuitive-Conversational-Design"),
            "urlQuality": 1.0
        },
        {
            "url": "https://dribbble.com/shots/25992289-Nobi-AI-AI-Assistant-Dashboard",
            "title": "Nobi AI - AI Assistant Dashboard",
            "desc": "Intelligent chat dashboard with instant access to chat, image, video, and code tools",
            "source": "dribbble", "sourceLabel": "Dribbble",
            "cat": "chat-layout", "tags": ["dashboard", "multi-tool", "ai-assistant"],
            "img": img_map.get("https://dribbble.com/shots/25992289-Nobi-AI-AI-Assistant-Dashboard"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.behance.net/gallery/169460271/ChatGPT-UIUX-Redesign-Case-Study",
            "title": "ChatGPT UI/UX Redesign Case Study",
            "desc": "Redesigned answer generation and sharing flow for ChatGPT web interface",
            "source": "behance", "sourceLabel": "Behance",
            "cat": "chat-layout", "tags": ["chatgpt", "case-study", "redesign"],
            "img": img_map.get("https://www.behance.net/gallery/169460271/ChatGPT-UIUX-Redesign-Case-Study"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.behance.net/gallery/229153639/AI-Assistant-App-Full-UIUX-Case-Study-",
            "title": "AI Assistant App - Full UI/UX Case Study",
            "desc": "AI-powered mobile assistant for focus, routine, and clarity — minimal dark-mode style",
            "source": "behance", "sourceLabel": "Behance",
            "cat": "chat-layout", "tags": ["mobile", "dark-mode", "assistant", "case-study"],
            "img": img_map.get("https://www.behance.net/gallery/229153639/AI-Assistant-App-Full-UIUX-Case-Study-"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.behance.net/gallery/237026811/Cortex-AI-Chatbot-SaaS-Platform",
            "title": "Cortex - AI Chatbot SaaS Platform",
            "desc": "SaaS chatbot platform with landing page and web UI/UX design",
            "source": "behance", "sourceLabel": "Behance",
            "cat": "chat-layout", "tags": ["saas", "platform", "landing-page"],
            "img": img_map.get("https://www.behance.net/gallery/237026811/Cortex-AI-Chatbot-SaaS-Platform"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.behance.net/gallery/242682339/ChatVision-AI-Chat-Creator-Mobile-App",
            "title": "ChatVision - AI Chat & Creator Mobile App",
            "desc": "All-in-one AI app for chat, image generation, and music creation",
            "source": "behance", "sourceLabel": "Behance",
            "cat": "chat-layout", "tags": ["mobile", "multimodal", "creator"],
            "img": img_map.get("https://www.behance.net/gallery/242682339/ChatVision-AI-Chat-Creator-Mobile-App"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.behance.net/gallery/217888627/Ello-AI-Assistant-Mobile-App-UXUI-Design",
            "title": "Ello AI Assistant - Mobile App UX/UI",
            "desc": "AI assistant mobile app with voice assistant and animation design",
            "source": "behance", "sourceLabel": "Behance",
            "cat": "chat-layout", "tags": ["mobile", "voice", "animation"],
            "img": img_map.get("https://www.behance.net/gallery/217888627/Ello-AI-Assistant-Mobile-App-UXUI-Design"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.eleken.co/blog-posts/chatbot-ui-examples",
            "title": "31 Chatbot UI Examples from Product Designers",
            "desc": "Curated collection of real chatbot interfaces with design analysis",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "chat-layout", "tags": ["examples", "analysis", "collection"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://arounda.agency/blog/chatbot-ui-examples",
            "title": "40 Chatbot UI Examples from Designers",
            "desc": "Extensive gallery of chatbot designs with commentary on design decisions",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "chat-layout", "tags": ["examples", "gallery", "analysis"],
            "img": None, "urlQuality": 0.5
        },

        # === Real App Flows ===
        {
            "url": "https://mobbin.com/explore/screens/4d616906-d745-4ecb-9567-69be9e28b10a",
            "title": "Mistral AI - Web Chat Interface",
            "desc": "Chat list sidebar with conversation area — production web app",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["mistral", "web", "sidebar", "chat"],
            "img": img_map.get("https://mobbin.com/explore/screens/4d616906-d745-4ecb-9567-69be9e28b10a"),
            "urlQuality": 1.0
        },
        {
            "url": "https://mobbin.com/explore/screens/2cae89fc-8f1d-45e2-8ee5-8f0252d949c1",
            "title": "Bing iOS - AI Chat Interface",
            "desc": "Suggested questions and conversation style selector for Copilot chat",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["bing", "copilot", "ios", "suggestions"],
            "img": img_map.get("https://mobbin.com/explore/screens/2cae89fc-8f1d-45e2-8ee5-8f0252d949c1"),
            "urlQuality": 1.0
        },
        {
            "url": "https://mobbin.com/explore/screens/a7287159-9ca1-4805-bccb-9bcd3c11f634",
            "title": "WhatsApp - Meta AI Chat",
            "desc": "Meta AI integrated into WhatsApp messaging with inline responses",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["whatsapp", "meta-ai", "android", "inline"],
            "img": img_map.get("https://mobbin.com/explore/screens/a7287159-9ca1-4805-bccb-9bcd3c11f634"),
            "urlQuality": 1.0
        },
        {
            "url": "https://mobbin.com/explore/flows/933e3742-9001-4116-972a-7e9b9a20af8b",
            "title": "Fiverr Web - Chatting with AI Flow",
            "desc": "AI suggests freelancers based on user queries and clarifications",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["fiverr", "web", "marketplace", "flow"],
            "img": None, "urlQuality": 1.0
        },
        {
            "url": "https://mobbin.com/explore/flows/7626da46-a288-433a-8f75-bfa387218d27",
            "title": "Brave Browser - Leo AI Chat Flow",
            "desc": "Built-in AI assistant with privacy notice and prompt interaction",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["brave", "leo", "privacy", "browser"],
            "img": None, "urlQuality": 1.0
        },
        {
            "url": "https://mobbin.com/explore/flows/fc516ed9-ec8b-4ab8-bee5-e9da198a0992",
            "title": "Tiimo iOS - Chatting with AI Flow",
            "desc": "AI-powered productivity app with conversational task management",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["tiimo", "ios", "productivity", "flow"],
            "img": None, "urlQuality": 1.0
        },
        {
            "url": "https://mobbin.com/explore/flows/fb0a7b5b-02e9-464b-b3de-3c49bc44bfb3",
            "title": "Trust Wallet - Crypto Buddy AI Flow",
            "desc": "AI assistant for crypto analysis with prompt-based interaction",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["trust-wallet", "crypto", "finance", "flow"],
            "img": None, "urlQuality": 1.0
        },
        {
            "url": "https://mobbin.com/explore/flows/98e69d00-b9be-4e8c-a6b2-4a4ef85d9f76",
            "title": "Notion Web - Notion AI Flow",
            "desc": "AI search and query interface integrated into Notion workspace",
            "source": "mobbin", "sourceLabel": "Mobbin",
            "cat": "real-apps", "tags": ["notion", "web", "workspace", "search"],
            "img": None, "urlQuality": 1.0
        },

        # === Code Components (v0.dev) ===
        {
            "url": "https://v0.dev/chat/community/ai-chat-interface-6VLiqkGu5vw",
            "title": "AI Chat Interface (9.6K forks)",
            "desc": "Most popular AI chat template — shadcn/ui with streaming support",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["shadcn", "popular", "streaming", "react"],
            "img": img_map.get("https://v0.dev/chat/community/ai-chat-interface-6VLiqkGu5vw"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/chat/ai-chat-ui-5Q0PZQ4eFH0",
            "title": "AI Chat UI",
            "desc": "Clean AI chat interface with message history and input composer",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["chat-ui", "clean", "react"],
            "img": img_map.get("https://v0.dev/chat/ai-chat-ui-5Q0PZQ4eFH0"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/chat/chat-interface-design-xukRZfjWAIS",
            "title": "Chat Interface Design (GPT-4 + AI SDK)",
            "desc": "Full chat implementation with API route and useChat hook",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["ai-sdk", "gpt-4", "full-stack"],
            "img": img_map.get("https://v0.dev/chat/chat-interface-design-xukRZfjWAIS"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/chat/chatbot-ui-design-xAByUcnl0vP",
            "title": "Chatbot UI Design (Split-Screen)",
            "desc": "Left panel chat UI + right panel dynamic content display",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["split-view", "dual-pane", "canvas"],
            "img": img_map.get("https://v0.dev/chat/chatbot-ui-design-xAByUcnl0vP"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/chat/8exklu5PQNz",
            "title": "React Chatbot Interface (Streaming)",
            "desc": "Real-time message streaming with AI SDK useChat hook",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["streaming", "react", "ai-sdk"],
            "img": img_map.get("https://v0.dev/chat/8exklu5PQNz"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/chat/vercel-chatbot-ui-SH4AEUt4glC",
            "title": "Vercel Chatbot UI",
            "desc": "Official Vercel-style chatbot with minimal design",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["vercel", "minimal", "official"],
            "img": img_map.get("https://v0.dev/chat/vercel-chatbot-ui-SH4AEUt4glC"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/chat/next-js-chatbot-ui-WzUi8fPWiRa",
            "title": "Next.js Chatbot UI",
            "desc": "Card-based chatbot with progress tracking and question flow",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["nextjs", "card", "progress"],
            "img": img_map.get("https://v0.dev/chat/next-js-chatbot-ui-WzUi8fPWiRa"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/t/0R5eEmfNCSx",
            "title": "Chatbot UI with Audio, Files & Sidebar",
            "desc": "Full-featured chat with audio input, file attachments, and history sidebar",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["audio", "files", "sidebar", "full-featured"],
            "img": img_map.get("https://v0.dev/t/0R5eEmfNCSx"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/t/q1x9K1kwGrv",
            "title": "AI Chat Interface (shadcn/ui + Clipboard)",
            "desc": "Chat component with clipboard integration and shadcn/ui styling",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["shadcn", "clipboard", "component"],
            "img": img_map.get("https://v0.dev/t/q1x9K1kwGrv"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://v0.dev/t/SDODJZUNxhJ",
            "title": "BI Tool Powered by AI Chatbot",
            "desc": "Business intelligence dashboard with conversational AI interface",
            "source": "v0", "sourceLabel": "v0.dev",
            "cat": "code-components", "tags": ["bi", "dashboard", "analytics", "enterprise"],
            "img": img_map.get("https://v0.dev/t/SDODJZUNxhJ"),
            "urlQuality": 1.0, "hasCode": True
        },
        {
            "url": "https://dev.to/alexander_lukashov/i-evaluated-every-ai-chat-ui-library-in-2026-heres-what-i-found-and-what-i-built-4p10",
            "title": "Every AI Chat UI Library Evaluated (2026)",
            "desc": "Comprehensive comparison of chat UI libraries — assistant-ui, chatscope, stream-chat",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "code-components", "tags": ["libraries", "comparison", "2026"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.assistant-ui.com/",
            "title": "assistant-ui - React AI Chat Components",
            "desc": "Open-source React components for building AI chat interfaces",
            "source": "tools", "sourceLabel": "Tools & Libs",
            "cat": "code-components", "tags": ["react", "open-source", "library"],
            "img": None, "urlQuality": 0.5
        },

        # === Figma UI Kits ===
        {
            "url": "https://www.figma.com/community/file/1373386017446585785/customizable-ai-chat-interface-ui-design-for-mobile-and-web-applications-free-download",
            "title": "Customizable AI Chat Interface (Mobile + Web)",
            "desc": "Free download — tailored for mobile and web applications",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["free", "mobile", "web", "customizable"],
            "img": img_map.get("https://www.figma.com/community/file/1373386017446585785/customizable-ai-chat-interface-ui-design-for-mobile-and-web-applications-free-download"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.figma.com/community/file/1283418411426693463/ai-conversational-agent-chat-interface-ux-ui-kit-beta-2",
            "title": "AI Conversational Agent UX/UI Kit (Beta 2)",
            "desc": "Comprehensive kit for building AI agent chat interfaces",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["agent", "comprehensive", "kit"],
            "img": img_map.get("https://www.figma.com/community/file/1283418411426693463/ai-conversational-agent-chat-interface-ux-ui-kit-beta-2"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.figma.com/community/file/1226866936281840601/chatgpt-ui-kit-ai-chat",
            "title": "ChatGPT UI Kit - SnowUI",
            "desc": "Design system supporting desktop, tablet and mobile with multi-terminal responses",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["chatgpt", "design-system", "responsive"],
            "img": img_map.get("https://www.figma.com/community/file/1226866936281840601/chatgpt-ui-kit-ai-chat"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.figma.com/community/file/1496647384826493443/figma-ui-kit-for-ai-agent-chat-apps-freemium-version",
            "title": "AI Agent Chat Apps UI Kit (Freemium)",
            "desc": "Modern AI chat kit for founders and startups — 2 free dashboard screens",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["agent", "freemium", "startup"],
            "img": img_map.get("https://www.figma.com/community/file/1496647384826493443/figma-ui-kit-for-ai-agent-chat-apps-freemium-version"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.figma.com/community/file/1546988096312619997/sundust-vibe-coding-ai-chatbot-ui-kit-free",
            "title": "Sundust - Vibe-coding AI Chatbot Kit (Free)",
            "desc": "Modern kit crafted for vibe-coding chatbot products",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["vibe-coding", "modern", "free"],
            "img": img_map.get("https://www.figma.com/community/file/1546988096312619997/sundust-vibe-coding-ai-chatbot-ui-kit-free"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.figma.com/community/file/1480293580970193440/sparkgpt-premium-ai-chatbot-ui-kit-like-chatgpt",
            "title": "SparkGPT - Premium AI Chatbot UI Kit",
            "desc": "Premium kit for building next-gen AI chatbot applications",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["premium", "chatgpt-style", "next-gen"],
            "img": img_map.get("https://www.figma.com/community/file/1480293580970193440/sparkgpt-premium-ai-chatbot-ui-kit-like-chatgpt"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.figma.com/community/file/1487281155452321751/chappy-ai-chat-bot-ui-kit-freebies",
            "title": "Chappy - AI Chat Bot UI Kit (Free)",
            "desc": "Modern and minimalist design with high-quality screens",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["minimalist", "free", "high-quality"],
            "img": img_map.get("https://www.figma.com/community/file/1487281155452321751/chappy-ai-chat-bot-ui-kit-freebies"),
            "urlQuality": 1.0
        },
        {
            "url": "https://www.figma.com/community/file/1251682862878798756/ai-smart-chat-ui-kit",
            "title": "AI Smart Chat UI Kit",
            "desc": "AI-powered solutions focused chatbot UI kit",
            "source": "figma", "sourceLabel": "Figma",
            "cat": "figma-kits", "tags": ["smart", "ai-powered", "kit"],
            "img": img_map.get("https://www.figma.com/community/file/1251682862878798756/ai-smart-chat-ui-kit"),
            "urlQuality": 1.0
        },
        {
            "url": "https://thefrontkit.com/blogs/best-ai-chat-ui-kits-2026",
            "title": "Best AI Chat UI Kits 2026: 7 Compared",
            "desc": "Side-by-side comparison of top AI chat UI kits and templates",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "figma-kits", "tags": ["comparison", "2026", "kits"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.jotform.com/ai/agents/best-chatbot-ui/",
            "title": "20 Best Looking Chatbot UIs in 2026",
            "desc": "From playful bots like Cleo to enterprise tools like Zendesk and Otter.ai",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "figma-kits", "tags": ["best-of", "2026", "roundup"],
            "img": None, "urlQuality": 0.5
        },

        # === UX Patterns & Analysis ===
        {
            "url": "https://www.nngroup.com/articles/perplexity-henry-modisett/",
            "title": "UX of AI: Lessons from Perplexity (NN/g)",
            "desc": "Nielsen Norman Group deep-dive into Perplexity's design decisions",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["perplexity", "nng", "research", "authority"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.smashingmagazine.com/2025/07/design-patterns-ai-interfaces/",
            "title": "Design Patterns for AI Interfaces (Smashing)",
            "desc": "Comprehensive guide to AI interface patterns from Smashing Magazine",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["patterns", "smashing", "comprehensive"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.patterns.dev/react/ai-ui-patterns/",
            "title": "AI UI Patterns (patterns.dev)",
            "desc": "React-focused AI UI patterns including streaming, typing indicators",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["react", "streaming", "patterns"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.aiuxdesign.guide/patterns/conversational-ui",
            "title": "Conversational UI Design Patterns",
            "desc": "Pattern library for chat interfaces and conversational UX",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["conversational", "pattern-library", "guide"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.shapeof.ai",
            "title": "Shape of AI - UX Patterns for AI Design",
            "desc": "Living collection of UX patterns specifically for AI product design",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["living-collection", "ai-ux", "reference"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://intuitionlabs.ai/articles/conversational-ai-ui-comparison-2025",
            "title": "Comparing Conversational AI UIs 2025",
            "desc": "Head-to-head comparison of ChatGPT, Claude, Perplexity, and Gemini interfaces",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["comparison", "chatgpt", "claude", "perplexity"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.saasui.design/application/perplexity-ai",
            "title": "Perplexity AI UI/UX Interface Design (SaaSUI)",
            "desc": "Detailed breakdown of Perplexity's interface patterns and components",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["perplexity", "breakdown", "saas"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://multitaskai.com/blog/chat-ui-design/",
            "title": "Chat UI Design Trends 2025",
            "desc": "Emerging trends in chat interface design — contextual inputs, AI cards",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["trends", "2025", "contextual"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://fuselabcreative.com/chatbot-interface-design-guide/",
            "title": "Chatbot Interface Design: Practical Guide 2026",
            "desc": "Step-by-step guide to designing effective chatbot interfaces",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["guide", "practical", "2026"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://dev.to/greedy_reader/ai-chat-ui-best-practices-designing-better-llm-interfaces-18jj",
            "title": "AI Chat UI Best Practices for LLM Interfaces",
            "desc": "Best practices for token streaming, markdown rendering, code block detection",
            "source": "articles", "sourceLabel": "Articles",
            "cat": "ux-patterns", "tags": ["best-practices", "llm", "streaming", "markdown"],
            "img": None, "urlQuality": 0.5
        },

        # === Model Selector & Canvas ===
        {
            "url": "https://uxpatterns.dev/patterns/ai-intelligence/model-selector",
            "title": "Model Selector Pattern (UX Patterns)",
            "desc": "Cross-platform model picker with provider logos and compact triggers",
            "source": "tools", "sourceLabel": "Tools & Libs",
            "cat": "model-canvas", "tags": ["model-picker", "pattern", "cross-platform"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.shadcn.io/ai/model-selector",
            "title": "React AI Model Selector (shadcn)",
            "desc": "shadcn/ui model selector component with fuzzy search and provider grouping",
            "source": "tools", "sourceLabel": "Tools & Libs",
            "cat": "model-canvas", "tags": ["shadcn", "react", "component"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://www.turbostarter.dev/ai/docs/components/model-selector",
            "title": "ModelSelector Component (TurboStarter)",
            "desc": "Production-ready model selector for AI apps with keyboard navigation",
            "source": "tools", "sourceLabel": "Tools & Libs",
            "cat": "model-canvas", "tags": ["component", "production", "keyboard"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://developers.openai.com/apps-sdk/build/chatgpt-ui",
            "title": "Build Your ChatGPT UI (OpenAI Apps SDK)",
            "desc": "Official guide to building custom UI components inside ChatGPT",
            "source": "tools", "sourceLabel": "Tools & Libs",
            "cat": "model-canvas", "tags": ["openai", "apps-sdk", "official", "chatgpt"],
            "img": None, "urlQuality": 0.5
        },
        {
            "url": "https://developers.openai.com/apps-sdk/concepts/ui-guidelines",
            "title": "ChatGPT UI Guidelines (OpenAI)",
            "desc": "Official UI guidelines for apps running inside ChatGPT — cards, carousels, fullscreen",
            "source": "tools", "sourceLabel": "Tools & Libs",
            "cat": "model-canvas", "tags": ["openai", "guidelines", "official", "cards"],
            "img": None, "urlQuality": 0.5
        },
    ],
    "allTags": [
        "chatgpt", "streaming", "react", "shadcn", "ai-sdk", "mobile",
        "dark-mode", "sidebar", "conversational", "case-study", "split-view",
        "dashboard", "perplexity", "agent", "free", "component", "patterns",
        "comparison", "2026", "voice", "multimodal", "saas"
    ],
    "tier": 0,
    "generatedAt": datetime.now().isoformat()
}

# Read template
with open(TEMPLATE) as f:
    html = f.read()

# Replace concept in title
html = html.replace("{{CONCEPT}}", data["concept"])

# Inject data at marker
data_json = json.dumps(data, indent=2, ensure_ascii=False)
# Replace the placeholder data between /*GALLERY_DATA*/ and /*END_GALLERY_DATA*/
import re
html = re.sub(
    r'/\*GALLERY_DATA\*/.*?/\*END_GALLERY_DATA\*/',
    f'/*GALLERY_DATA*/{data_json}/*END_GALLERY_DATA*/',
    html,
    flags=re.DOTALL
)

# Write output
with open(OUTPUT, "w") as f:
    f.write(html)

with_imgs = sum(1 for r in data["refs"] if r.get("img"))
print(f"Gallery built: {OUTPUT}")
print(f"  {len(data['refs'])} references")
print(f"  {with_imgs} with images")
print(f"  {len(data['refs']) - with_imgs} without images (placeholders)")
