# ThinkTank Security Analysis Demo - Manifest

## What This Demo Contains

This is a **self-contained, production-ready** demonstration of ThinkTank's **PERSONA** architecture (**P**ersona-**E**nhanced **R**easoning through **S**tructured **O**ntological **N**atural **A**rgumentation) applied to security analysis.

## Complete File Structure

```
demo/
├── README.md                 # Complete documentation (10KB)
├── QUICKSTART.md             # 5-minute setup guide (5KB)
├── MANIFEST.md              # This file
├── LICENSE                  # MIT License
├── requirements.txt         # Python dependencies (minimal)
├── .env.example            # Configuration template
├── .gitignore              # Git exclusions
├── demo.py                 # Main entry point (7KB, executable)
│
├── lib/                    # Core ThinkTank library (simplified)
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── llm_provider.py    # Claude API integration
│   ├── agent.py           # Individual agent implementation
│   ├── persona_loader.py  # Persona management
│   ├── swarm.py           # Parallel swarm orchestration
│   └── extension_loader.py # Extension system
│
├── personas/               # Agent personas (curated for security)
│   ├── personas.json      # 5 diverse agents (2B/2S/1N)
│   └── foreperson.json    # Consensus synthesizer
│
├── extensions/             # Domain expertise modules
│   └── mcp_security/      # Security analysis extension
│       ├── __init__.py
│       ├── extension.json # Extension metadata
│       └── system_prompt.txt # Security expertise (2KB)
│
├── examples/               # Example prompts and use cases
│   └── security_prompts.txt # 50+ security analysis prompts
│
└── logs/                   # Output directory (created on first run)
```

## Line Counts

```
Core Library:      ~500 lines
Demo Script:       ~200 lines
Documentation:     ~600 lines
Personas:          ~100 lines
Extension:         ~100 lines
-----------------------------------
Total:            ~1,500 lines
```

## What's Included

### Core Functionality ✅
- [x] Multi-agent swarm orchestration
- [x] Parallel execution (ThreadPoolExecutor)
- [x] Persona-attributed agents (diverse backgrounds)
- [x] Extension system with auto-activation
- [x] MCP Security domain expertise
- [x] Consensus synthesis with disagreement handling
- [x] Claude API integration (version-agnostic)

### Agent Configuration ✅
- [x] 2 Believers (optimistic, solution-focused)
- [x] 2 Skeptics (critical, risk-focused)
- [x] 1 Neutral (balanced, objective)
- [x] 1 Foreperson (synthesis, consensus-building)

### Documentation ✅
- [x] Complete README with architecture diagrams
- [x] Quick start guide (5-minute setup)
- [x] 50+ example security prompts
- [x] Presentation guide with demo flow
- [x] Troubleshooting section
- [x] Customization instructions

### Development Tools ✅
- [x] Requirements file (minimal dependencies)
- [x] Environment configuration template
- [x] Git ignore file
- [x] MIT License
- [x] Executable demo script

## What's NOT Included

The following are intentionally excluded to keep the demo lightweight:

- ❌ Dynamic persona generation (static personas only)
- ❌ Multiple extension examples (MCP Security only)
- ❌ Database/persistence layer
- ❌ Web UI or API server
- ❌ Experiment/evaluation framework
- ❌ Docker containerization
- ❌ CI/CD configuration
- ❌ Unit tests (demo-focused)

These features are available in the main ThinkTank repository.

## Fork-Ready

This demo is designed to be forked into a standalone repository:

### To Fork as Separate Repo:

```bash
# 1. Create new repository on GitHub (e.g., "thinktank-security-demo")

# 2. Copy demo folder contents
cp -r demo/ ../thinktank-security-demo/
cd ../thinktank-security-demo/

# 3. Initialize git
git init
git add .
git commit -m "Initial commit: ThinkTank Security Analysis Demo"

# 4. Push to GitHub
git remote add origin https://github.com/yourusername/thinktank-security-demo.git
git push -u origin main

# 5. Update README.md if needed
# - Change repository links
# - Update contact information
# - Customize for your use case
```

### Recommended Repo Name Options:
- `thinktank-security-demo`
- `thinktank-swarm-demo`
- `pads-security-analysis`
- `multi-agent-security-demo`

## Dependencies

### Required:
- Python 3.8+
- `anthropic` library (0.39.0+)

### Optional:
- `python-dotenv` (for .env file support)

### No External Services Required:
- No database
- No message queue
- No external APIs (except Claude)
- No Docker/containers

## Size & Performance

### Package Size:
- Compressed: ~25KB (without venv)
- With dependencies: ~15MB (anthropic + deps)
- Installed: ~20MB total

### Performance:
- Cold start: ~2 seconds (persona loading)
- Analysis time: ~5 seconds (parallel execution)
- Memory usage: ~50MB (lightweight)

### API Costs (Claude Sonnet 4):
- Single analysis: ~$0.02-0.05
- 100 analyses: ~$2-5
- Verbose mode: +20% tokens (more output)

## Customization Points

### Easy Customizations (No Code):
1. **Personas**: Edit `personas/personas.json`
2. **Extension Expertise**: Edit `extensions/mcp_security/system_prompt.txt`
3. **Example Prompts**: Add to `examples/security_prompts.txt`
4. **Keywords**: Edit `extensions/mcp_security/extension.json`

### Medium Customizations (Minimal Code):
1. **Swarm Size**: Edit `lib/config.py` (SWARM_SIZE)
2. **Token Limits**: Edit `lib/config.py` (MAX_TOKENS)
3. **New Extension**: Copy extension structure, add metadata

### Advanced Customizations (Code Changes):
1. **Different LLM**: Replace `lib/llm_provider.py`
2. **Web UI**: Add Flask/FastAPI wrapper
3. **Persistence**: Add database layer
4. **Streaming**: Modify swarm to stream responses

## Presentation-Ready

This demo is optimized for live presentations:

### Timing:
- Setup: 5 minutes (if API key ready)
- Introduction: 1-2 minutes
- Live demo: 5-7 minutes
- Q&A: 10-15 minutes
- **Total: 20-30 minute slot**

### Backup Plan:
- Pre-run demo and save output to file
- Show file if live demo has technical issues
- Explain architecture with README diagrams

### Key Talking Points:
1. **Persona Attribution** - Not generic multi-agent
2. **Parallel Execution** - Production-ready speed
3. **Extension System** - Modular domain expertise
4. **Consensus with Disagreement** - Transparent reasoning
5. **Security Focus** - Real-world application

## Support & Resources

### Documentation:
- `README.md` - Complete guide
- `QUICKSTART.md` - Fast setup
- `examples/security_prompts.txt` - 50+ examples

### Source:
- Main repository: [github.com/yourusername/thinktank](https://github.com/yourusername/thinktank)
- Issues: Report via GitHub Issues

### Contact:
- Questions: Open an issue in main repo
- Contributions: Pull requests welcome
- Custom versions: Fork this demo

## Version Info

- **Demo Version**: 1.0.0
- **ThinkTank Core**: Based on v2.x architecture
- **Claude Model**: Sonnet 4 (configurable)
- **Last Updated**: 2025-01-03

## License

MIT License - See `LICENSE` file

Free to use, modify, and distribute for commercial or non-commercial purposes.

---

**This demo is production-ready and presentation-ready out of the box.**

No additional setup beyond API key required. Just run `python demo.py` and you're live.
