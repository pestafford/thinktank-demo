#!/usr/bin/env python3
"""
Batch generate swarm results for evaluation
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from lib.persona_loader import load_personas, load_foreperson
from lib.swarm import Swarm
from lib.extension_loader import ExtensionLoader
from lib.config import EXTENSIONS_ENABLED

# 20 diverse security analysis prompts
PROMPTS = [
    "Analyze the security implications of implementing passwordless authentication using WebAuthn for a financial services application.",
    "What are the key security risks in deploying AI agents with Model Context Protocol (MCP) tools in an enterprise environment?",
    "Evaluate the security architecture of a microservices-based API gateway that handles authentication and rate limiting.",
    "Assess the security considerations for implementing zero-trust network architecture in a hybrid cloud environment.",
    "What are the critical security vulnerabilities in implementing OAuth 2.0 for a mobile banking application?",
    "Analyze the security implications of implementing end-to-end encryption in a collaborative document editing platform.",
    "Evaluate the security risks of implementing blockchain-based identity management for healthcare records.",
    "What are the key security challenges in deploying serverless functions in a multi-tenant cloud environment?",
    "Assess the security implications of implementing biometric authentication for remote workforce access.",
    "Analyze the security architecture needed for a real-time payment processing system handling cryptocurrency transactions.",
    "What are the critical security considerations for implementing federated identity management across multiple cloud providers?",
    "Evaluate the security risks of implementing AI-powered threat detection in a critical infrastructure network.",
    "Assess the security implications of migrating legacy authentication systems to cloud-native identity providers.",
    "What are the key security vulnerabilities in implementing GraphQL APIs for mobile applications?",
    "Analyze the security considerations for implementing secure multi-party computation in financial trading systems.",
    "Evaluate the security architecture needed for implementing IoT device management in smart city infrastructure.",
    "What are the critical security risks in implementing container orchestration with Kubernetes in production environments?",
    "Assess the security implications of implementing homomorphic encryption for privacy-preserving data analytics.",
    "Analyze the security challenges in implementing secure software supply chain management for open-source dependencies.",
    "What are the key security considerations for implementing quantum-resistant cryptography in long-term data storage systems?"
]

def run_swarm_analysis(prompt, use_extensions=True):
    """Run a single prompt through the swarm."""
    # Load extensions
    extension_context = None
    if use_extensions and EXTENSIONS_ENABLED:
        loader = ExtensionLoader("extensions")
        loader.load_extensions()
        extension_context = loader.get_extension_context(prompt)

    # Initialize swarm
    swarm = Swarm(all_personas, verbose=False)

    # Run analysis
    consensus = swarm.run_multi_phase(prompt, phases=3, extension_context=extension_context)

    return {
        "prompt": prompt,
        "consensus": consensus,
        "timestamp": datetime.now().isoformat(),
        "extension_used": extension_context is not None
    }

# Load personas once
print("Loading personas...")
personas = load_personas('personas/personas.json')
foreperson = load_foreperson('personas/foreperson.json')
all_personas = personas + [foreperson]
print(f"✓ Loaded {len(personas)} agents + foreperson\n")

# Process all prompts
results = []
total = len(PROMPTS)

print(f"Generating {total} swarm analyses...")
print("="*70)

for i, prompt in enumerate(PROMPTS, 1):
    print(f"\n[{i}/{total}] {prompt[:65]}...")

    try:
        result = run_swarm_analysis(prompt)
        results.append(result)
        print(f"✓ Complete ({len(result['consensus'])} chars)")
    except Exception as e:
        print(f"✗ Error: {e}")

# Save results
output_file = "ignored/swarm_results.json"
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*70)
print(f"\n✓ Generated {len(results)}/{total} results")
print(f"✓ Saved to: {output_file}")
print(f"\nNext step:")
print(f"  python3 evaluate_simple.py {output_file}")
print()
