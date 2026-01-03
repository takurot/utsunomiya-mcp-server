# Utsunomiya Open Data MCP Server

This is an MCP (Model Context Protocol) server that provides access to Utsunomiya city's open data through natural language queries.

## Features

- List available datasets from Utsunomiya city
- Get schema information for specific datasets
- Query dataset contents with filtering
- Statistical analysis of dataset values
- Caching for improved performance

## Setup

1. Install dependencies: `pip install -e .`
2. Run the server: `python -m utsunomiya_mcp`

## Usage

The server provides several tools for interacting with Utsunomiya's open data:

- `list_datasets`: Get available datasets
- `get_dataset_schema`: Get schema information for a dataset
- `query_dataset`: Query dataset contents
- `analyze_dataset`: Get statistical analysis of a dataset