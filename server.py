"""
Utsunomiya Open Data MCP Server

An MCP server that provides access to Utsunomiya city's open data through natural language queries.
"""
import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from fastmcp import FastMCP
from pydantic import BaseModel
import chardet
import urllib3

# Disable insecure request warnings when SSL verification is disabled
# Disable insecure request warnings when SSL verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CKAN_API_BASE = "https://catalog.city.utsunomiya.tochigi.jp/api/3/action"


# Create a temporary directory for caching
CACHE_DIR = os.path.join(tempfile.gettempdir(), "utsunomiya_mcp_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Load the catalog of datasets from JSON file
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "catalog.json")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG = json.load(f)

# Create FastMCP server
mcp = FastMCP("utsunomiya-open-data-server")


class Dataset(BaseModel):
    id: str
    name: str
    url: str
    format: str
    encoding: str
    description: str
    verify_ssl: bool = True


class FilterParams(BaseModel):
    dataset_id: str
    limit: Optional[int] = 100
    filter_column: Optional[str] = None
    filter_value: Optional[str] = None


class StatisticalAnalysisResult(BaseModel):
    dataset_id: str
    total_rows: int
    total_columns: int
    numeric_columns: List[str]
    statistics: Dict[str, Dict[str, float]]  # column -> {stat_name -> value}
    categorical_summary: Dict[str, Dict[str, int]]  # column -> {value -> count}


def get_cached_data(dataset_id: str) -> Optional[pd.DataFrame]:
    """Get cached data if it exists and is not expired (less than 24 hours old)."""
    cache_file = os.path.join(CACHE_DIR, f"{dataset_id}.pkl")
    if os.path.exists(cache_file):
        # Check if cache is less than 24 hours old
        cache_time = os.path.getmtime(cache_file)
        if datetime.fromtimestamp(cache_time) > datetime.now() - timedelta(hours=24):
            try:
                return pd.read_pickle(cache_file)
            except Exception:
                # If there's an error reading the cache, remove the file and return None
                os.remove(cache_file)
    return None


def cache_data(dataset_id: str, df: pd.DataFrame):
    """Cache the data to a file."""
    cache_file = os.path.join(CACHE_DIR, f"{dataset_id}.pkl")
    df.to_pickle(cache_file)


def load_dataset(dataset_id: str) -> pd.DataFrame:
    """Load a dataset from URL or cache."""
    # Find the dataset in the catalog
    dataset_info = None
    for ds in CATALOG["datasets"]:
        if ds["id"] == dataset_id:
            dataset_info = ds
            break

    if dataset_info is None:
        # Try fetching from CKAN
        try:
            response = requests.get(f"{CKAN_API_BASE}/package_show", params={"id": dataset_id})
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    package = data["result"]
                    # Find a CSV resource
                    csv_resource = next((r for r in package["resources"] if r["format"].upper() == "CSV"), None)
                    if csv_resource:
                        dataset_info = {
                            "id": package["id"],
                            "name": package["title"],
                            "url": csv_resource["url"],
                            "format": "csv",
                            "description": package.get("notes", ""),
                            # Encoding will be detected automatically
                        }
        except Exception:
            # Ignore errors and fall through to raise ValueError
            pass

    if dataset_info is None:
        raise ValueError(f"Dataset with ID '{dataset_id}' not found in catalog or CKAN")

    # Check if we have cached data
    cached_df = get_cached_data(dataset_id)
    if cached_df is not None:
        return cached_df

    # Determine if the URL is local or remote
    url = dataset_info["url"]
    if url.startswith(('http://', 'https://')):
        # Remote URL - download the data
        verify_ssl = dataset_info.get("verify_ssl", True)
        response = requests.get(url, verify=verify_ssl)
        response.raise_for_status()

        # Detect encoding if not specified
        encoding = dataset_info.get("encoding", "utf-8")
        if not dataset_info.get("encoding"):
            detected = chardet.detect(response.content)
            encoding = detected["encoding"] or "utf-8"

        # Load the data based on format
        if dataset_info["format"] == "csv":
            df = pd.read_csv(
                pd.io.common.BytesIO(response.content),
                encoding=encoding,
                on_bad_lines="skip"
            )
        else:
            raise ValueError(f"Unsupported format: {dataset_info['format']}")
    else:
        # Local file
        encoding = dataset_info.get("encoding", "utf-8")
        if dataset_info["format"] == "csv":
            df = pd.read_csv(url, encoding=encoding)
        else:
            raise ValueError(f"Unsupported format: {dataset_info['format']}")

    # Cache the data
    cache_data(dataset_id, df)

    return df


@mcp.tool()
def list_datasets() -> List[Dict[str, Any]]:
    """List available datasets from Utsunomiya city.
    
    Returns a list of available datasets with their IDs, names, and descriptions.
    Use this to discover what data is available before querying.
    """
    result = []
    for ds in CATALOG["datasets"]:
        result.append({
            "id": ds["id"],
            "name": ds["name"],
            "description": ds["description"]
        })
    return result


@mcp.tool()
def search_datasets(query: str) -> List[Dict[str, Any]]:
    """Search for datasets in the Utsunomiya Open Data Catalog.
    
    Args:
        query: Search query string (e.g., "population", "AED").
        
    Returns:
        List of found datasets with ID, title, and description.
    """
    try:
        response = requests.get(f"{CKAN_API_BASE}/package_search", params={"q": query, "rows": 10})
        response.raise_for_status()
        data = response.json()
        
        results = []
        if data.get("success"):
            for package in data["result"]["results"]:
                # Check if it has a CSV resource
                has_csv = any(r["format"].upper() == "CSV" for r in package["resources"])
                
                results.append({
                    "id": package["id"],
                    "name": package["title"],
                    "description": package.get("notes", "")[:100] + "..." if package.get("notes") else "",
                    "has_csv": has_csv,
                    "url": f"https://catalog.city.utsunomiya.tochigi.jp/dataset/{package['name']}"
                })
        return results
    except Exception as e:
        return [{"error": f"Failed to search datasets: {str(e)}"}]


@mcp.tool()
def get_dataset_schema(dataset_id: str) -> Dict[str, Any]:
    """Get schema information for a specific dataset.
    
    Args:
        dataset_id: The ID of the dataset to get schema for.
        
    Returns schema including column names, types, total rows, and sample data.
    """
    df = load_dataset(dataset_id)
    
    # Get column names and types
    columns = []
    for col in df.columns:
        col_type = str(df[col].dtype)
        columns.append({
            "name": col,
            "type": col_type
        })
    
    # Get sample data (first 3 rows)
    sample_data = df.head(3).to_dict(orient="records")
    
    return {
        "dataset_id": dataset_id,
        "columns": columns,
        "total_rows": len(df),
        "sample_data": sample_data
    }


@mcp.tool()
def query_dataset(
    dataset_id: str,
    limit: int = 100,
    filter_column: Optional[str] = None,
    filter_value: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query dataset contents with optional filtering.
    
    Args:
        dataset_id: The ID of the dataset to query.
        limit: Maximum number of rows to return (default: 100).
        filter_column: Optional column name to filter on.
        filter_value: Optional value to filter for (partial match supported).
        
    Returns a list of matching records.
    """
    df = load_dataset(dataset_id)
    
    # Apply filtering if specified
    if filter_column and filter_value:
        df = df[df[filter_column].astype(str).str.contains(filter_value, na=False)]
    
    # Apply limit
    if limit:
        df = df.head(limit)
    
    # Convert to list of dictionaries
    result = df.to_dict(orient="records")
    
    return result


@mcp.tool()
def analyze_dataset(dataset_id: str) -> Dict[str, Any]:
    """Perform statistical analysis on a dataset.
    
    Args:
        dataset_id: The ID of the dataset to analyze.
        
    Returns statistics for numeric columns and value counts for categorical columns.
    """
    df = load_dataset(dataset_id)
    
    # Identify numeric and categorical columns
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Calculate statistics for numeric columns
    statistics = {}
    for col in numeric_columns:
        series = df[col].dropna()  # Remove NaN values for calculations
        if len(series) > 0:
            stats = {
                "count": int(series.count()),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
                "median": float(series.median()),
                "q25": float(series.quantile(0.25)),
                "q75": float(series.quantile(0.75))
            }
            statistics[col] = stats
    
    # Calculate value counts for categorical columns (limit to top 10 values to prevent large responses)
    categorical_summary = {}
    for col in categorical_columns:
        value_counts = df[col].value_counts().head(10)  # Top 10 most common values
        categorical_summary[col] = {str(k): int(v) for k, v in value_counts.items()}
    
    # Prepare the result
    result = {
        "dataset_id": dataset_id,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "statistics": statistics,
        "categorical_summary": categorical_summary
    }
    
    return result


def main():
    mcp.run()

if __name__ == "__main__":
    main()