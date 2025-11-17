#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal RAGAS Evaluation Script
Uses RAGAS without HuggingFace datasets library
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_swarm_results(results_file):
    """Load swarm results from JSON file."""
    with open(results_file, 'r') as f:
        data = json.load(f)

    print(f"✓ Loaded {len(data)} swarm results from {results_file}")
    return data


def evaluate_with_ragas(swarm_results):
    """
    Evaluate with ragas metrics using direct API (no datasets library).
    """
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy
    from langchain_openai import ChatOpenAI

    # Initialize evaluator LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create evaluation data in dict format (RAGAS 0.2+  supports this)
    eval_data = {
        "question": [],
        "answer": [],
        "contexts": []
    }

    for item in swarm_results:
        eval_data["question"].append(item["prompt"])
        eval_data["answer"].append(item["consensus"])
        eval_data["contexts"].append([item["consensus"]])  # Using consensus as context

    print("\n" + "="*70)
    print(" Running RAGAS Evaluation")
    print("="*70)
    print(f"\nMetrics: faithfulness, answer_relevancy")
    print(f"LLM: gpt-4o-mini")
    print(f"Examples: {len(eval_data['question'])}\n")

    # Run evaluation
    metrics = [faithfulness, answer_relevancy]

    results = evaluate(
        eval_data,
        metrics=metrics,
        llm=llm,
    )

    return results, eval_data


def display_results(results, eval_data):
    """Display evaluation results in a readable format."""
    print("\n" + "="*70)
    print(" RAGAS EVALUATION RESULTS")
    print("="*70 + "\n")

    # Display summary statistics
    print("Summary Statistics:")
    print("-" * 70)

    for metric_name, score in results.items():
        if isinstance(score, (int, float)):
            print(f"  {metric_name:20s}: {score:.3f}")

    print("\n" + "-" * 70)
    print("\nDetailed Results:")
    print("-" * 70)

    # Display per-question results if available
    num_questions = len(eval_data["question"])
    for idx in range(num_questions):
        print(f"\nQuestion {idx + 1}:")
        print(f"  Question: {eval_data['question'][idx][:60]}...")
        print(f"  Answer length: {len(eval_data['answer'][idx])} chars")

    print("\n" + "="*70)

    return results


def save_results(results, eval_data, output_file):
    """Save evaluation results to JSON."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results_dict = {
        "summary": {k: float(v) if isinstance(v, (int, float)) else v
                   for k, v in results.items()},
        "evaluation_data": {
            "questions": eval_data["question"],
            "answers": eval_data["answer"]
        },
        "timestamp": datetime.now().isoformat()
    }

    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Minimal RAGAS evaluation for swarm results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:

  # Evaluate swarm results
  python3.12 evaluate_ragas_minimal.py ignored/swarm_results.json

  # Specify output file
  python3.12 evaluate_ragas_minimal.py ignored/swarm_results.json --output ignored/ragas_eval.json
        """
    )

    parser.add_argument(
        "results_file",
        help="Path to JSON file with swarm results"
    )

    parser.add_argument(
        "--output", "-o",
        default="ignored/ragas_evaluation.json",
        help="Output file for evaluation results (default: ignored/ragas_evaluation.json)"
    )

    args = parser.parse_args()

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set in .env")
        print("This is required for RAGAS evaluation.")
        sys.exit(1)

    # Check input file exists
    if not Path(args.results_file).exists():
        print(f"ERROR: Results file not found: {args.results_file}")
        sys.exit(1)

    print("\n" + "="*70)
    print(" ThinkTank Swarm - RAGAS Evaluation (Minimal)")
    print("="*70 + "\n")

    # Step 1: Load results
    swarm_results = load_swarm_results(args.results_file)

    # Step 2: Evaluate
    try:
        eval_results, eval_data = evaluate_with_ragas(swarm_results)
    except Exception as e:
        print(f"\nERROR during evaluation: {e}")
        print("\nThis might be due to missing dependencies.")
        print("Try installing in a venv:")
        print("  python3.12 -m venv venv-ragas")
        print("  source venv-ragas/bin/activate")
        print("  pip install ragas langchain-openai python-dotenv --no-deps")
        print("  pip install langchain-core langchain openai pydantic tiktoken python-dotenv")
        sys.exit(1)

    # Step 3: Display results
    results = display_results(eval_results, eval_data)

    # Step 4: Save results
    save_results(results, eval_data, args.output)

    print("\n" + "="*70)
    print(" Evaluation Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
