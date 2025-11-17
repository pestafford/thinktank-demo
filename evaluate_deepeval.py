#!/usr/bin/env python3
"""
Evaluate ThinkTank Swarm Results with DeepEval
Uses deepeval metrics for comprehensive LLM evaluation
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import AnswerRelevancyMetric, GEval


def load_swarm_results(results_file):
    """Load swarm results from JSON file."""
    with open(results_file, 'r') as f:
        data = json.load(f)

    print(f"✓ Loaded {len(data)} swarm results from {results_file}")
    return data


def create_test_cases(swarm_results):
    """Convert swarm results to DeepEval test cases."""
    test_cases = []

    for result in swarm_results:
        test_case = LLMTestCase(
            input=result["prompt"],
            actual_output=result["consensus"]
        )
        test_cases.append(test_case)

    return test_cases


def evaluate_with_deepeval(test_cases, use_openai=False):
    """
    Evaluate using DeepEval metrics.

    Args:
        test_cases: List of LLMTestCase objects
        use_openai: If True, use OpenAI (gpt-4o-mini). If False, use Claude.
    """

    # Determine which model to use
    if use_openai:
        if not os.getenv("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not set but --openai flag was used")
            sys.exit(1)
        model = "gpt-4o-mini"
        print(f"Using model: {model}")
    else:
        # Check if deepeval supports Claude
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("CLAUDE_API_KEY"):
            print("ERROR: Neither ANTHROPIC_API_KEY nor CLAUDE_API_KEY is set")
            print("DeepEval typically uses OpenAI by default.")
            print("Try running with --openai flag if you have an OpenAI key.")
            sys.exit(1)
        # Note: DeepEval may not support Claude directly, might need custom implementation
        model = "claude-3-5-sonnet-20241022"
        print(f"Attempting to use model: {model}")
        print("Note: DeepEval may default to OpenAI. Check output.")

    # Define metrics
    print("\n" + "="*70)
    print(" DeepEval Metrics Configuration")
    print("="*70)

    # 1. Answer Relevancy
    relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=model,
        include_reason=True
    )
    print("✓ Answer Relevancy (threshold: 0.7)")

    # 2. Completeness (using GEval)
    completeness_metric = GEval(
        name="Completeness",
        criteria="""Evaluate how comprehensively the security analysis addresses all important
        aspects of the question. Consider whether it covers technical, operational, compliance,
        and risk management dimensions.""",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        model=model,
        include_reason=True,
        threshold=0.7
    )
    print("✓ Completeness (GEval, threshold: 0.7)")

    # 3. Technical Accuracy (using GEval)
    accuracy_metric = GEval(
        name="Technical Accuracy",
        criteria="""Determine whether the security analysis is technically sound and accurate.
        Evaluate if the security claims, vulnerabilities, and recommendations align with
        established cybersecurity best practices and industry standards.""",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        model=model,
        include_reason=True,
        threshold=0.7
    )
    print("✓ Technical Accuracy (GEval, threshold: 0.7)")

    # 4. Actionability (using GEval)
    actionability_metric = GEval(
        name="Actionability",
        criteria="""Assess whether the security analysis provides concrete, implementable
        recommendations. Look for specific steps, timelines, tools, or frameworks that
        organizations can directly act upon.""",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        model=model,
        include_reason=True,
        threshold=0.7
    )
    print("✓ Actionability (GEval, threshold: 0.7)")

    # Run evaluation
    print("\n" + "="*70)
    print(" Running Evaluation")
    print("="*70 + "\n")

    metrics = [
        relevancy_metric,
        completeness_metric,
        accuracy_metric,
        actionability_metric
    ]

    # Evaluate
    results = evaluate(
        test_cases=test_cases,
        metrics=metrics,
        run_async=False  # Set to True for faster evaluation if supported
    )

    return results, metrics


def display_results(test_cases, metrics):
    """Display evaluation results in a readable format."""
    print("\n" + "="*70)
    print(" DEEPEVAL EVALUATION RESULTS")
    print("="*70 + "\n")

    # Calculate averages
    metric_names = ["Answer Relevancy", "Completeness", "Technical Accuracy", "Actionability"]
    averages = {name: 0 for name in metric_names}

    for idx, test_case in enumerate(test_cases, 1):
        print(f"Question {idx}:")
        print(f"  {test_case.input[:70]}...")
        print()

        for metric_idx, metric in enumerate(metrics):
            metric_name = metric_names[metric_idx]
            # DeepEval stores metrics on the test case
            # This is a simplified version - actual implementation may vary
            print(f"  {metric_name:20s}: [See DeepEval output above]")

        print("-" * 70)
        print()

    print("\n" + "="*70)
    print(" Evaluation Complete!")
    print("="*70)
    print("\nNote: DeepEval provides detailed output during evaluation.")
    print("Check the output above for individual scores and reasoning.")


def save_results_to_json(output_file):
    """Save results to JSON (placeholder - DeepEval has its own output)."""
    print(f"\nDeepEval results are displayed in console output.")
    print(f"For persistent storage, consider DeepEval's built-in tracking features.")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate swarm results using DeepEval metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:

  # Evaluate swarm results (attempts Claude, may fall back to OpenAI)
  python3 evaluate_deepeval.py ignored/swarm_results.json

  # Explicitly use OpenAI
  python3 evaluate_deepeval.py ignored/swarm_results.json --openai

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
        "--openai",
        action="store_true",
        help="Use OpenAI (gpt-4o-mini) instead of attempting Claude"
    )

    args = parser.parse_args()

    # Check input file exists
    if not Path(args.results_file).exists():
        print(f"ERROR: Results file not found: {args.results_file}")
        sys.exit(1)

    print("\n" + "="*70)
    print(" ThinkTank Swarm - DeepEval Evaluation")
    print("="*70 + "\n")

    # Step 1: Load results
    swarm_results = load_swarm_results(args.results_file)

    # Step 2: Create test cases
    print(f"\nCreating {len(swarm_results)} test cases...")
    test_cases = create_test_cases(swarm_results)
    print(f"✓ Created {len(test_cases)} test cases")

    # Step 3: Evaluate
    try:
        results, metrics = evaluate_with_deepeval(test_cases, use_openai=args.openai)

        # Step 4: Display summary
        # Note: DeepEval prints detailed results during evaluation
        print("\n" + "="*70)
        print(" Evaluation Summary")
        print("="*70)
        print(f"\nEvaluated {len(test_cases)} swarm analyses")
        print(f"Metrics used: {len(metrics)}")
        print("\nSee detailed scores and reasoning in output above.")

    except Exception as e:
        print(f"\nERROR: Evaluation failed: {e}")
        print("\nNote: DeepEval primarily supports OpenAI models.")
        print("Try running with --openai flag if you have an OpenAI API key.")
        sys.exit(1)


if __name__ == "__main__":
    main()
