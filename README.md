# Mifos Gazelle Demo Creator
This repo contains the code for the demo creator for Mifos Gazelle. Note this is currently WIP. 

branch main - is release/stable code

branch dev - is current development branch

All PR's must be to dev.  dev-->Main will be undertaken at release points

## Quick Setup

1. Clone the repository:

```bash
git clone https://github.com/openMF/mifos-gazelle-demo-creator.git
cd mifos-gazelle-demo-creator
```
2. Run the setup script:

```bash
bash scripts/setup.sh
```
This script checks for and installs the tools.

3. Install dependencies and run the application:

```bash
just install
just create-demo
```
The TUI will start.

## NOTES
This is currently Work in progress.