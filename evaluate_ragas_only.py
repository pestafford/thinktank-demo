#!/usr/bin/env python3
"""
Ragas-Only Evaluation Script
Takes pre-generated swarm results and evaluates them with ragas
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


def create_ragas_dataset(swarm_results):
    """
    Convert swarm results to ragas-compatible format.

    Expected input format:
    [
      {
        "prompt": "question text",
        "consensus": "swarm consensus report",
        "timestamp": "optional"
      }
    ]

    Ragas format:
    - question: The user's query
    - answer: The generated response
    - contexts: List of context chunks
    """
    from datasets import Dataset

    ragas_data = []
    for item in swarm_results:
        ragas_data.append({
            "question": item["prompt"],
            "answer": item["consensus"],
            "contexts": [item["consensus"]],  # Using consensus as context
        })

    dataset = Dataset.from_list(ragas_data)
    print(f"✓ Created ragas dataset with {len(dataset)} examples")
    return dataset


def evaluate_with_ragas(dataset, metrics_to_use=None):
    """
    Evaluate with ragas metrics.

    Available metrics:
    - faithfulness: Answer grounded in context
    - answer_relevancy: Answer relevant to question
    - answer_correctness: Factual correctness (requires ground_truth)
    - context_precision: Precision of retrieved context (requires ground_truth)
    - context_recall: Recall of relevant context (requires ground_truth)
    """
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
    )
    from langchain_openai import ChatOpenAI

    # Initialize evaluator LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Default metrics (no ground truth required)
    default_metrics = [
        faithfulness,
        answer_relevancy,
    ]

    metrics = metrics_to_use or default_metrics

    print("\n" + "="*70)
    print(" Running Ragas Evaluation")
    print("="*70)
    print(f"\nMetrics: {[m.name for m in metrics]}")
    print(f"LLM: gpt-4o-mini")
    print(f"Examples: {len(dataset)}\n")

    # Run evaluation
    results = evaluate(
        dataset,
        metrics=metrics,
        llm=llm,
    )

    return results


def display_results(results):
    """Display evaluation results in a readable format."""
    print("\n" + "="*70)
    print(" RAGAS EVALUATION RESULTS")
    print("="*70 + "\n")

    # Convert to pandas for better display
    df = results.to_pandas()

    # Display summary statistics
    print("Summary Statistics:")
    print("-" * 70)

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        mean_val = df[col].mean()
        print(f"  {col:20s}: {mean_val:.3f} (avg)")

    print("\n" + "-" * 70)
    print("\nDetailed Results:")
    print("-" * 70)

    # Display per-question results
    for idx, row in df.iterrows():
        print(f"\nQuestion {idx + 1}:")
        print(f"  Question: {row['question'][:60]}...")
        for col in numeric_cols:
            print(f"  {col:20s}: {row[col]:.3f}")

    print("\n" + "="*70)

    return df


def save_results(results_df, output_file):
    """Save evaluation results to JSON."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results_dict = {
        "summary": {
            col: float(results_df[col].mean())
            for col in results_df.select_dtypes(include=['float64', 'int64']).columns
        },
        "detailed_results": results_df.to_dict('records'),
        "timestamp": datetime.now().isoformat()
    }

    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate swarm results with ragas metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:

  # Evaluate swarm results
  python evaluate_ragas_only.py ignored/swarm_results.json

  # Specify output file
  python evaluate_ragas_only.py ignored/swarm_results.json --output ignored/eval.json

Expected input JSON format:
  [
    {
      "prompt": "Your security question",
      "consensus": "The swarm consensus report"
    }
  ]
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
        print("This is required for ragas evaluation.")
        sys.exit(1)

    # Check input file exists
    if not Path(args.results_file).exists():
        print(f"ERROR: Results file not found: {args.results_file}")
        sys.exit(1)

    print("\n" + "="*70)
    print(" ThinkTank Swarm - Ragas Evaluation")
    print("="*70 + "\n")

    # Step 1: Load results
    swarm_results = load_swarm_results(args.results_file)

    # Step 2: Create ragas dataset
    dataset = create_ragas_dataset(swarm_results)

    # Step 3: Evaluate
    eval_results = evaluate_with_ragas(dataset)

    # Step 4: Display results
    results_df = display_results(eval_results)

    # Step 5: Save results
    save_results(results_df, args.output)

    print("\n" + "="*70)
    print(" Evaluation Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
