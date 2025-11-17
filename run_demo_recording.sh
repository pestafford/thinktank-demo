#!/bin/bash

#==============================================================================
# MCP Security Demo - Recording Version (No API Required)
# Uses existing ThinkTank analysis for seamless demo
#==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEMO_DIR="$SCRIPT_DIR/mcp-demo"

# Helper functions
print_header() {
    echo -e "\n${BOLD}${CYAN}========================================${NC}"
    echo -e "${BOLD}${CYAN} $1${NC}"
    echo -e "${BOLD}${CYAN}========================================${NC}\n"
    sleep 1
}

print_step() {
    echo -e "${BOLD}${GREEN}[$1] $2${NC}"
    sleep 0.5
}

print_info() {
    echo -e "${BLUE}      ℹ $1${NC}"
}

print_success() {
    echo -e "${GREEN}      ✓ $1${NC}"
    sleep 0.3
}

pause_demo() {
    if [ "${DEMO_MODE:-1}" == "1" ]; then
        sleep 2
    fi
}

#==============================================================================
# Main Demo
#==============================================================================

clear

print_header "ThinkTank Security Demo - Live Recording"

echo -e "${BOLD}${MAGENTA}OBJECTIVE:${NC}"
echo "  Demonstrate AI-powered confidence-based security assessment"
echo "  Pipeline: Security Scans → ThinkTank Analysis → Deployment Decision"
echo ""

# Extract target name from report if available
TARGET_NAME="Security Target"
if [ -f "$DEMO_DIR/security-reports/consolidated-security-report.json" ]; then
    TARGET_NAME=$(jq -r '.metadata.target // "Security Target"' "$DEMO_DIR/security-reports/consolidated-security-report.json" 2>/dev/null || echo "Security Target")
fi

echo -e "${YELLOW}Target: $TARGET_NAME${NC}"
echo -e "${YELLOW}Demo Mode: Recording-optimized (using cached analysis)${NC}"
pause_demo

#==============================================================================
# Part 1: Show Existing Security Reports
#==============================================================================

print_header "Part 1: Security Scan Results"

print_step "1/3" "Loading consolidated security report..."

if [ -f "$DEMO_DIR/security-reports/consolidated-security-report.json" ]; then
    print_success "Security scan data loaded"
    echo ""

    # Show summary
    echo -e "${BOLD}Scan Summary:${NC}"
    jq -r '.summary | to_entries | .[] | "  \(.key): \(.value)"' "$DEMO_DIR/security-reports/consolidated-security-report.json" 2>/dev/null || echo "  [Scan results available]"
    echo ""
    pause_demo
else
    print_info "No existing security reports found"
    print_info "Run ./run_mcp_security_demo.sh first to generate scan data"
    echo ""
    exit 1
fi

#==============================================================================
# Part 2: Show ThinkTank Analysis (Pre-generated)
#==============================================================================

print_header "Part 2: ThinkTank Multi-Agent Analysis"

print_step "2/3" "Loading ThinkTank consensus analysis..."
sleep 1

if [ -f "$SCRIPT_DIR/ignored/security_report_swarm_analysis.json" ]; then
    print_success "ThinkTank analysis loaded"
    echo ""

    # Extract key info
    CONFIDENCE=$(jq -r '.confidence_score // "N/A"' "$SCRIPT_DIR/ignored/security_report_swarm_analysis.json")
    TAG=$(jq -r '.security_assessment.tag // "UNKNOWN"' "$SCRIPT_DIR/ignored/security_report_swarm_analysis.json")
    ACTION=$(jq -r '.security_assessment.action // "unknown"' "$SCRIPT_DIR/ignored/security_report_swarm_analysis.json")

    echo -e "${BOLD}Multi-Agent Deliberation Complete:${NC}"
    echo "  • Conservative security perspective analyzed"
    echo "  • Pragmatic risk assessment completed"
    echo "  • Operational context evaluated"
    echo ""
    pause_demo

else
    print_info "No existing ThinkTank analysis found"
    echo ""
    echo "To generate analysis, you need:"
    echo "  1. Claude API credits"
    echo "  2. Run: python3 run_security_report_analysis.py"
    echo ""
    exit 1
fi

#==============================================================================
# Part 3: Display Confidence-Based Decision
#==============================================================================

print_header "Part 3: Confidence-Based Security Decision"

print_step "3/3" "Extracting confidence score and security tag..."
sleep 1

echo ""
echo -e "${BOLD}Confidence Score Extracted: ${CYAN}${CONFIDENCE}%${NC}"
echo ""
sleep 1

# Display tag with color
if [ "$TAG" == "SECURE" ]; then
    COLOR=$GREEN
    SYMBOL="✅"
elif [ "$TAG" == "INSECURE" ]; then
    COLOR=$RED
    SYMBOL="❌"
else
    COLOR=$YELLOW
    SYMBOL="⚠️"
fi

echo -e "${COLOR}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${COLOR}║${NC}                    ${BOLD}SECURITY TAG: ${TAG}${NC}                    ${COLOR}║${NC}"
echo -e "${COLOR}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Display action
ACTION_DISPLAY=$(echo "$ACTION" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
echo -e "${BOLD}Recommended Action:${NC} $ACTION_DISPLAY"
echo ""

# Get reasoning
REASONING=$(jq -r '.security_assessment.reason // "See full report for details"' "$SCRIPT_DIR/ignored/security_report_swarm_analysis.json")
echo -e "${BOLD}Reasoning:${NC}"
echo "  $REASONING"
echo ""
pause_demo

#==============================================================================
# Final Summary
#==============================================================================

print_header "Demo Summary"

echo -e "${SYMBOL} ${BOLD}Final Assessment:${NC}"
if [ "$TAG" == "SECURE" ]; then
    echo -e "${GREEN}  Deployment APPROVED - High confidence in security posture${NC}"
elif [ "$TAG" == "INSECURE" ]; then
    echo -e "${RED}  Deployment BLOCKED - Significant security concerns identified${NC}"
else
    echo -e "${YELLOW}  Human review REQUIRED - Manual security assessment needed${NC}"
fi

echo ""
echo -e "${BOLD}Key Demo Points:${NC}"
echo "  ✓ Automated security scanning (SAST, SBOM, CVE, Secrets)"
echo "  ✓ Multi-agent AI analysis with diverse perspectives"
echo "  ✓ Confidence-based decision making (0-100% scale)"
echo "  ✓ Automated tagging: SECURE / INSECURE / REVIEW"
echo ""

echo -e "${BOLD}Output Files:${NC}"
echo "  • Security Reports: ${CYAN}./mcp-demo/security-reports/${NC}"
echo "  • ThinkTank Analysis: ${CYAN}./ignored/security_report_swarm_analysis.md${NC}"
echo "  • JSON Results: ${CYAN}./ignored/security_report_swarm_analysis.json${NC}"
echo ""

print_header "Demo Complete! 🎬"

echo "To view detailed ThinkTank analysis:"
echo -e "  ${CYAN}cat ignored/security_report_swarm_analysis.md${NC}"
echo ""
echo "To view full scan results:"
echo -e "  ${CYAN}jq . mcp-demo/security-reports/consolidated-security-report.json${NC}"
echo ""
