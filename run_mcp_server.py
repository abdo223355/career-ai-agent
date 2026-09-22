"""
Career AI Agent — MCP Server Entry Point
=========================================
Runs the FastMCP server that exposes all career AI tools
via the Model Context Protocol (JSON-RPC over stdio or SSE).

Usage:
    # stdio mode (for Claude Desktop / VS Code MCP)
    python run_mcp_server.py

    # SSE mode (HTTP — for browser / remote clients)
    python run_mcp_server.py --sse --port 8502
"""

import os
import sys
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MCP] %(levelname)s %(message)s"
)

# ── Add project root to path ──────────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.mcp.tools import mcp  # Import the FastMCP app with all tools registered


def main():
    parser = argparse.ArgumentParser(description="Career AI Agent MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport layer (default: stdio for Claude Desktop integration)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE/HTTP mode")
    parser.add_argument("--port", type=int, default=8502, help="Port for SSE/HTTP mode")
    args = parser.parse_args()

    if args.transport == "stdio":
        logging.info("Starting Career AI Agent MCP Server (stdio mode)...")
        logging.info("Tools registered: %s", [
            "search_knowledge_base",
            "get_career_roadmap",
            "get_salary_info",
            "get_interview_questions",
            "match_jobs_to_skills",
            "recommend_projects",
        ])
        mcp.run(transport="stdio")

    elif args.transport in ("sse", "streamable-http"):
        logging.info(
            "Starting Career AI Agent MCP Server (%s) on http://%s:%d",
            args.transport, args.host, args.port
        )
        mcp.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
