# Demo Examples for GAZ-211

This directory contains the customer onboarding demo created for the GAZ-211 task.

## Task: Demo 5 - Create your own Demo

**Requirement**: Design a demo using Gazelle components for a use case, created using Mifos-Gazelle Demo Creator and visible in Demo-Runtime.

## Customer Onboarding Demo

**File**: `customer_onboarding_demo.json`  
**Use Case**: New customer registration workflow for financial services

### Demo Flow:
1. **Welcome** - Introduction and overview
2. **Personal Details** - Customer information collection  
3. **Document Upload** - Identity verification
4. **Confirmation** - Review and submission

### Technical Details:
- **Demo ID**: `5bc9ad4e-6d7b-4701-941a-5293d0654139`
- **Steps Count**: 4
- **Tags**: `onboarding`, `demo5`
- **Format**: Standard Mifos Gazelle Demo JSON structure

## Testing Instructions

1. **Load in Demo Creator**:
   ```bash
   uv run python main.py
   ```

2. **Import Demo**: Use the TUI to load `customer_onboarding_demo.json`

3. **Verify Structure**: Check all steps, URLs, and metadata

4. **Deploy to Runtime**: Upload via TUI for Demo-Runtime visibility

## Compliance

✅ Uses existing Mifos Gazelle Demo Creator  
✅ Follows standard demo JSON format  
✅ No core code modifications  
✅ No additional dependencies  
✅ Ready for Demo-Runtime deployment

## JSON Structure

```json
{
  "demoId": "unique-identifier",
  "demoName": "Display name", 
  "steps": {
    "1": { "title": "Step name", "url": "/path", "details": "Description" }
  },
  "tags": ["category", "type"],
  "demoDescription": "Brief overview"
}
```