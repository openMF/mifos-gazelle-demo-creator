# Demo Examples

This directory contains example demo files created using the Mifos Gazelle Demo Creator TUI.

## Customer Onboarding Demo

**File**: `customer_onboarding_demo.json`

A 4-step customer onboarding flow demonstrating:
1. Welcome page introduction
2. Personal details collection
3. Document upload process
4. Confirmation and submission

**Created for**: GAZ-211 issue
**Tags**: onboarding, demo5

## How to Use

1. Run the demo creator: `uv run python main.py`
2. Use "Create Demo" to build similar demos
3. Export demos to JSON format
4. Upload to Artifactory using the TUI

## Demo Structure

Each demo JSON contains:
- `demoId`: Unique identifier
- `demoName`: Display name
- `steps`: Numbered steps with title, URL, and details
- `tags`: Categorization tags
- `demoDescription`: Brief description