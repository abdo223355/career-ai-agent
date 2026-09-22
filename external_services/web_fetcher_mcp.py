"""
External Web Fetcher MCP Server
================================
This is a standalone FastMCP server designed to simulate an external service.
It provides a tool to fetch raw text content from public URLs.
Our Career AI Agent will connect to this server as an MCP Client.
"""

import urllib.request
import urllib.error
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("WebFetcher")

@mcp.tool()
def fetch_web_content(url: str) -> str:
    """
    Fetches the raw text content of a public URL.
    Useful for reading external job postings, articles, or company pages.

    Args:
        url: The full HTTP/HTTPS URL to fetch.

    Returns:
        The text content of the page (first 5000 characters to prevent overflow).
    """
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Very basic HTML tag stripping for clean text
            import re
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text[:5000] + ("..." if len(text) > 5000 else "")
            
    except urllib.error.URLError as e:
        return f"Error fetching {url}: {str(e)}"
    except Exception as e:
        return f"Unexpected error reading {url}: {str(e)}"

if __name__ == "__main__":
    # Runs the server using stdio transport (standard for MCP clients)
    mcp.run(transport="stdio")
