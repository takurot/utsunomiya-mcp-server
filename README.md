# Utsunomiya Open Data MCP Server

This is an MCP (Model Context Protocol) server that provides access to Utsunomiya city's open data through natural language queries.

## Features

- List available datasets from Utsunomiya city
- Get schema information for specific datasets
- Query dataset contents with filtering
- Statistical analysis of dataset values
- Caching for improved performance

## Setup

1. Install via pip: `pip install utsunomiya-mcp-server`
2. Run directly: `utsunomiya-mcp`

### Usage with Claude Desktop

Add the following configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "utsunomiya-open-data": {
      "command": "uvx",
      "args": [
        "--from",
        "utsunomiya-mcp-server",
        "utsunomiya-mcp"
      ]
    }
  }
}
```

Or if you installed it via pip in a specific environment:

```json
{
  "mcpServers": {
    "utsunomiya-open-data": {
      "command": "utsunomiya-mcp",
      "args": []
    }
  }
}
```

## Usage

The server provides several tools for interacting with Utsunomiya's open data:

- `list_datasets`: Get available datasets
- `get_dataset_schema`: Get schema information for a dataset
- `query_dataset`: Query dataset contents
- `analyze_dataset`: Get statistical analysis of a dataset