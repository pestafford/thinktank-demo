"""
ThinkTank Demo Configuration
Simplified configuration for demo deployment
"""

import os

# Model Configuration (version-agnostic)
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

# Swarm Configuration
# Demo uses: 2 Believers, 2 Skeptics, 1 Neutral + 1 Foreperson = 6 total agents
SWARM_SIZE = {
    "Believer": 2,  # Optimistic, solution-focused perspectives
    "Skeptic": 2,   # Critical, risk-focused perspectives
    "Neutral": 1    # Balanced, objective analysis
}

# Token Limits
AGENT_MAX_TOKENS = 2048      # Response length for regular agents (increased for high-quality responses)
FOREPERSON_MAX_TOKENS = 4096 # Longer report for synthesis (increased for complete analysis)

# Performance Settings
PARALLEL_EXECUTION = True    # Enable parallel agent execution
MAX_WORKERS = 8             # Maximum concurrent threads

# Extension System
EXTENSIONS_ENABLED = True
EXTENSIONS_PATH = "extensions"
