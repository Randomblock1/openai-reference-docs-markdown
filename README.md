# OpenAI Documentation Converter

A utility for scraping and converting OpenAI's documentation into markdown format, making it more accessible for AI agents and other applications.

## Prerequisites

- Python 3.x
- uv
- Bun & Node.js

## Installation

### Python Dependencies

Install the required Python package:

```bash
uv venv
.venv/Scripts/activate
uv sync
```

### JS Dependencies

```bash
bun install
```

## Usage

### Step 1: Scrape OpenAI documentation

Run the Python utility to download the latest OpenAI documentation:

```bash
# download and update the openai-docs-reference.js file
uv run js_downloader.py
```

after running the file, the folder downloaded_files is created by seleniumbase - it can be deleted.

### Step 2: Convert to Markdown

Before running the conversion utility, you may want to delete the output folder `openai-docs-api-reference` to ensure a clean generation.

Run the TypeScript converter:

```bash
bun run src/convertDocs.ts
```

This will generate markdown files in the `openai-docs-api-reference` directory.
