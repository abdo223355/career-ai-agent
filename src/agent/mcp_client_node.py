"""
External Researcher Node via MCP
=================================
This node acts as an MCP Client. It connects to an external MCP Server
via stdio (the web_fetcher_mcp.py we created), loads its tools dynamically,
binds them to the LLM, and lets the LLM fetch live web content!
"""

import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import SystemMessage, HumanMessage

from src.models.llm import llm
from src.agent.language import get_language_prompt_instruction

async def _run_external_research(query: str, language_pref: str) -> str:
    """
    Async core function that connects to the MCP server, gets tools, 
    and invokes the LLM with tool calling capabilities.
    """
    # Define the external MCP server parameters
    # We execute python on the web_fetcher_mcp.py script we wrote
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["external_services/web_fetcher_mcp.py"],
    )

    try:
        # Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # Fetch tools exposed by the MCP server (e.g. fetch_web_content)
                tools = await load_mcp_tools(session)
                
                # Bind the external tools to our LLM
                llm_with_tools = llm.bind_tools(tools)
                
                system_prompt = (
                    "You are an External Researcher Agent.\n"
                    "Your superpower is that you have access to live external tools.\n"
                    "Use your tools (like fetch_web_content) to gather real data from URLs provided by the user, "
                    "then summarize or answer the user's question based on the fetched data.\n"
                    f"{get_language_prompt_instruction(language_pref)}"
                )
                
                # Start the tool-calling loop (basic ReAct loop)
                messages = [SystemMessage(content=system_prompt), HumanMessage(content=query)]
                
                # 1. LLM decides which tool to call
                response = llm_with_tools.invoke(messages)
                messages.append(response)
                
                # 2. If it called a tool, execute it
                if response.tool_calls:
                    for tool_call in response.tool_calls:
                        # Find the correct tool from our MCP tools list
                        tool = next((t for t in tools if t.name == tool_call["name"]), None)
                        if tool:
                            tool_result = await tool.ainvoke(tool_call["args"])
                            messages.append(tool_result)
                    
                    # 3. LLM formulates the final answer based on the tool result
                    final_response = llm_with_tools.invoke(messages)
                    return final_response.content
                else:
                    # No tool called
                    return response.content
    except Exception as e:
        return f"External research failed. Error connecting to MCP server: {str(e)}"

def mcp_client_node(state: dict) -> dict:
    """
    Synchronous wrapper for the external researcher node.
    """
    print(f"--- [EXTERNAL RESEARCHER MCP] Fetching data for query: {state['user_query']} ---")
    language_pref = state.get("language_preference", "en")
    
    # Run the async loop
    result = asyncio.run(_run_external_research(state["user_query"], language_pref))
    
    return {"final_response": result}
