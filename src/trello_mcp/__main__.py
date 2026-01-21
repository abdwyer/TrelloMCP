"""Entry point for Trello MCP Server."""

import os
import sys
from dotenv import load_dotenv
from .server import mcp


def main():
    """Main entry point for the Trello MCP server."""
    # Load environment variables from .env file
    load_dotenv()

    # Validate required environment variables
    api_key = os.getenv("TRELLO_API_KEY")
    api_token = os.getenv("TRELLO_API_TOKEN")

    if not api_key or not api_token:
        print(
            "Error: Trello API credentials not found.\n"
            "Please set TRELLO_API_KEY and TRELLO_API_TOKEN environment variables.\n"
            "You can create a .env file with these values or set them in your environment.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run the MCP server with stdio transport
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
