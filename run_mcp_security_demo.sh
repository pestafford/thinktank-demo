#!/bin/bash

#==============================================================================
# MCP Security Demo - Complete Pipeline with ThinkTank Analysis
# Demonstrates automated security scanning + AI-powered credence assessment
#==============================================================================

set -e  # Exit on error (except where explicitly handled)

# Terminal colors for better recording visibility
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration - Get absolute path to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEMO_DIR="$SCRIPT_DIR/mcp-demo"
MCP_REPO_URL="https://github.com/modelcontextprotocol/servers.git"
TARGET_SERVER="src/fetch"
THINKTANK_DIR="$SCRIPT_DIR"

# Debug: Show paths early
echo ""
echo "Script directory: $SCRIPT_DIR"
echo "Demo directory will be: $DEMO_DIR"
echo "Current directory: $(pwd)"
echo ""

#==============================================================================
# Helper Functions
#==============================================================================

print_header() {
    echo -e "\n${BOLD}${CYAN}========================================${NC}"
    echo -e "${BOLD}${CYAN} $1${NC}"
    echo -e "${BOLD}${CYAN}========================================${NC}\n"
}

print_step() {
    echo -e "${BOLD}${GREEN}[$1] $2${NC}"
}

print_info() {
    echo -e "${BLUE}      ℹ $1${NC}"
}

print_success() {
    echo -e "${GREEN}      ✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}      ⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}      ✗ $1${NC}"
}

pause_for_recording() {
    if [ "${RECORDING_MODE:-0}" == "1" ]; then
        sleep 2
    fi
}

check_tool() {
    if command -v $1 &> /dev/null; then
        print_success "$1 found: $(command -v $1)"
        return 0
    else
        print_error "$1 not found - please install it first"
        return 1
    fi
}

#==============================================================================
# Main Pipeline
#==============================================================================

print_header "MCP Security Demo - ThinkTank Credence Analysis"

echo -e "${BOLD}${MAGENTA}DEMO OBJECTIVE:${NC}"
echo "  Demonstrate ThinkTank's confidence-based security assessment"
echo "  Multi-agent AI analyzes security scan results and produces:"
echo "    → Confidence score (0-100%)"
echo "    → Automated tagging: SECURE / INSECURE / HUMAN REVIEW REQUIRED"
echo "    → Actionable deployment recommendations"
echo ""
echo -e "${BOLD}Pipeline:${NC}"
echo "  1. Automated security scanning (Semgrep, Trivy, GitLeaks, etc.)"
echo "  2. ThinkTank multi-agent deliberation"
echo "  3. Confidence-based deployment decision"
echo ""
echo -e "${YELLOW}Target: @modelcontextprotocol/server-fetch${NC}"
echo -e "${YELLOW}Attack Surface: SSRF, arbitrary URL fetching${NC}"
pause_for_recording

#==============================================================================
# Step 0: Prerequisites Check
#==============================================================================

print_header "Step 0: Checking Prerequisites"

TOOLS_OK=true

print_step "0/8" "Verifying security scanning tools..."
check_tool "semgrep" || TOOLS_OK=false
check_tool "syft" || TOOLS_OK=false
check_tool "trivy" || TOOLS_OK=false
check_tool "gitleaks" || TOOLS_OK=false
check_tool "jq" || TOOLS_OK=false
check_tool "npm" || TOOLS_OK=false
check_tool "git" || TOOLS_OK=false
check_tool "python3" || TOOLS_OK=false

if [ "$TOOLS_OK" = false ]; then
    print_error "Missing required tools. Please install them first:"
    echo ""
    echo "  brew install semgrep syft trivy gitleaks jq"
    echo ""
    exit 1
fi

print_success "All tools available!"
pause_for_recording

#==============================================================================
# Step 1: Environment Setup
#==============================================================================

print_header "Step 1: Setting Up Demo Environment"

print_step "1/8" "Creating demo directory structure..."
if mkdir -p "$DEMO_DIR"; then
    print_info "Created: $DEMO_DIR"
else
    print_error "Failed to create directory: $DEMO_DIR"
    exit 1
fi

if cd "$DEMO_DIR"; then
    print_success "Working directory: $(pwd)"
    print_info "Verified we are in: $DEMO_DIR"

    # CRITICAL: Verify we're inside thinktank-demo
    if [[ "$(pwd)" != *"thinktank-demo/mcp-demo"* ]]; then
        print_error "SAFETY CHECK FAILED: Not in thinktank-demo directory!"
        print_error "Current: $(pwd)"
        print_error "Expected to contain: thinktank-demo/mcp-demo"
        exit 1
    fi
else
    print_error "Failed to cd to: $DEMO_DIR"
    exit 1
fi
pause_for_recording

#==============================================================================
# Step 2: Clone Target Repository
#==============================================================================

print_header "Step 2: Acquiring Target MCP Server"

print_step "2/8" "Cloning MCP servers repository..."

# CRITICAL: Ensure we're in the right place before cloning
echo "Current directory before clone: $(pwd)"
if [[ "$(pwd)" != "$DEMO_DIR" ]]; then
    print_error "Not in correct directory before cloning!"
    print_error "Expected: $DEMO_DIR"
    print_error "Actual: $(pwd)"
    exit 1
fi

if [ ! -d "servers" ]; then
    print_info "Cloning from $MCP_REPO_URL into $(pwd)/servers"
    if git clone "$MCP_REPO_URL" servers; then
        print_success "Repository cloned to: $(pwd)/servers"
    else
        print_error "Failed to clone repository"
        exit 1
    fi
else
    print_info "Repository already exists at: $(pwd)/servers"
    if cd servers; then
        git pull --quiet
        cd ..
        print_success "Repository updated"
    else
        print_error "Failed to access servers directory"
        exit 1
    fi
fi

# Navigate to target
if [ -d "servers/$TARGET_SERVER" ]; then
    if cd "servers/$TARGET_SERVER"; then
        print_info "Target location: $(pwd)"

        # CRITICAL: Verify we're still in thinktank-demo
        if [[ "$(pwd)" != *"thinktank-demo/mcp-demo/servers"* ]]; then
            print_error "SAFETY CHECK FAILED: Navigated outside thinktank-demo!"
            print_error "Current: $(pwd)"
            exit 1
        fi
    else
        print_error "Failed to cd to servers/$TARGET_SERVER"
        exit 1
    fi
else
    print_error "Directory servers/$TARGET_SERVER does not exist"
    print_info "Available in servers/:"
    ls -la servers/
    exit 1
fi
pause_for_recording

print_step "2/8" "Installing dependencies..."
print_info "Running npm install (this may take 1-2 minutes)..."
if npm install; then
    print_success "Dependencies installed"
else
    print_error "npm install failed"
    exit 1
fi
pause_for_recording

#==============================================================================
# Step 3: Security Reports Directory
#==============================================================================

print_header "Step 3: Preparing Security Reports Directory"

print_step "3/8" "Creating reports directory..."

# Use absolute paths - no relative navigation
REPORTS_DIR="$DEMO_DIR/security-reports"
TARGET_PATH="$DEMO_DIR/servers/$TARGET_SERVER"

if mkdir -p "$REPORTS_DIR"; then
    print_info "Created: $REPORTS_DIR"
else
    print_error "Failed to create reports directory"
    exit 1
fi

if cd "$REPORTS_DIR"; then
    print_success "Reports directory: $(pwd)"
    print_info "Target path: $TARGET_PATH"

    # CRITICAL: Verify paths are within thinktank-demo
    if [[ "$REPORTS_DIR" != *"thinktank-demo/mcp-demo"* ]]; then
        print_error "SAFETY CHECK FAILED: Reports directory outside thinktank-demo!"
        exit 1
    fi
else
    print_error "Failed to cd to reports directory"
    exit 1
fi

pause_for_recording

#==============================================================================
# Step 4: SAST Scanning
#==============================================================================

print_header "Step 4: Static Application Security Testing (SAST)"

print_step "4/8" "Running Semgrep with security rulesets..."
print_info "Scanning for: SSRF, injection flaws, insecure patterns"
print_info "This may take 2-3 minutes on first run (downloading rules)..."
echo ""

if semgrep scan \
  --config=auto \
  --config="p/javascript" \
  --config="p/typescript" \
  --config="p/security-audit" \
  --json \
  --output sast-report.json \
  "$TARGET_PATH" 2>&1 | grep -v "^\s*$"; then
    print_success "Semgrep completed"
else
    print_warning "Semgrep had findings or warnings (this is normal)"
fi

SAST_COUNT=$(jq '.results | length' sast-report.json 2>/dev/null || echo "0")
print_success "SAST scan complete: ${SAST_COUNT} findings"
pause_for_recording

#==============================================================================
# Step 5: SBOM Generation & Vulnerability Scanning
#==============================================================================

print_header "Step 5: Software Bill of Materials & CVE Scanning"

print_step "5/8" "Generating SBOM with Syft..."
print_info "This may take 1-2 minutes for the first scan..."
print_info "Target: $TARGET_PATH"
echo ""

# Syft prefers absolute paths or dir: prefix
if syft "$TARGET_PATH" -o json=sbom.json; then
    SBOM_COUNT=$(jq '.artifacts | length' sbom.json 2>/dev/null || echo "0")
    print_success "SBOM generated: ${SBOM_COUNT} packages catalogued"
else
    print_error "Syft failed to generate SBOM"
    print_info "Attempting with dir: prefix..."
    if syft "dir:$TARGET_PATH" -o json=sbom.json; then
        SBOM_COUNT=$(jq '.artifacts | length' sbom.json 2>/dev/null || echo "0")
        print_success "SBOM generated: ${SBOM_COUNT} packages catalogued"
    else
        print_error "Syft failed with both methods"
        exit 1
    fi
fi
pause_for_recording

print_step "5/8" "Scanning for known vulnerabilities with Trivy..."
print_info "Trivy will download vulnerability database on first run..."
echo ""
if trivy sbom sbom.json --format json --output vuln-report.json; then
    print_success "Vulnerability scan complete"
else
    print_warning "Trivy scan had issues, continuing anyway..."
    echo '{"Results":[]}' > vuln-report.json
fi

# Count vulnerabilities by severity
CRIT_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' vuln-report.json 2>/dev/null || echo "0")
HIGH_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length' vuln-report.json 2>/dev/null || echo "0")
MED_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length' vuln-report.json 2>/dev/null || echo "0")
TOTAL_VULN=$((CRIT_COUNT + HIGH_COUNT + MED_COUNT))

echo ""
print_success "Vulnerability scan complete:"
echo -e "      ${RED}Critical: ${CRIT_COUNT}${NC}"
echo -e "      ${YELLOW}High: ${HIGH_COUNT}${NC}"
echo -e "      ${BLUE}Medium: ${MED_COUNT}${NC}"
echo -e "      Total: ${TOTAL_VULN}"
pause_for_recording

#==============================================================================
# Step 6: Secrets Detection
#==============================================================================

print_header "Step 6: Scanning for Exposed Secrets"

print_step "6/8" "Running GitLeaks to detect exposed credentials..."
echo ""
if gitleaks detect \
  --source "$TARGET_PATH" \
  --report-format json \
  --report-path secrets-report.json \
  --no-git 2>&1; then
    print_success "GitLeaks scan complete"
else
    # GitLeaks returns non-zero if it finds secrets OR if there's nothing to scan
    if [ ! -f secrets-report.json ]; then
        echo '[]' > secrets-report.json
    fi
    print_info "GitLeaks completed (exit code indicates findings or no git repo)"
fi

SECRET_COUNT=$(jq '. | length' secrets-report.json 2>/dev/null || echo "0")
if [ "$SECRET_COUNT" == "0" ]; then
    print_success "No exposed secrets found ✓"
else
    print_warning "${SECRET_COUNT} potential secrets detected"
fi
pause_for_recording

#==============================================================================
# Step 7: NPM Security Audit
#==============================================================================

print_header "Step 7: NPM Security Audit"

print_step "7/8" "Running npm audit..."
echo ""
cd "$TARGET_PATH"
npm audit --json > "$REPORTS_DIR/npm-audit.json" 2>&1 || true
cd "$REPORTS_DIR"

if [ -f npm-audit.json ]; then
    NPM_VULN=$(jq '.metadata.vulnerabilities | to_entries | map(.value) | add // 0' npm-audit.json 2>/dev/null || echo "0")
    print_success "NPM audit complete: ${NPM_VULN} total vulnerabilities"
else
    print_warning "NPM audit output not found"
    echo '{}' > npm-audit.json
fi
pause_for_recording

#==============================================================================
# Step 8: Report Consolidation
#==============================================================================

print_header "Step 8: Consolidating Security Reports"

print_step "8/8" "Merging all scan results into unified report..."

# Get tool versions
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
SEMGREP_VER=$(semgrep --version 2>/dev/null | head -n1 || echo "unknown")
SYFT_VER=$(syft version -o json 2>/dev/null | jq -r '.version' || echo "unknown")
TRIVY_VER=$(trivy --version 2>/dev/null | grep Version | awk '{print $2}' || echo "unknown")
GITLEAKS_VER=$(gitleaks version 2>/dev/null || echo "unknown")

# Create consolidated report
jq -n \
  --arg timestamp "$TIMESTAMP" \
  --arg semgrep_ver "$SEMGREP_VER" \
  --arg syft_ver "$SYFT_VER" \
  --arg trivy_ver "$TRIVY_VER" \
  --arg gitleaks_ver "$GITLEAKS_VER" \
  --slurpfile sast sast-report.json \
  --slurpfile sbom sbom.json \
  --slurpfile vuln vuln-report.json \
  --slurpfile secrets secrets-report.json \
  --slurpfile npm npm-audit.json \
  '{
    metadata: {
      target: "@modelcontextprotocol/server-fetch",
      repository: "https://github.com/modelcontextprotocol/servers",
      scan_timestamp: $timestamp,
      scanner_versions: {
        semgrep: $semgrep_ver,
        syft: $syft_ver,
        trivy: $trivy_ver,
        gitleaks: $gitleaks_ver
      }
    },
    reports: {
      sast: $sast[0],
      sbom: $sbom[0],
      vulnerabilities: $vuln[0],
      secrets: $secrets[0],
      npm_audit: $npm[0]
    },
    summary: {
      sast_findings: ($sast[0].results | length),
      total_packages: ($sbom[0].artifacts | length),
      critical_vulns: ([$vuln[0].Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length),
      high_vulns: ([$vuln[0].Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH")] | length),
      medium_vulns: ([$vuln[0].Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM")] | length),
      secrets_found: ($secrets[0] | length)
    }
  }' > consolidated-security-report.json

print_success "Consolidated report created"

# Generate executive summary
cat > executive-summary.txt << EOF
========================================
MCP SERVER SECURITY ASSESSMENT SUMMARY
========================================
Target: @modelcontextprotocol/server-fetch
Scan Date: $(date)
Repository: https://github.com/modelcontextprotocol/servers

FINDINGS OVERVIEW:
------------------
SAST Findings:         ${SAST_COUNT}
Known Vulnerabilities: ${TOTAL_VULN}
Exposed Secrets:       ${SECRET_COUNT}
Total Packages:        ${SBOM_COUNT}

SEVERITY BREAKDOWN:
-------------------
  Critical: ${CRIT_COUNT}
  High:     ${HIGH_COUNT}
  Medium:   ${MED_COUNT}

SCANNER VERSIONS:
-----------------
  Semgrep:  ${SEMGREP_VER}
  Syft:     ${SYFT_VER}
  Trivy:    ${TRIVY_VER}
  GitLeaks: ${GITLEAKS_VER}

NEXT STEPS:
-----------
1. Review detailed findings in consolidated-security-report.json
2. Run ThinkTank analysis for credence assessment
3. Evaluate deployment readiness

Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
========================================
EOF

print_success "Executive summary generated"
pause_for_recording

#==============================================================================
# Display Results
#==============================================================================

print_header "Security Scan Complete - Results Summary"

cat executive-summary.txt

pause_for_recording

#==============================================================================
# Sample SAST Findings (for demo)
#==============================================================================

print_header "Sample SAST Findings"

echo -e "${BOLD}Top security findings from Semgrep:${NC}\n"
jq -r '.results[0:5]? | .[] | "  • [\(.extra.severity)] \(.check_id)\n    \(.extra.message)\n    Location: \(.path):\(.start.line)\n"' sast-report.json 2>/dev/null || echo "  No findings to display"

pause_for_recording

#==============================================================================
# ThinkTank Analysis Setup
#==============================================================================

print_header "Preparing ThinkTank Analysis"

print_info "Creating ThinkTank-compatible prompt..."

# Create prompt for ThinkTank
cat > thinktank-analysis-prompt.md << 'EOF'
# Security Analysis Request for ThinkTank Credence

## Task
Analyze the consolidated security scan results for the @modelcontextprotocol/server-fetch MCP server and provide a confidence-based security assessment for production deployment.

## Input Data
The attached consolidated-security-report.json contains:
- SAST findings from Semgrep (JavaScript/TypeScript security patterns)
- Software Bill of Materials (SBOM) from Syft
- Known vulnerability analysis from Trivy (CVE database)
- Secrets scanning results from GitLeaks
- NPM security audit results

## Critical Analysis Question
**What is your confidence (0-100%) that this MCP server is safe for production deployment?**

⚠️ **IMPORTANT**: Your final consensus MUST include an explicit confidence score as a percentage.

## Confidence-Based Decision Framework

Based on your analysis, the system will automatically:
- **>75% confidence**: Tag as "SECURE" → Auto-approve deployment
- **50-75% confidence**: Tag as "HUMAN REVIEW REQUIRED" → Alert security team
- **<50% confidence**: Tag as "INSECURE" → Block deployment

## Required Analysis Framework

### Agent Perspectives Required:
1. **Security Hardening Perspective** (Conservative)
   - Focus on identified vulnerabilities and their exploitability
   - Assess SSRF risks and attack surface
   - Evaluate dependency security posture
   - Consider worst-case scenarios
   - Provide individual confidence score with justification

2. **Risk Pragmatist Perspective** (Balanced)
   - Weigh severity against likelihood of exploitation
   - Consider MCP protocol-level mitigations
   - Assess practical attack scenarios
   - Evaluate cost/benefit of deployment vs. remediation
   - Provide individual confidence score with justification

3. **Operational Context Perspective** (Use-Case Focused)
   - Consider intended use case and threat model
   - Evaluate organizational risk tolerance
   - Assess compensating controls availability
   - Review deployment environment security
   - Provide individual confidence score with justification

### Output Requirements:
1. **Individual agent confidence scores (0-100%) with detailed reasoning**
2. Key areas of agreement and disagreement between perspectives
3. Critical security findings requiring immediate attention
4. Medium-priority findings for security roadmap
5. Low-risk or false positive findings that can be accepted
6. **Final consensus confidence score (0-100%) - REQUIRED**
7. Specific recommendations:
   - Immediate deployment blockers (if any)
   - Required remediation before deployment
   - Recommended compensating controls
   - Ongoing monitoring requirements

### Debate Focus Areas:
- Is SSRF risk acceptable given MCP's intended use case?
- Are the identified dependency vulnerabilities actually exploitable in this context?
- Do the benefits of deployment outweigh the identified risks?
- What specific gaps exist between current state and "production ready"?
- Which findings are theoretical vs. practically exploitable?

## Expected Output Format

Your consensus report MUST include:

1. **Executive Summary** with clear confidence score statement
   - Example: "Confidence Score: 65% - Manual review recommended"

2. **Individual Agent Assessments**
   - Each agent's confidence score and reasoning
   - Areas of agreement and contention

3. **Security Findings Analysis**
   - Critical issues (deployment blockers)
   - Medium issues (security debt)
   - Low issues (acceptable risk)
   - False positives (can ignore)

4. **Deployment Recommendation**
   - Clear go/no-go/review recommendation
   - Specific action items
   - Timeline for remediation (if needed)

5. **Final Confidence Score**: X%
   - State this explicitly at the end
   - Justify the score based on debate consensus

Remember: The confidence score drives automated decision-making. Be precise and justify your assessment thoroughly.
EOF

print_success "ThinkTank prompt created: thinktank-analysis-prompt.md"

# Convert consolidated report to markdown for ThinkTank
cat > mcp-security-report-for-thinktank.md << 'EOF'
# MCP Fetch Server - Consolidated Security Report

## Executive Summary
EOF

cat executive-summary.txt >> mcp-security-report-for-thinktank.md

cat >> mcp-security-report-for-thinktank.md << 'EOF'

## Detailed Findings

### SAST Findings (Semgrep)
EOF

echo -e "\nTop 10 security issues:\n" >> mcp-security-report-for-thinktank.md
jq -r '.results[0:10]? | .[] | "**[\(.extra.severity)] \(.check_id)**\n- Message: \(.extra.message)\n- Location: \(.path):\(.start.line)\n- CWE: \(.extra.metadata.cwe[0]? // "N/A")\n"' sast-report.json >> mcp-security-report-for-thinktank.md 2>/dev/null || echo "No SAST findings" >> mcp-security-report-for-thinktank.md

cat >> mcp-security-report-for-thinktank.md << 'EOF'

### Known Vulnerabilities (CVEs)
EOF

jq -r '.Results[]?.Vulnerabilities[0:10]? | .[] | "**\(.VulnerabilityID)** - \(.Title // "No title")\n- Severity: \(.Severity)\n- Package: \(.PkgName)@\(.InstalledVersion)\n- Fixed: \(.FixedVersion // "No fix available")\n- Description: \(.Description[0:200] // "N/A")\n"' vuln-report.json >> mcp-security-report-for-thinktank.md 2>/dev/null || echo "No vulnerabilities found" >> mcp-security-report-for-thinktank.md

print_success "Markdown report created for ThinkTank analysis"

#==============================================================================
# File Outputs Summary
#==============================================================================

print_header "Generated Files"

echo -e "${BOLD}All reports saved in:${NC} ${CYAN}./mcp-demo/security-reports/${NC}\n"
ls -lh *.json *.txt *.md 2>/dev/null | awk '{printf "  %-40s %10s\n", $9, $5}'

echo ""
print_success "Security scanning pipeline complete!"

#==============================================================================
# ThinkTank Integration
#==============================================================================

print_header "Running ThinkTank Credence Analysis"

echo -e "${BOLD}${CYAN}This is the core of the demo:${NC}"
echo "  • Multi-agent security assessment"
echo "  • Confidence-based decision making"
echo "  • Automated SECURE/INSECURE/REVIEW tagging"
echo ""
pause_for_recording

# Copy files to ThinkTank directory
print_step "TT/1" "Copying reports to ThinkTank directory..."
mkdir -p "$THINKTANK_DIR/ignored"

# Create the security report prompt
cat thinktank-analysis-prompt.md > "$THINKTANK_DIR/ignored/security_report_prompt.txt"

# Copy the markdown report as the synthetic report
cp mcp-security-report-for-thinktank.md "$THINKTANK_DIR/ignored/synthetic_security_report.md"

# Also copy the JSON for reference
cp consolidated-security-report.json "$THINKTANK_DIR/ignored/mcp-consolidated-security-report.json"

print_success "Reports copied to ThinkTank directory"

# Activate virtual environment and run analysis
print_step "TT/2" "Activating virtual environment and running analysis..."
echo ""

cd "$THINKTANK_DIR"

# Check if venv exists
if [ ! -d "$THINKTANK_DIR/venv" ]; then
    print_error "Virtual environment not found at ./venv"
    print_info "Please create it first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate and run
source "$THINKTANK_DIR/venv/bin/activate"

print_info "Running ThinkTank multi-agent deliberation..."
print_info "Agents will debate exploitability, context, and risk..."
print_info "This may take 5-10 minutes depending on report complexity"
echo ""
pause_for_recording

python3 run_security_report_analysis.py

deactivate

print_header "Demo Complete!"

echo -e "${GREEN}✓ Security scanning complete${NC}"
echo -e "${GREEN}✓ ThinkTank analysis complete${NC}"
echo -e "${GREEN}✓ Confidence-based tagging applied${NC}"
echo ""
echo -e "${BOLD}Results:${NC}"
echo "  • Security reports: ./mcp-demo/security-reports/"
echo "  • ThinkTank analysis: ./ignored/security_report_swarm_analysis.md"
echo "  • JSON results: ./ignored/security_report_swarm_analysis.json"
echo ""

print_header "Demo Recording Ready!"

echo -e "${BOLD}${GREEN}All files are ready for demo recording.${NC}\n"
echo "Security reports location:"
echo "  ${CYAN}./mcp-demo/security-reports/${NC}"
echo ""
echo "Key files for demo:"
echo "  • executive-summary.txt - Quick overview"
echo "  • consolidated-security-report.json - Complete findings"
echo "  • thinktank-analysis-prompt.md - AI analysis prompt"
echo ""
echo -e "${YELLOW}Recording tips:${NC}"
echo "  • cd mcp-demo/security-reports/"
echo "  • cat executive-summary.txt - Show findings"
echo "  • jq .summary consolidated-security-report.json - JSON view"
echo "  • cat ../../ignored/security_report_swarm_analysis.md - ThinkTank results"
echo ""
echo -e "${BOLD}Demo complete! 🎬${NC}\n"
