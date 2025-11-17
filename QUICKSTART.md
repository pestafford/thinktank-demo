# ThinkTank Demo - 5-Minute Quick Start

Get the demo running in under 5 minutes.

## Prerequisites
- Python 3.8 or higher
- Claude API key ([Get one here](https://console.anthropic.com/))

## Installation

```bash
# 1. Navigate to demo directory
cd demo

# 2. Install dependencies (just anthropic library)
pip install anthropic

# 3. Set your API key
export CLAUDE_API_KEY="your-api-key-here"

# 4. Run the demo!
python demo.py
```

## What You'll See

The demo will:
1. Load 5 diverse agent personas + 1 foreperson (6 total agents)
2. Activate the MCP Security extension (adds domain expertise)
3. Present you with 3 example security prompts
4. Run a ~5-second parallel analysis with diverse perspectives
5. Show you the synthesized consensus report

## Example Output

```
======================================================================
              ThinkTank Security Analysis Demo
         Multi-Agent PERSONA Architecture
======================================================================

Configuration:
  • Agents: 2 Believers + 2 Skeptics + 1 Neutral + 1 Foreperson
  • Extension: MCP Security (auto-activates on security keywords)
  • Execution: Parallel (sub-10-second analysis)
======================================================================

[1/4] Loading agent personas...
      Loaded 5 agents + foreperson

[2/4] Loading extensions...
      Available: mcp_security
      ✓ MCP Security extension activated!

[3/4] Initializing swarm...

[4/4] Running deliberation...

======================================================================
PROMPT: Analyze the security implications of implementing
passwordless authentication using WebAuthn...
======================================================================

[Believer 1] Thinking...
[Believer 2] Thinking...
[Skeptic 1] Thinking...
[Skeptic 2] Thinking...
[Neutral 1] Thinking...

--- Foreperson Synthesis ---

[Foreperson] Synthesizing perspectives...

======================================================================
                     CONSENSUS REPORT
======================================================================

[Detailed multi-perspective security analysis appears here]

======================================================================
```

## Next Steps

### Try Different Modes

```bash
# Verbose mode (see agent reasoning)
python demo.py --verbose

# Multi-phase deliberation (3 rounds)
python demo.py --multi

# Save report to file
python demo.py --output security_report.md

# Use a custom prompt
python demo.py --prompt "Your security question here"
```

### For Your Presentation

1. **Live Demo** (5-7 minutes):
   ```bash
   python demo.py --verbose --prompt "Analyze the security of..."
   ```

2. **Pre-run and Save** (for backup):
   ```bash
   python demo.py --multi -o backup_report.md
   ```

3. **Compare Approaches**:
   ```bash
   # Single-phase (fast)
   python demo.py

   # Multi-phase (more thorough)
   python demo.py --multi
   ```

## Troubleshooting

### "CLAUDE_API_KEY not set"
```bash
# Option 1: Export in terminal
export CLAUDE_API_KEY="sk-ant-..."

# Option 2: Create .env file
cp .env.example .env
# Edit .env and add your key
```

### "Module not found"
```bash
# Ensure you're in the demo directory
cd demo

# Reinstall dependencies
pip install -r requirements.txt
```

### "Connection error"
- Check your internet connection
- Verify your Claude API key is valid
- Try again (occasional API timeouts are normal)

## Demo Tips

1. **Start Simple**: Use the default prompt first
2. **Show Diversity**: Use `--verbose` to reveal different perspectives
3. **Explain the Flow**: Point out Believers, Skeptics, Neutral, and Foreperson roles
4. **Highlight Speed**: Mention this is real-time parallel processing (~5 sec)
5. **Discuss Extension**: Note how security expertise auto-activates

## Architecture Highlight

```
User Prompt → Extension System → Multi-Agent Swarm → Consensus Report
                    ↓                    ↓
              (Security      (2 Believers, 2 Skeptics,
               Expertise)     1 Neutral + Foreperson)
```

**Key Differentiators:**
- Persona-attributed agents (not generic multi-agent)
- Automatic domain expertise injection
- Parallel execution for production speed
- Transparent reasoning (see all perspectives)
- Structured consensus with disagreement handling

## Full Documentation

See `README.md` for:
- Complete feature documentation
- All command-line options
- Customization guide
- 50+ example security prompts
- Architecture deep-dive
- Extension system details

## Support

Questions? Check:
- `README.md` - Full documentation
- `examples/security_prompts.txt` - 50+ example prompts
- Main ThinkTank repository - Issues and discussions

---

**Ready to present!** Just run `python demo.py` and you're good to go.
