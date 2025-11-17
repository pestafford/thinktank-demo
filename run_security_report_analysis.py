#!/usr/bin/env python3
"""
Run Security Report Analysis through ThinkTank Swarm
Combines prompt guidance with synthetic security report for comprehensive analysis

Produces confidence-based security assessment:
- >75%: Automatically tagged as "SECURE"
- 50-75%: Tagged as "HUMAN REVIEW REQUIRED"
- <50%: Automatically tagged as "INSECURE"
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

# Import ThinkTank components
from lib.persona_loader import load_personas, load_foreperson
from lib.swarm import Swarm
from lib.extension_loader import ExtensionLoader
from lib.config import EXTENSIONS_ENABLED

def load_prompt_and_report():
    """Load and combine security report prompt with the actual report."""

    # Load the prompt guidance
    prompt_file = Path("ignored/security_report_prompt.txt")
    with open(prompt_file, 'r') as f:
        prompt_guidance = f.read()

    # Load the synthetic security report
    report_file = Path("ignored/synthetic_security_report.md")
    with open(report_file, 'r') as f:
        security_report = f.read()

    # Combine them
    combined_prompt = f"""{prompt_guidance}

{security_report}"""

    return combined_prompt


def extract_report_metadata():
    """Extract metadata from the consolidated security report for display."""
    try:
        report_path = Path("ignored/mcp-consolidated-security-report.json")
        if report_path.exists():
            with open(report_path, 'r') as f:
                report_data = json.load(f)

            target = report_data.get('metadata', {}).get('target', 'Unknown Target')
            summary = report_data.get('summary', {})

            return {
                'target': target,
                'sast_findings': summary.get('sast_findings', 0),
                'critical_vulns': summary.get('critical_vulns', 0),
                'high_vulns': summary.get('high_vulns', 0),
                'medium_vulns': summary.get('medium_vulns', 0),
                'secrets_found': summary.get('secrets_found', 0)
            }
    except Exception as e:
        print(f"      ⚠ Could not load report metadata: {e}")

    # Fallback to generic display
    return {
        'target': 'Security Report Analysis',
        'sast_findings': 0,
        'critical_vulns': 0,
        'high_vulns': 0,
        'medium_vulns': 0,
        'secrets_found': 0
    }


def extract_confidence_score(consensus_text):
    """
    Extract confidence score from consensus text.

    Prioritizes finding the FINAL/CONSENSUS score, not intermediate scores.
    Looks from the end of the document backwards to find the final score.

    Returns:
        int: Confidence score (0-100), or None if not found
    """
    text_lower = consensus_text.lower()

    # Priority 1: Look for explicit "final" or "consensus" confidence score
    priority_patterns = [
        r'final\s+confidence[:\s]+(\d+)%?',
        r'consensus\s+confidence[:\s]+(\d+)%?',
        r'overall\s+confidence[:\s]+(\d+)%?',
        r'final\s+score[:\s]+(\d+)%?',
        r'consensus\s+score[:\s]+(\d+)%?',
        r'confidence\s+score[:\s]*[:-]?\s*(\d+)%',  # More specific pattern
    ]

    for pattern in priority_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            try:
                # Take the LAST match (most likely the final score)
                score = int(matches[-1])
                if 0 <= score <= 100:
                    return score
            except (ValueError, IndexError):
                continue

    # Priority 2: Look in the last 500 characters for any confidence score
    # (Final scores are usually at the end)
    last_section = text_lower[-500:]

    standard_patterns = [
        r'confidence[:\s]+(\d+)%',
        r'credence[:\s]+(\d+)%',
        r'(\d+)%\s+confidence',
    ]

    for pattern in standard_patterns:
        matches = re.findall(pattern, last_section, re.IGNORECASE)
        if matches:
            try:
                # Take the LAST match in the final section
                score = int(matches[-1])
                if 0 <= score <= 100:
                    return score
            except (ValueError, IndexError):
                continue

    # Priority 3: Fallback - search entire document but take LAST match
    for pattern in standard_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            try:
                # Take the LAST occurrence (most likely final score)
                score = int(matches[-1])
                if 0 <= score <= 100:
                    return score
            except (ValueError, IndexError):
                continue

    return None


def determine_security_tag(confidence_score):
    """
    Determine security tag based on confidence score.

    Args:
        confidence_score: Integer 0-100

    Returns:
        dict: {
            "tag": "SECURE" | "INSECURE" | "HUMAN_REVIEW_REQUIRED",
            "action": "auto_approve" | "manual_review" | "auto_reject",
            "color": "green" | "yellow" | "red"
        }
    """
    if confidence_score is None:
        return {
            "tag": "HUMAN_REVIEW_REQUIRED",
            "action": "manual_review",
            "color": "yellow",
            "reason": "Unable to extract confidence score from analysis"
        }

    if confidence_score > 75:
        return {
            "tag": "SECURE",
            "action": "auto_approve",
            "color": "green",
            "reason": f"High confidence ({confidence_score}%) in security posture"
        }
    elif confidence_score >= 50:
        return {
            "tag": "HUMAN_REVIEW_REQUIRED",
            "action": "manual_review",
            "color": "yellow",
            "reason": f"Moderate confidence ({confidence_score}%) requires human judgment"
        }
    else:
        return {
            "tag": "INSECURE",
            "action": "auto_reject",
            "color": "red",
            "reason": f"Low confidence ({confidence_score}%) indicates significant security concerns"
        }


def extract_key_findings(consensus_text):
    """Extract key security findings from consensus text."""
    findings = {
        "critical_issues": [],
        "medium_issues": [],
        "low_issues": [],
        "recommendations": []
    }

    # Simple extraction based on common patterns
    lines = consensus_text.split('\n')
    current_section = None

    for line in lines:
        line_lower = line.lower()

        if 'critical' in line_lower or 'blocker' in line_lower:
            current_section = 'critical_issues'
        elif 'medium' in line_lower or 'moderate' in line_lower:
            current_section = 'medium_issues'
        elif 'low' in line_lower or 'minor' in line_lower:
            current_section = 'low_issues'
        elif 'recommend' in line_lower:
            current_section = 'recommendations'

        # Extract bullet points or numbered items
        if current_section and (line.strip().startswith('-') or line.strip().startswith('•') or re.match(r'^\d+\.', line.strip())):
            findings[current_section].append(line.strip())

    return findings

def main():
    print("\n" + "="*70)
    print(" ThinkTank Swarm - Security Report Analysis")
    print("="*70 + "\n")

    # Load personas
    print("[1/5] Loading agent personas...")
    personas = load_personas('personas/personas.json')
    foreperson = load_foreperson('personas/foreperson.json')
    all_personas = personas + [foreperson]
    print(f"      Loaded {len(personas)} agents + foreperson")

    # Load extensions
    print("\n[2/5] Loading extensions...")
    extension_context = None
    if EXTENSIONS_ENABLED:
        loader = ExtensionLoader("extensions")
        loader.load_extensions()
        extensions = loader.list_extensions()

        if extensions:
            print(f"      Available: {', '.join(extensions)}")
            # Extension will activate on "security" keyword in prompt
        else:
            print("      No extensions found")
    else:
        print("      Extensions disabled")

    # Load prompt and report
    print("\n[3/5] Loading security report and analysis guidance...")
    combined_prompt = load_prompt_and_report()
    print(f"      Combined prompt length: {len(combined_prompt):,} characters")

    # Check if extension applies
    if EXTENSIONS_ENABLED:
        extension_context = loader.get_extension_context(combined_prompt)
        if extension_context:
            print(f"      ✓ MCP Security extension activated!")

    # Initialize swarm
    print("\n[4/5] Initializing swarm...")
    swarm = Swarm(all_personas, verbose=True)

    # Run multi-phase analysis
    print("\n[5/5] Running multi-phase deliberation...")
    print("      (This may take 5-10 minutes given the report complexity)\n")

    # Extract and display report metadata dynamically
    metadata = extract_report_metadata()
    total_vulns = metadata['critical_vulns'] + metadata['high_vulns'] + metadata['medium_vulns']

    print(f"{'='*70}")
    print(f"TARGET: {metadata['target']}")
    print(f"FINDINGS: {metadata['sast_findings']} SAST, {total_vulns} vulnerabilities, {metadata['secrets_found']} secrets")
    print(f"{'='*70}\n")

    consensus = swarm.run_multi_phase(
        combined_prompt,
        phases=3,
        extension_context=extension_context
    )

    # Display raw consensus
    print(f"\n{'='*70}")
    print(" " * 20 + "CONSENSUS REPORT")
    print(f"{'='*70}\n")
    print(consensus)
    print(f"\n{'='*70}\n")

    # Extract confidence score
    print("\n" + "="*70)
    print(" " * 15 + "CONFIDENCE-BASED ASSESSMENT")
    print("="*70 + "\n")

    confidence_score = extract_confidence_score(consensus)
    if confidence_score is not None:
        print(f"Extracted Confidence Score: {confidence_score}%")
    else:
        print("⚠ Could not extract confidence score from consensus")

    # Determine security tag
    security_assessment = determine_security_tag(confidence_score)

    # Display with color coding
    tag_display = {
        "green": "\033[92m",  # Green
        "yellow": "\033[93m", # Yellow
        "red": "\033[91m",    # Red
        "reset": "\033[0m"    # Reset
    }

    color = tag_display.get(security_assessment["color"], "")
    reset = tag_display["reset"]

    print(f"\n{color}╔{'═'*66}╗{reset}")
    print(f"{color}║{' '*20}SECURITY TAG: {security_assessment['tag']}{' '*(66-len(security_assessment['tag'])-35)}║{reset}")
    print(f"{color}╚{'═'*66}╝{reset}\n")

    print(f"Action: {security_assessment['action'].replace('_', ' ').title()}")
    print(f"Reason: {security_assessment['reason']}\n")

    # Extract key findings
    key_findings = extract_key_findings(consensus)

    # Save results to dedicated file in /ignored
    output_file = Path("ignored/security_report_swarm_analysis.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "prompt_summary": f"{metadata['target']} Security Assessment",
        "analysis_timestamp": datetime.now().isoformat(),
        "confidence_score": confidence_score,
        "security_assessment": security_assessment,
        "key_findings": key_findings,
        "consensus_report": consensus,
        "extension_used": extension_context is not None,
        "report_metadata": {
            "target": metadata['target'],
            "scanners_used": ["Semgrep", "Syft", "Trivy", "GitLeaks", "NPM Audit"]
        }
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("="*70)
    print(" " * 25 + "RESULTS SAVED")
    print("="*70)
    print(f"\n✓ JSON output: {output_file}")
    print(f"✓ Confidence score: {confidence_score}% " if confidence_score else "✓ Confidence score: Unable to extract")
    print(f"✓ Security tag: {security_assessment['tag']}")
    print(f"✓ Extension used: {extension_context is not None}")

    # Save markdown report with assessment header
    md_output_file = Path("ignored/security_report_swarm_analysis.md")
    with open(md_output_file, 'w') as f:
        f.write(f"# {metadata['target']} - ThinkTank Security Analysis\n\n")
        f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Target**: {metadata['target']}\n")
        f.write(f"**Confidence Score**: {confidence_score}%\n" if confidence_score else "**Confidence Score**: N/A\n")
        f.write(f"**Security Tag**: {security_assessment['tag']}\n")
        f.write(f"**Action**: {security_assessment['action'].replace('_', ' ').title()}\n\n")

        # Add visual indicator
        if security_assessment['tag'] == 'SECURE':
            f.write("✅ **STATUS**: APPROVED FOR DEPLOYMENT\n\n")
        elif security_assessment['tag'] == 'INSECURE':
            f.write("❌ **STATUS**: DEPLOYMENT BLOCKED\n\n")
        else:
            f.write("⚠️  **STATUS**: MANUAL SECURITY REVIEW REQUIRED\n\n")

        f.write(f"**Reasoning**: {security_assessment['reason']}\n\n")
        f.write("---\n\n")
        f.write("## Full Consensus Report\n\n")
        f.write(consensus)

    print(f"✓ Markdown report: {md_output_file}\n")

    # Final summary based on tag
    print("\n" + "="*70)
    if security_assessment['tag'] == 'SECURE':
        print(f"{color} ✅ DEPLOYMENT APPROVED - MCP server meets security threshold{reset}")
    elif security_assessment['tag'] == 'INSECURE':
        print(f"{color} ❌ DEPLOYMENT BLOCKED - Security concerns require remediation{reset}")
    else:
        print(f"{color} ⚠️  HUMAN REVIEW REQUIRED - Manual security assessment needed{reset}")
    print("="*70 + "\n")

    return output_data

if __name__ == "__main__":
    main()
