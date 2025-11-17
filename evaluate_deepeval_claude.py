#!/usr/bin/env python3
"""
Evaluate ThinkTank Swarm Results with DeepEval using Claude
Custom metrics implementation that uses Claude instead of OpenAI
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

from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric
from deepeval.scorer import Scorer
from anthropic import Anthropic


class ClaudeMetric(BaseMetric):
    """Base class for Claude-powered metrics"""

    def __init__(self, name: str, criteria: str, threshold: float = 0.7):
        self.name = name
        self.criteria = criteria
        self.threshold = threshold
        self.evaluation_cost = 0  # Track API costs

        # Initialize Claude client
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not set in environment")
        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

    def measure(self, test_case: LLMTestCase) -> float:
        """Evaluate the test case using Claude"""

        # Build evaluation prompt
        eval_prompt = f"""You are an expert evaluator. Evaluate the following response based on this criteria:

CRITERIA: {self.criteria}

QUESTION:
{test_case.input}

RESPONSE:
{test_case.actual_output}

Provide a score from 0.0 to 1.0 where:
- 1.0 = Excellent, fully meets criteria
- 0.7-0.9 = Good, mostly meets criteria
- 0.4-0.6 = Adequate, partially meets criteria
- 0.0-0.3 = Poor, does not meet criteria

Also provide a brief explanation for your score.

Respond in JSON format:
{{
    "score": 0.85,
    "reason": "Brief explanation here"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0,
                messages=[{"role": "user", "content": eval_prompt}]
            )

            # Extract JSON from response
            content = response.content[0].text

            # Try to parse JSON
            try:
                result = json.loads(content)
                score = result.get("score", 0.0)
                self.reason = result.get("reason", "No reason provided")
            except json.JSONDecodeError:
                # Try to extract JSON from text
                import re
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    score = result.get("score", 0.0)
                    self.reason = result.get("reason", "No reason provided")
                else:
                    # Fallback: try to find a number
                    score_match = re.search(r'score["\s:]+([0-9.]+)', content)
                    if score_match:
                        score = float(score_match.group(1))
                        self.reason = content[:200]
                    else:
                        score = 0.0
                        self.reason = f"Could not parse response: {content[:200]}"

            self.score = score
            self.success = score >= self.threshold

            return score

        except Exception as e:
            print(f"Error evaluating with Claude: {e}")
            self.score = 0.0
            self.reason = f"Evaluation error: {str(e)}"
            self.success = False
            return 0.0

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async version - just call sync for now"""
        return self.measure(test_case)

    def is_successful(self) -> bool:
        """Check if metric passed threshold"""
        return self.success

    @property
    def __name__(self):
        return self.name


class RelevancyMetric(ClaudeMetric):
    """Measures how relevant the response is to the question"""

    def __init__(self, threshold: float = 0.7):
        super().__init__(
            name="Relevancy",
            criteria="""Evaluate how well the response addresses the security question asked.
            The response should directly answer what was asked and stay focused on the topic.""",
            threshold=threshold
        )


class CompletenessMetric(ClaudeMetric):
    """Measures how comprehensive the analysis is"""

    def __init__(self, threshold: float = 0.7):
        super().__init__(
            name="Completeness",
            criteria="""Evaluate how comprehensively the security analysis addresses all important
            aspects. Consider whether it covers technical, operational, compliance, risk management,
            and implementation dimensions.""",
            threshold=threshold
        )


class AccuracyMetric(ClaudeMetric):
    """Measures technical accuracy"""

    def __init__(self, threshold: float = 0.7):
        super().__init__(
            name="Technical Accuracy",
            criteria="""Determine whether the security analysis is technically sound and accurate.
            Evaluate if security claims, vulnerabilities, and recommendations align with established
            cybersecurity best practices and industry standards.""",
            threshold=threshold
        )


class ActionabilityMetric(ClaudeMetric):
    """Measures how actionable the recommendations are"""

    def __init__(self, threshold: float = 0.7):
        super().__init__(
            name="Actionability",
            criteria="""Assess whether the security analysis provides concrete, implementable
            recommendations. Look for specific steps, timelines, tools, frameworks, or controls
            that organizations can directly act upon.""",
            threshold=threshold
        )


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


def evaluate_with_claude_metrics(test_cases):
    """Evaluate using custom Claude-powered metrics."""

    print("\n" + "="*70)
    print(" Claude-Powered DeepEval Metrics")
    print("="*70)

    # Initialize metrics
    metrics = [
        RelevancyMetric(threshold=0.7),
        CompletenessMetric(threshold=0.7),
        AccuracyMetric(threshold=0.7),
        ActionabilityMetric(threshold=0.7)
    ]

    print(f"\n✓ Initialized {len(metrics)} custom Claude metrics")
    print(f"  Model: {metrics[0].model}")
    print()

    # Evaluate each test case
    results = []

    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n[{idx}/{len(test_cases)}] Evaluating: {test_case.input[:60]}...")

        test_results = {
            "question": test_case.input,
            "answer": test_case.actual_output,
            "scores": {}
        }

        for metric in metrics:
            score = metric.measure(test_case)
            test_results["scores"][metric.name] = {
                "score": score,
                "passed": metric.is_successful(),
                "reason": metric.reason
            }

            status = "✓" if metric.is_successful() else "✗"
            print(f"  {status} {metric.name:20s}: {score:.2f} ({'PASS' if metric.is_successful() else 'FAIL'})")

        results.append(test_results)

    return results, metrics


def display_results(results):
    """Display detailed evaluation results."""
    print("\n" + "="*70)
    print(" DETAILED EVALUATION RESULTS")
    print("="*70 + "\n")

    # Calculate averages
    metric_names = ["Relevancy", "Completeness", "Technical Accuracy", "Actionability"]
    averages = {name: 0 for name in metric_names}

    for idx, result in enumerate(results, 1):
        print(f"Question {idx}:")
        print(f"  {result['question'][:70]}...")
        print()

        for metric_name in metric_names:
            if metric_name in result['scores']:
                score_data = result['scores'][metric_name]
                score = score_data['score']
                reason = score_data['reason']

                averages[metric_name] += score

                print(f"  {metric_name:20s}: {score:.2f}/1.00")
                print(f"    → {reason}")
                print()

        print("-" * 70)
        print()

    # Calculate and display averages
    print("="*70)
    print(" SUMMARY STATISTICS")
    print("="*70 + "\n")

    overall_avg = 0
    for metric_name, total in averages.items():
        avg = total / len(results)
        overall_avg += avg
        print(f"  {metric_name:20s}: {avg:.2f}/1.00")

    overall_avg /= len(metric_names)
    print(f"\n  {'OVERALL':20s}: {overall_avg:.2f}/1.00")
    print()
    print("="*70)


def save_results(results, output_file):
    """Save results to JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Calculate summary
    metric_names = ["Relevancy", "Completeness", "Technical Accuracy", "Actionability"]
    summary = {name: 0 for name in metric_names}

    for result in results:
        for metric_name in metric_names:
            if metric_name in result['scores']:
                summary[metric_name] += result['scores'][metric_name]['score']

    for metric_name in summary:
        summary[metric_name] /= len(results)

    summary['overall'] = sum(summary.values()) / len(summary)

    output_data = {
        "summary": summary,
        "detailed_results": results,
        "timestamp": datetime.now().isoformat()
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate swarm results using DeepEval with Claude metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:

  # Evaluate swarm results with Claude
  python3 evaluate_deepeval_claude.py ignored/swarm_results.json

  # Specify output file
  python3 evaluate_deepeval_claude.py ignored/swarm_results.json --output ignored/deepeval_results.json
        """
    )

    parser.add_argument(
        "results_file",
        help="Path to JSON file with swarm results"
    )

    parser.add_argument(
        "--output", "-o",
        default="ignored/deepeval_claude_evaluation.json",
        help="Output file for evaluation results"
    )

    args = parser.parse_args()

    # Check API key
    if not os.getenv("CLAUDE_API_KEY"):
        print("ERROR: CLAUDE_API_KEY not set in .env")
        sys.exit(1)

    # Check input file
    if not Path(args.results_file).exists():
        print(f"ERROR: Results file not found: {args.results_file}")
        sys.exit(1)

    print("\n" + "="*70)
    print(" ThinkTank Swarm - DeepEval with Claude")
    print("="*70 + "\n")

    # Load results
    swarm_results = load_swarm_results(args.results_file)

    # Create test cases
    print(f"\nCreating {len(swarm_results)} test cases...")
    test_cases = create_test_cases(swarm_results)
    print(f"✓ Created {len(test_cases)} test cases")

    # Evaluate
    results, metrics = evaluate_with_claude_metrics(test_cases)

    # Display results
    display_results(results)

    # Save results
    save_results(results, args.output)

    print("\n" + "="*70)
    print(" Evaluation Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
