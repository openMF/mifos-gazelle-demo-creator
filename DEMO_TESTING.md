# Demo Testing Guide

## Customer Onboarding Demo - GAZ-211

This document explains how to test the customer onboarding demo created for GAZ-211.

### Demo Location
- **Demo File**: `demo_examples/customer_onboarding_demo.json`
- **Documentation**: `demo_examples/README.md`

### Demo Details
- **Name**: Customer Onboarding Demo
- **Use Case**: New customer registration workflow
- **Steps**: 4 (Welcome → Personal Details → Document Upload → Confirmation)
- **Tags**: onboarding, demo5

### Testing with Demo Creator TUI

1. **Run the TUI application**:
   ```bash
   uv run python main.py
   ```

2. **Load the demo**:
   - Use "Create Demo" or import functionality
   - Load the JSON file from `demo_examples/customer_onboarding_demo.json`

3. **Verify demo structure**:
   - Check all 4 steps are loaded correctly
   - Verify URLs and descriptions
   - Confirm tags are applied

### Demo Workflow
1. **Welcome** (`/onboarding/welcome`) - Introduction page
2. **Personal Details** (`/onboarding/personal-info`) - Name, age, phone collection
3. **Document Upload** (`/onboarding/doc-upload`) - Identity document upload
4. **Confirmation** (`/onboarding/confirmation`) - Review and submit

### Integration with Demo Runtime
This demo is designed to work with the existing Mifos Gazelle Demo Runtime system once uploaded through the TUI application.

### No Core Changes
This contribution only adds demo files and documentation. No modifications to:
- Installation scripts
- Core application code
- Dependencies
- Build system