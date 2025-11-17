#!/bin/bash

#==============================================================================
# Clean Demo Outputs
# Removes all generated demo files for a fresh start
#==============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "========================================"
echo " Cleaning Demo Outputs"
echo "========================================"
echo ""

# Remove MCP demo directory
if [ -d "$SCRIPT_DIR/mcp-demo" ]; then
    echo "Removing mcp-demo/ directory..."
    rm -rf "$SCRIPT_DIR/mcp-demo"
    echo "  ✓ Removed mcp-demo/"
else
    echo "  • mcp-demo/ not found (already clean)"
fi

# Remove ThinkTank analysis outputs
echo ""
echo "Removing ThinkTank analysis outputs..."
rm -f "$SCRIPT_DIR/ignored/security_report_prompt.txt"
rm -f "$SCRIPT_DIR/ignored/synthetic_security_report.md"
rm -f "$SCRIPT_DIR/ignored/mcp-consolidated-security-report.json"
rm -f "$SCRIPT_DIR/ignored/security_report_swarm_analysis.json"
rm -f "$SCRIPT_DIR/ignored/security_report_swarm_analysis.md"
echo "  ✓ Removed ThinkTank outputs"

echo ""
echo "========================================"
echo " Clean Complete!"
echo "========================================"
echo ""
echo "Ready for fresh demo run:"
echo "  ./run_mcp_security_demo.sh"
echo ""
