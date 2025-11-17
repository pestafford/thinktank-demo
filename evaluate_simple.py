#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Evaluation Script for Swarm Results
Uses direct Claude API calls instead of RAGAS framework
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


def evaluate_answer(question, answer):
    """
    Evaluate a single answer using Claude API.
    Returns scores for different metrics.
    """
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

    # Evaluation prompt
    eval_prompt = f"""You are an expert evaluator for AI-generated security analysis reports.

Evaluate the following security analysis on these dimensions (scale 1-5):

1. **Relevancy**: How well does the analysis address the security question?
2. **Completeness**: Does it cover all important security aspects?
3. **Accuracy**: Are the security claims and recommendations technically sound?
4. **Clarity**: Is the analysis well-structured and easy to understand?
5. **Actionability**: Does it provide concrete, actionable recommendations?

QUESTION:
{question}

ANALYSIS:
{answer}

Provide your evaluation as a JSON object with scores (1-5) and brief explanations:
{{
  "relevancy": {{"score": X, "reasoning": "..."}},
  "completeness": {{"score": X, "reasoning": "..."}},
  "accuracy": {{"score": X, "reasoning": "..."}},
  "clarity": {{"score": X, "reasoning": "..."}},
  "actionability": {{"score": X, "reasoning": "..."}}
}}

Respond with ONLY the JSON object, no other text."""

    try:
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=2000,
            temperature=0,
            messages=[{"role": "user", "content": eval_prompt}]
        )

        # Extract JSON from response
        content = response.content[0].text

        # Try to parse JSON directly
        try:
            evaluation = json.loads(content)
        except json.JSONDecodeError:
            # If there's extra text, try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
            else:
                raise ValueError("Could not extract JSON from response")

        return evaluation

    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return None


def calculate_average_scores(evaluations):
    """Calculate average scores across all metrics."""
    metrics = ["relevancy", "completeness", "accuracy", "clarity", "actionability"]
    averages = {}

    for metric in metrics:
        scores = [e[metric]["score"] for e in evaluations if e and metric in e]
        if scores:
            averages[metric] = sum(scores) / len(scores)
        else:
            averages[metric] = 0

    # Overall average
    averages["overall"] = sum(averages.values()) / len(averages)

    return averages


def display_results(evaluations, swarm_results):
    """Display evaluation results in a readable format."""
    print("\n" + "="*70)
    print(" EVALUATION RESULTS")
    print("="*70 + "\n")

    for idx, (result, evaluation) in enumerate(zip(swarm_results, evaluations), 1):
        print(f"Question {idx}:")
        print(f"  {result['prompt'][:70]}...")
        print()

        if evaluation:
            for metric, data in evaluation.items():
                score = data.get("score", 0)
                reasoning = data.get("reasoning", "N/A")
                print(f"  {metric.upper():15s}: {score}/5")
                print(f"    → {reasoning}")
                print()
        else:
            print("  [Evaluation failed]")

        print("-" * 70)
        print()

    # Summary statistics
    averages = calculate_average_scores(evaluations)

    print("\n" + "="*70)
    print(" SUMMARY STATISTICS")
    print("="*70 + "\n")

    for metric, score in averages.items():
        print(f"  {metric.upper():15s}: {score:.2f}/5.00")

    print("\n" + "="*70)


def save_results(evaluations, swarm_results, output_file):
    """Save evaluation results to JSON."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    averages = calculate_average_scores(evaluations)

    results_dict = {
        "summary": averages,
        "detailed_results": [
            {
                "question": result["prompt"],
                "answer": result["consensus"],
                "evaluation": evaluation
            }
            for result, evaluation in zip(swarm_results, evaluations)
        ],
        "timestamp": datetime.now().isoformat()
    }

    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Simple evaluation for swarm results using Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:

  # Evaluate swarm results
  python3 evaluate_simple.py ignored/swarm_results.json

  # Specify output file
  python3 evaluate_simple.py ignored/swarm_results.json --output ignored/simple_eval.json

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
        default="ignored/simple_evaluation.json",
        help="Output file for evaluation results (default: ignored/simple_evaluation.json)"
    )

    args = parser.parse_args()

    # Check API keys
    if not os.getenv("CLAUDE_API_KEY"):
        print("ERROR: CLAUDE_API_KEY not set in .env")
        print("This is required for evaluation.")
        sys.exit(1)

    # Check input file exists
    if not Path(args.results_file).exists():
        print(f"ERROR: Results file not found: {args.results_file}")
        sys.exit(1)

    print("\n" + "="*70)
    print(" ThinkTank Swarm - Simple Evaluation")
    print("="*70 + "\n")

    # Step 1: Load results
    swarm_results = load_swarm_results(args.results_file)

    # Step 2: Evaluate each result
    print(f"\nEvaluating {len(swarm_results)} results...")
    evaluations = []

    for idx, result in enumerate(swarm_results, 1):
        print(f"\n[{idx}/{len(swarm_results)}] Evaluating: {result['prompt'][:60]}...")
        evaluation = evaluate_answer(result["prompt"], result["consensus"])
        evaluations.append(evaluation)

    # Step 3: Display results
    display_results(evaluations, swarm_results)

    # Step 4: Save results
    save_results(evaluations, swarm_results, args.output)

    print("\n" + "="*70)
    print(" Evaluation Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
