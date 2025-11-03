#!/usr/bin/env python3
"""
ThinkTank Security Analysis Demo
Self-contained demonstration of multi-agent swarm architecture
"""

import sys
import argparse
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.persona_loader import load_personas, load_foreperson
from lib.swarm import Swarm
from lib.extension_loader import ExtensionLoader
from lib.config import EXTENSIONS_ENABLED


# Example security prompts for quick demo
EXAMPLE_PROMPTS = [
    "Analyze the security implications of implementing passwordless authentication using WebAuthn for a financial services application.",
    "What are the key security risks in deploying AI agents with Model Context Protocol (MCP) tools in an enterprise environment?",
    "Evaluate the security architecture of a microservices-based API gateway that handles authentication and rate limiting."
]


def print_header():
    """Print demo header"""
    print("\n" + "="*70)
    print(" " * 15 + "ThinkTank Security Analysis Demo")
    print(" " * 10 + "Multi-Agent Swarm Architecture (PADS)")
    print("="*70)
    print("\nConfiguration:")
    print("  • Agents: 2 Believers + 2 Skeptics + 1 Neutral + 1 Foreperson")
    print("  • Extension: MCP Security (auto-activates on security keywords)")
    print("  • Execution: Parallel (sub-10-second analysis)")
    print("="*70 + "\n")


def print_prompt_menu():
    """Print example prompts menu"""
    print("\nExample Security Analysis Prompts:\n")
    for i, prompt in enumerate(EXAMPLE_PROMPTS, 1):
        print(f"{i}. {prompt}\n")
    print("0. Enter custom prompt\n")


def get_user_prompt():
    """Get prompt from user"""
    print_prompt_menu()

    choice = input("Select prompt (0-3) or press Enter for #1: ").strip()

    if not choice or choice == "1":
        return EXAMPLE_PROMPTS[0]
    elif choice == "2":
        return EXAMPLE_PROMPTS[1]
    elif choice == "3":
        return EXAMPLE_PROMPTS[2]
    elif choice == "0":
        custom = input("\nEnter your security analysis question: ").strip()
        return custom if custom else EXAMPLE_PROMPTS[0]
    else:
        print(f"Invalid choice, using example #1")
        return EXAMPLE_PROMPTS[0]


def run_demo(prompt, verbose=False, output_file=None, use_extensions=True, multi_phase=False):
    """
    Run the ThinkTank demo.

    Args:
        prompt: Security question to analyze
        verbose: Show detailed progress
        output_file: Save report to file
        use_extensions: Enable extension system
        multi_phase: Run multi-phase deliberation
    """
    # Load personas
    print("\n[1/4] Loading agent personas...")
    personas = load_personas("personas/personas.json")
    foreperson = load_foreperson("personas/foreperson.json")
    all_personas = personas + [foreperson]
    print(f"      Loaded {len(personas)} agents + foreperson")

    # Load extensions
    extension_context = None
    if use_extensions and EXTENSIONS_ENABLED:
        print("\n[2/4] Loading extensions...")
        loader = ExtensionLoader("extensions")
        loader.load_extensions()
        extensions = loader.list_extensions()

        if extensions:
            print(f"      Available: {', '.join(extensions)}")

            # Check if extension applies
            extension_context = loader.get_extension_context(prompt)
            if extension_context:
                print(f"      ✓ MCP Security extension activated!")
            else:
                print(f"      No extension match (prompt doesn't contain security keywords)")
        else:
            print("      No extensions found")
    else:
        print("\n[2/4] Extensions disabled")

    # Initialize swarm
    print("\n[3/4] Initializing swarm...")
    swarm = Swarm(all_personas, verbose=verbose)

    # Run analysis
    print("\n[4/4] Running deliberation...")
    print(f"\n{'='*70}")
    print(f"PROMPT: {prompt}")
    print(f"{'='*70}\n")

    if multi_phase:
        consensus = swarm.run_multi_phase(prompt, phases=3, extension_context=extension_context)
    else:
        consensus = swarm.run_single_phase(prompt, extension_context=extension_context)

    # Display results
    print(f"\n{'='*70}")
    print(" " * 20 + "CONSENSUS REPORT")
    print(f"{'='*70}\n")
    print(consensus)
    print(f"\n{'='*70}\n")

    # Save to file if requested
    if output_file:
        with open(output_file, "w") as f:
            f.write(f"ThinkTank Security Analysis\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"PROMPT:\n{prompt}\n\n")
            f.write(f"CONSENSUS REPORT:\n{consensus}\n")
        print(f"\n✓ Report saved to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ThinkTank Security Analysis Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with prompt selection
  python demo.py

  # Custom prompt
  python demo.py --prompt "Analyze API security for OAuth 2.0"

  # Verbose mode (show agent thinking)
  python demo.py --verbose

  # Multi-phase deliberation (3 rounds)
  python demo.py --multi

  # Save report to file
  python demo.py --output report.md

  # Disable extensions
  python demo.py --no-extension
        """
    )

    parser.add_argument(
        "--prompt",
        type=str,
        help="Custom security analysis prompt"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed agent reasoning"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Save consensus report to file"
    )

    parser.add_argument(
        "--no-extension",
        action="store_true",
        help="Disable security extension"
    )

    parser.add_argument(
        "--multi",
        action="store_true",
        help="Run multi-phase deliberation (3 rounds)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive prompt selection"
    )

    args = parser.parse_args()

    # Print header
    print_header()

    # Get prompt
    if args.prompt:
        prompt = args.prompt
        print(f"Using provided prompt: {prompt[:80]}...")
    elif args.interactive or not args.prompt:
        prompt = get_user_prompt()
    else:
        # Default to first example
        prompt = EXAMPLE_PROMPTS[0]
        print(f"Using default prompt: {prompt[:80]}...")

    # Run demo
    try:
        run_demo(
            prompt=prompt,
            verbose=args.verbose,
            output_file=args.output,
            use_extensions=not args.no_extension,
            multi_phase=args.multi
        )

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
