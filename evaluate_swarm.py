#!/usr/bin/env python3
"""
ThinkTank Swarm Evaluation with Ragas
Run security analysis through the swarm and evaluate with ragas metrics
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.persona_loader import load_personas, load_foreperson
from lib.swarm import Swarm
from lib.extension_loader import ExtensionLoader
from lib.config import EXTENSIONS_ENABLED

# Load environment variables
load_dotenv()


def run_swarm_analysis(prompt, use_extensions=True):
    """
    Run a single prompt through the swarm and return results.

    Args:
        prompt: Security question to analyze
        use_extensions: Enable extension system

    Returns:
        dict: Contains prompt, consensus, and individual agent responses
    """
    print(f"\n{'='*70}")
    print(f"Running swarm analysis...")
    print(f"{'='*70}\n")

    # Load personas
    personas = load_personas("personas/personas.json")
    foreperson = load_foreperson("personas/foreperson.json")
    all_personas = personas + [foreperson]

    # Load extensions
    extension_context = None
    if use_extensions and EXTENSIONS_ENABLED:
        loader = ExtensionLoader("extensions")
        loader.load_extensions()
        extension_context = loader.get_extension_context(prompt)
        if extension_context:
            print(f"✓ MCP Security extension activated!")

    # Initialize swarm
    swarm = Swarm(all_personas, verbose=True)

    # Run analysis (multi-phase by default)
    print(f"\nPrompt: {prompt}\n")
    consensus = swarm.run_multi_phase(prompt, phases=3, extension_context=extension_context)

    # Collect individual agent responses (from last phase)
    # Note: In a production system, you'd want to capture this during swarm execution

    return {
        "prompt": prompt,
        "consensus": consensus,
        "timestamp": datetime.now().isoformat(),
        "extension_used": extension_context is not None
    }


def save_results(results, output_file):
    """Save swarm results to JSON file for ragas evaluation."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


def create_ragas_dataset(results_file):
    """
    Convert swarm results to ragas-compatible format.

    Ragas expects:
    - question: The user's query
    - answer: The generated response
    - contexts: List of context chunks (we'll use the consensus)
    - ground_truth: Reference answer (optional)
    """
    from datasets import Dataset

    with open(results_file, 'r') as f:
        data = json.load(f)

    # Convert to ragas format
    ragas_data = []
    for item in data:
        ragas_data.append({
            "question": item["prompt"],
            "answer": item["consensus"],
            "contexts": [item["consensus"]],  # Using consensus as context
        })

    dataset = Dataset.from_list(ragas_data)
    return dataset


def evaluate_with_ragas(dataset):
    """
    Evaluate swarm outputs using ragas metrics.

    Available metrics:
    - faithfulness: Is the answer grounded in context?
    - answer_relevancy: Is the answer relevant to the question?
    - context_precision: How precise is the retrieved context?
    - context_recall: How much relevant context was retrieved?
    """
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
    )
    from langchain_openai import ChatOpenAI

    # Initialize evaluator LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Run evaluation
    print("\n" + "="*70)
    print("Running Ragas Evaluation...")
    print("="*70 + "\n")

    results = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
        ],
        llm=llm,
    )

    return results


def main():
    """Main workflow: collect prompts, run swarm, save for ragas."""

    # Example security analysis prompts
    test_prompts = [
        "Analyze the security implications of implementing passwordless authentication using WebAuthn for a financial services application.",
        "What are the key security risks in deploying AI agents with Model Context Protocol (MCP) tools in an enterprise environment?",
        "Evaluate the security architecture of a microservices-based API gateway that handles authentication and rate limiting.",
    ]

    print("\n" + "="*70)
    print(" ThinkTank Swarm Evaluation Pipeline")
    print("="*70)
    print("\nThis script will:")
    print("1. Run prompts through the multi-agent swarm")
    print("2. Save results to JSON")
    print("3. Convert to ragas format")
    print("4. Evaluate with ragas metrics")
    print("\n" + "="*70 + "\n")

    # Step 1: Run swarm analyses
    all_results = []
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[{i}/{len(test_prompts)}] Processing prompt...")
        result = run_swarm_analysis(prompt)
        all_results.append(result)

    # Step 2: Save results
    output_file = "ignored/swarm_results.json"
    save_results(all_results, output_file)

    # Step 3: Create ragas dataset
    print("\n" + "="*70)
    print("Converting to Ragas Dataset...")
    print("="*70)
    dataset = create_ragas_dataset(output_file)
    print(f"✓ Dataset created with {len(dataset)} examples")

    # Step 4: Evaluate with ragas
    eval_results = evaluate_with_ragas(dataset)

    # Step 5: Display results
    print("\n" + "="*70)
    print(" RAGAS EVALUATION RESULTS")
    print("="*70 + "\n")
    print(eval_results)

    # Save evaluation results
    eval_output = "ignored/ragas_evaluation_results.json"
    with open(eval_output, 'w') as f:
        json.dump({
            "metrics": eval_results.to_pandas().to_dict(),
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    print(f"\n✓ Evaluation results saved to: {eval_output}")


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("CLAUDE_API_KEY"):
        print("ERROR: CLAUDE_API_KEY not set in .env")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set in .env")
        sys.exit(1)

    main()
