# ThinkTank Security Analysis Demo

A self-contained demonstration of ThinkTank's multi-agent swarm architecture applied to security analysis.

## Overview

This demo showcases ThinkTank's Persona-Attributed Deliberative Swarm (PADS) architecture:
- **5 Diverse Agents**: 2 Believers, 2 Skeptics, 1 Neutral perspective
- **Security Extension**: Specialized MCP Security domain expertise
- **Foreperson Synthesis**: Consensus reporting from multi-perspective debate
- **Parallel Execution**: Sub-10-second analysis using concurrent agent processing

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Prompt                        │
│         "Analyze security of X system"               │
└──────────────────────┬──────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │  Extension System (Optional)  │
        │  - MCP Security Extension    │
        │  - Auto-activates on keywords│
        └──────────────┬───────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │    Persona-Attributed Swarm  │
        │                              │
        │  ┌─────────┐  ┌─────────┐  │
        │  │Believer │  │Believer │  │
        │  │Agent 1  │  │Agent 2  │  │
        │  └─────────┘  └─────────┘  │
        │                              │
        │  ┌─────────┐  ┌─────────┐  │
        │  │Skeptic  │  │Skeptic  │  │
        │  │Agent 1  │  │Agent 2  │  │
        │  └─────────┘  └─────────┘  │
        │                              │
        │  ┌─────────────────────┐    │
        │  │  Neutral Observer   │    │
        │  └─────────────────────┘    │
        │                              │
        │  (Parallel Execution)        │
        └──────────────┬───────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │    Foreperson Agent          │
        │  - Synthesizes perspectives  │
        │  - Identifies consensus      │
        │  - Highlights disagreements  │
        │  - Provides recommendations  │
        └──────────────┬───────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │    Consensus Report          │
        │  - Executive Summary         │
        │  - Key Findings              │
        │  - Risk Assessment           │
        │  - Recommendations           │
        └──────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- Claude API key (Anthropic)

### Installation

```bash
# 1. Navigate to demo folder
cd demo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your CLAUDE_API_KEY

# 4. Run demo
python demo.py
```

## Usage

### Interactive Demo
```bash
python demo.py
```
This runs the default security analysis examples.

### Custom Analysis
```bash
python demo.py --prompt "Your security question here"
```

### Example Prompts
See `examples/security_prompts.txt` for pre-written examples:
- API security review
- Authentication system analysis
- Cloud infrastructure security
- Supply chain security assessment
- Zero-trust architecture evaluation

### Command-Line Options
```bash
python demo.py --help

Options:
  --prompt TEXT          Custom security analysis prompt
  --verbose             Show detailed agent reasoning
  --output FILE         Save consensus report to file
  --no-extension        Disable security extension
```

## Presentation Guide

### Demo Flow (5-10 minutes)

**1. Introduction (1 min)**
- "ThinkTank is a multi-agent swarm architecture for deliberative AI"
- "Today's demo: Security analysis use case"

**2. Architecture Overview (2 min)**
- Show architecture diagram (above)
- Explain persona diversity: Believers (optimistic), Skeptics (critical), Neutral (balanced)
- Highlight extension system for domain expertise

**3. Live Demo (3-5 min)**
```bash
# Run a compelling example
python demo.py --verbose --prompt "Analyze the security implications of implementing passwordless authentication using WebAuthn"
```

Watch the demo show:
- Extension activation (MCP Security expertise loaded)
- Parallel agent execution (~5 seconds)
- Diverse perspectives emerging
- Foreperson synthesis

**4. Key Points (2 min)**
- **Diversity reduces groupthink**: Multiple perspectives catch blind spots
- **Fast execution**: Parallel processing enables real-time analysis
- **Extensible**: Domain modules activate automatically
- **Transparent**: See all agent reasoning, not just final output

**5. Q&A Setup**
Have these ready:
- Compare to single-agent LLM output
- Show consensus vs. disagreement handling
- Demonstrate different security scenarios

## What Makes This Interesting

### 1. Persona-Attributed Deliberation
Unlike generic "multi-agent" systems, each ThinkTank agent has:
- Professional background and expertise
- Educational history
- Demographic diversity
- Explicit perspective (Believer/Skeptic/Neutral)

This creates **genuine intellectual diversity**, not just parallel calls to the same model.

### 2. Security Extension System
The MCP Security extension:
- Activates automatically on security keywords
- Injects specialized security knowledge
- Enhances all agents with domain expertise
- No manual configuration required

### 3. Consensus with Disagreement
The Foreperson doesn't force false consensus:
- Highlights areas of agreement
- Documents points of contention
- Explains why disagreements exist
- Provides nuanced recommendations

### 4. Performance
- **5-second analysis** for 5-agent swarm
- Parallel execution using ThreadPoolExecutor
- Production-ready performance

## Technical Details

### Swarm Configuration
```python
SWARM_SIZE = {
    "Believer": 2,  # Optimistic, solution-focused
    "Skeptic": 2,   # Critical, risk-focused
    "Neutral": 1    # Balanced, objective
}
# + 1 Foreperson for synthesis (6 agents total)
```

### Model Configuration
- Default: Claude Sonnet 4
- Configurable via `CLAUDE_MODEL` environment variable
- Version-agnostic design for easy upgrades

### Extension System
Extensions in `extensions/` auto-activate based on keywords:
```python
{
    "name": "mcp_security",
    "keywords": ["security", "vulnerability", "exploit", ...],
    "priority": 10
}
```

## File Structure

```
demo/
├── README.md                 # This file
├── demo.py                   # Main demo script
├── requirements.txt          # Python dependencies
├── .env.example             # Configuration template
│
├── lib/                     # Core ThinkTank code
│   ├── config.py           # Configuration
│   ├── agent.py            # Agent implementation
│   ├── swarm.py            # Swarm orchestration
│   ├── persona_loader.py   # Persona management
│   └── llm_provider.py     # Claude API integration
│
├── personas/                # Agent personas
│   ├── personas.json       # 5 diverse agent personas
│   └── foreperson.json     # Foreperson persona
│
├── extensions/              # Extension system
│   └── mcp_security/       # Security domain extension
│       ├── extension.json  # Extension metadata
│       └── system_prompt.txt
│
├── examples/                # Example prompts
│   └── security_prompts.txt
│
└── logs/                    # Output logs (created on first run)
```

## Customization

### Add Your Own Personas
Edit `personas/personas.json`:
```json
{
  "name": "Your Expert Name",
  "backstory": "Professional background...",
  "expertise": "Specific skills...",
  "camp": "Believer|Skeptic|Neutral"
}
```

### Change Swarm Size
Edit `lib/config.py`:
```python
SWARM_SIZE = {
    "Believer": 3,
    "Skeptic": 3,
    "Neutral": 2
}
```

### Create New Extensions
1. Copy `extensions/mcp_security/` structure
2. Create `extension.json` with keywords
3. Write `system_prompt.txt` with domain expertise
4. Place in `extensions/your_extension/`

## Troubleshooting

### "CLAUDE_API_KEY not set"
```bash
export CLAUDE_API_KEY="your-api-key-here"
# or edit .env file
```

### "Import error" or "Module not found"
```bash
pip install -r requirements.txt
```

### Slow performance
- First run may be slower (model initialization)
- Subsequent runs should be ~5 seconds
- Check network connection to Claude API

### Extension not activating
- Ensure keyword appears in prompt
- Check `extensions/mcp_security/extension.json`
- Use `--verbose` flag to see extension loading

## License

This demo is part of the ThinkTank project. See main repository for license details.

## Contact

For questions or feedback about this demo:
- Open an issue in the main ThinkTank repository
- Include `[demo]` tag in issue title

---

**Built with ThinkTank PADS Architecture**
*Bringing diverse perspectives to AI decision-making*
