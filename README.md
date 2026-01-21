# Trello MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with Trello's API. Manage your Trello boards, lists, and cards directly through Claude or any MCP-compatible client.

## Features

- **Board Management**: List, view, and create Trello boards
- **List Operations**: Create, view, and archive lists on boards
- **Card CRUD**: Full create, read, update, delete operations for cards
- **Card Movement**: Move cards between lists with position control
- **MCP Resources**: Load board, list, and card data into LLM context for analysis
- **Secure Authentication**: API key and token-based authentication via environment variables

## Installation

### Prerequisites

- Python 3.11 or higher
- A Trello account
- Trello API credentials (API key and token)

### Install the Package

```bash
# Clone or download this repository
cd TrelloMCP

# Install using pip
pip install -e .

# Or using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Getting Trello API Credentials

### Step 1: Get Your API Key

1. Visit [Trello Power-Ups Admin](https://trello.com/power-ups/admin)
2. Click "New" to create a new Power-Up (if you don't have one)
3. Fill in the required information (name, workspace, etc.)
4. Once created, you'll see your **API Key** on the Power-Up's page

Alternatively, you can get your API key directly from: https://trello.com/app-key

### Step 2: Generate an API Token

1. While viewing your API key page, click the "Token" link or visit:
   ```
   https://trello.com/1/authorize?expiration=never&name=TrelloMCP&scope=read,write&response_type=token&key=YOUR_API_KEY
   ```
   (Replace `YOUR_API_KEY` with the key from Step 1)

2. Click "Allow" to authorize the application
3. Copy the **API Token** that is displayed

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
TRELLO_API_KEY=your_api_key_here
TRELLO_API_TOKEN=your_api_token_here
```

**Important**: Never commit your `.env` file to version control. It's already in `.gitignore`.

## Usage

### Running the Server Standalone

```bash
trello-mcp
```

The server will start and listen for MCP connections via stdio.

### Using with Claude Desktop

Add the following to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "trello": {
      "command": "trello-mcp",
      "env": {
        "TRELLO_API_KEY": "your_api_key_here",
        "TRELLO_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

Alternatively, if you have a `.env` file in your project directory:

```json
{
  "mcpServers": {
    "trello": {
      "command": "python",
      "args": ["-m", "trello_mcp"],
      "cwd": "/path/to/TrelloMCP",
      "env": {}
    }
  }
}
```

The server will automatically load credentials from the `.env` file in the working directory.

### Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the Trello MCP server.

## Available Tools

The server provides the following tools that you can use through natural language with Claude:

### Board Tools

- `list_boards()` - List all your Trello boards
- `get_board(board_id)` - Get details of a specific board
- `create_board(name, desc?)` - Create a new board

### List Tools

- `get_board_lists(board_id)` - Get all lists on a board
- `create_list(board_id, name, pos?)` - Create a new list on a board
- `archive_list(list_id)` - Archive (close) a list

### Card Tools

- `list_cards(list_id)` - Get all cards in a list
- `get_card(card_id)` - Get details of a specific card
- `create_card(list_id, name, desc?, pos?)` - Create a new card
- `update_card(card_id, name?, desc?, list_id?)` - Update a card
- `delete_card(card_id)` - Delete a card
- `move_card(card_id, list_id, pos?)` - Move a card to another list

## Available Resources

Resources allow you to load Trello data into the LLM's context for analysis:

- `trello://board/{board_id}` - Load complete board information with all lists and cards
- `trello://list/{list_id}` - Load list information with all cards
- `trello://card/{card_id}` - Load detailed card information

## Example Conversations with Claude

Once configured, you can interact with Trello naturally:

**"Show me all my Trello boards"**
- Claude will call `list_boards()` and display your boards

**"Create a new board called 'Q1 2026 Planning'"**
- Claude will call `create_board(name="Q1 2026 Planning")`

**"On my project board, create a new list called 'In Review'"**
- Claude will first find your board, then call `create_list()`

**"Add a card 'Review design docs' to the To Do list with description 'Need to review the new UI designs'"**
- Claude will call `create_card()` with the appropriate parameters

**"Move that card to the In Progress list"**
- Claude will call `move_card()` to relocate it

**"Load the full context of board abc123"**
- Claude will use the resource `trello://board/abc123` to load all data

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure

```
TrelloMCP/
├── src/
│   └── trello_mcp/
│       ├── __init__.py
│       ├── __main__.py       # Entry point
│       ├── server.py          # MCP server with tools and resources
│       └── trello_client.py   # Trello API client wrapper
├── tests/
│   ├── __init__.py
│   └── test_server.py
├── pyproject.toml
├── README.md
├── .env.example
└── .gitignore
```

### Adding New Features

1. Add new API methods to `TrelloClient` in `trello_client.py`
2. Add corresponding tools/resources in `server.py` using FastMCP decorators
3. Update this README with the new functionality

## API Rate Limits

Trello's API has rate limits per API key. If you exceed them, you'll receive a 429 error. For frequent updates, consider using Trello webhooks instead of polling.

## Troubleshooting

### "Invalid Trello API credentials" error

- Verify your `TRELLO_API_KEY` and `TRELLO_API_TOKEN` are correct
- Make sure there are no extra spaces or quotes in your `.env` file
- Try regenerating your API token

### "Resource not found" error

- Double-check the board/list/card ID you're using
- Ensure you have access to the resource with your Trello account

### Server not showing in Claude Desktop

- Check that the path to `trello-mcp` is correct
- Verify the JSON syntax in `claude_desktop_config.json`
- Restart Claude Desktop completely
- Check Claude Desktop's logs for error messages

## Security Notes

- Keep your API key and token secure - never commit them to version control
- The `.env` file is automatically ignored by git
- API tokens grant full access to your Trello account - treat them like passwords
- Consider creating a separate Trello workspace for testing

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this server for your own projects.

## References

- [Trello REST API Documentation](https://developer.atlassian.com/cloud/trello/rest/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://gofastmcp.com/)
- [Getting Started with Trello REST API](https://support.atlassian.com/trello/docs/getting-started-with-trello-rest-api/)

## Acknowledgments

Built with:
- [FastMCP](https://gofastmcp.com/) - High-level Python SDK for MCP
- [httpx](https://www.python-httpx.org/) - Modern HTTP client
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management
