"""Trello MCP Server - Tools and resources for managing Trello boards, lists, and cards."""

from typing import Optional
from fastmcp import FastMCP, Context
from .trello_client import TrelloClient

# Initialize FastMCP server
mcp = FastMCP("Trello MCP Server")

# Initialize Trello client (will be created when server starts)
trello_client: Optional[TrelloClient] = None


def get_client() -> TrelloClient:
    """Get or create the Trello client instance."""
    global trello_client
    if trello_client is None:
        trello_client = TrelloClient()
    return trello_client


# ========== Board Tools ==========


@mcp.tool()
def list_boards(context: Context) -> list[dict]:
    """List all Trello boards for the authenticated user.

    Returns:
        List of board objects with id, name, url, and other details
    """
    try:
        client = get_client()
        boards = client.list_boards()
        context.info(f"Retrieved {len(boards)} boards")
        return boards
    except Exception as e:
        context.error(f"Failed to list boards: {str(e)}")
        return [{"error": str(e)}]


@mcp.tool()
def get_board(board_id: str, context: Context) -> dict:
    """Get details of a specific Trello board.

    Args:
        board_id: The ID of the board to retrieve

    Returns:
        Board object with detailed information
    """
    try:
        client = get_client()
        board = client.get_board(board_id)
        context.info(f"Retrieved board: {board.get('name', board_id)}")
        return board
    except Exception as e:
        context.error(f"Failed to get board {board_id}: {str(e)}")
        return {"error": str(e), "board_id": board_id}


@mcp.tool()
def create_board(name: str, desc: Optional[str] = None, context: Context = None) -> dict:
    """Create a new Trello board.

    Args:
        name: Name of the new board
        desc: Optional description for the board

    Returns:
        Created board object
    """
    try:
        client = get_client()
        board = client.create_board(name, desc)
        context.info(f"Created board: {name}")
        return board
    except Exception as e:
        context.error(f"Failed to create board '{name}': {str(e)}")
        return {"error": str(e), "name": name}


# ========== List Tools ==========


@mcp.tool()
def get_board_lists(board_id: str, context: Context) -> list[dict]:
    """Get all lists on a Trello board.

    Args:
        board_id: The ID of the board

    Returns:
        List of list objects from the board
    """
    try:
        client = get_client()
        lists = client.get_board_lists(board_id)
        context.info(f"Retrieved {len(lists)} lists from board {board_id}")
        return lists
    except Exception as e:
        context.error(f"Failed to get lists for board {board_id}: {str(e)}")
        return [{"error": str(e), "board_id": board_id}]


@mcp.tool()
def create_list(
    board_id: str, name: str, pos: Optional[str] = None, context: Context = None
) -> dict:
    """Create a new list on a Trello board.

    Args:
        board_id: The ID of the board where the list will be created
        name: Name of the new list
        pos: Position of the list (top, bottom, or a positive number)

    Returns:
        Created list object
    """
    try:
        client = get_client()
        list_obj = client.create_list(board_id, name, pos)
        context.info(f"Created list '{name}' on board {board_id}")
        return list_obj
    except Exception as e:
        context.error(f"Failed to create list '{name}' on board {board_id}: {str(e)}")
        return {"error": str(e), "board_id": board_id, "name": name}


@mcp.tool()
def archive_list(list_id: str, context: Context) -> dict:
    """Archive (close) a Trello list.

    Args:
        list_id: The ID of the list to archive

    Returns:
        Updated list object
    """
    try:
        client = get_client()
        list_obj = client.archive_list(list_id)
        context.info(f"Archived list {list_id}")
        return list_obj
    except Exception as e:
        context.error(f"Failed to archive list {list_id}: {str(e)}")
        return {"error": str(e), "list_id": list_id}


# ========== Card Tools ==========


@mcp.tool()
def list_cards(list_id: str, context: Context) -> list[dict]:
    """Get all cards in a Trello list.

    Args:
        list_id: The ID of the list

    Returns:
        List of card objects
    """
    try:
        client = get_client()
        cards = client.list_cards(list_id)
        context.info(f"Retrieved {len(cards)} cards from list {list_id}")
        return cards
    except Exception as e:
        context.error(f"Failed to get cards for list {list_id}: {str(e)}")
        return [{"error": str(e), "list_id": list_id}]


@mcp.tool()
def get_card(card_id: str, context: Context) -> dict:
    """Get details of a specific Trello card.

    Args:
        card_id: The ID of the card to retrieve

    Returns:
        Card object with detailed information
    """
    try:
        client = get_client()
        card = client.get_card(card_id)
        context.info(f"Retrieved card: {card.get('name', card_id)}")
        return card
    except Exception as e:
        context.error(f"Failed to get card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id}


@mcp.tool()
def create_card(
    list_id: str,
    name: str,
    desc: Optional[str] = None,
    pos: Optional[str] = None,
    due: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Create a new card in a Trello list.

    Args:
        list_id: The ID of the list where the card will be created
        name: Name of the new card
        desc: Optional description for the card
        pos: Position of the card (top, bottom, or a positive number)
        due: Optional due date (ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ)

    Returns:
        Created card object
    """
    try:
        client = get_client()
        card = client.create_card(list_id, name, desc, pos, due)
        context.info(f"Created card '{name}' in list {list_id}")
        return card
    except Exception as e:
        context.error(f"Failed to create card '{name}' in list {list_id}: {str(e)}")
        return {"error": str(e), "list_id": list_id, "name": name}


@mcp.tool()
def update_card(
    card_id: str,
    name: Optional[str] = None,
    desc: Optional[str] = None,
    list_id: Optional[str] = None,
    due: Optional[str] = None,
    due_complete: Optional[bool] = None,
    context: Context = None,
) -> dict:
    """Update a Trello card.

    Args:
        card_id: The ID of the card to update
        name: New name for the card
        desc: New description for the card
        list_id: New list ID to move the card to
        due: New due date (ISO 8601 format, or null to clear)
        due_complete: Mark due date as complete (true/false)

    Returns:
        Updated card object
    """
    try:
        client = get_client()
        card = client.update_card(card_id, name, desc, list_id, due, due_complete)
        context.info(f"Updated card {card_id}")
        return card
    except Exception as e:
        context.error(f"Failed to update card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id}


@mcp.tool()
def delete_card(card_id: str, context: Context) -> dict:
    """Delete a Trello card.

    Args:
        card_id: The ID of the card to delete

    Returns:
        Response confirming deletion
    """
    try:
        client = get_client()
        result = client.delete_card(card_id)
        context.info(f"Deleted card {card_id}")
        return {"success": True, "card_id": card_id, "result": result}
    except Exception as e:
        context.error(f"Failed to delete card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id}


@mcp.tool()
def move_card(
    card_id: str, list_id: str, pos: Optional[str] = None, context: Context = None
) -> dict:
    """Move a Trello card to a different list.

    Args:
        card_id: The ID of the card to move
        list_id: The ID of the destination list
        pos: Position in the new list (top, bottom, or a positive number)

    Returns:
        Updated card object
    """
    try:
        client = get_client()
        card = client.move_card(card_id, list_id, pos)
        context.info(f"Moved card {card_id} to list {list_id}")
        return card
    except Exception as e:
        context.error(f"Failed to move card {card_id} to list {list_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "list_id": list_id}


# ========== Checklist Tools ==========


@mcp.tool()
def get_card_checklists(card_id: str, context: Context) -> list[dict]:
    """Get all checklists on a Trello card.

    Args:
        card_id: The ID of the card

    Returns:
        List of checklist objects
    """
    try:
        client = get_client()
        checklists = client.get_card_checklists(card_id)
        context.info(f"Retrieved {len(checklists)} checklists from card {card_id}")
        return checklists
    except Exception as e:
        context.error(f"Failed to get checklists for card {card_id}: {str(e)}")
        return [{"error": str(e), "card_id": card_id}]


@mcp.tool()
def create_checklist(
    card_id: str, name: str, pos: Optional[str] = None, context: Context = None
) -> dict:
    """Create a new checklist on a Trello card.

    Args:
        card_id: The ID of the card to add the checklist to
        name: Name of the checklist
        pos: Position of the checklist (top, bottom, or a positive number)

    Returns:
        Created checklist object
    """
    try:
        client = get_client()
        checklist = client.create_checklist(card_id, name, pos)
        context.info(f"Created checklist '{name}' on card {card_id}")
        return checklist
    except Exception as e:
        context.error(f"Failed to create checklist '{name}' on card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "name": name}


@mcp.tool()
def get_checklist(checklist_id: str, context: Context) -> dict:
    """Get details of a specific Trello checklist.

    Args:
        checklist_id: The ID of the checklist

    Returns:
        Checklist object with items
    """
    try:
        client = get_client()
        checklist = client.get_checklist(checklist_id)
        context.info(f"Retrieved checklist: {checklist.get('name', checklist_id)}")
        return checklist
    except Exception as e:
        context.error(f"Failed to get checklist {checklist_id}: {str(e)}")
        return {"error": str(e), "checklist_id": checklist_id}


@mcp.tool()
def update_checklist(
    checklist_id: str,
    name: Optional[str] = None,
    pos: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Update a Trello checklist.

    Args:
        checklist_id: The ID of the checklist to update
        name: New name for the checklist
        pos: New position for the checklist

    Returns:
        Updated checklist object
    """
    try:
        client = get_client()
        checklist = client.update_checklist(checklist_id, name, pos)
        context.info(f"Updated checklist {checklist_id}")
        return checklist
    except Exception as e:
        context.error(f"Failed to update checklist {checklist_id}: {str(e)}")
        return {"error": str(e), "checklist_id": checklist_id}


@mcp.tool()
def delete_checklist(checklist_id: str, context: Context) -> dict:
    """Delete a Trello checklist.

    Args:
        checklist_id: The ID of the checklist to delete

    Returns:
        Response confirming deletion
    """
    try:
        client = get_client()
        result = client.delete_checklist(checklist_id)
        context.info(f"Deleted checklist {checklist_id}")
        return result
    except Exception as e:
        context.error(f"Failed to delete checklist {checklist_id}: {str(e)}")
        return {"error": str(e), "checklist_id": checklist_id}


@mcp.tool()
def get_checklist_items(checklist_id: str, context: Context) -> list[dict]:
    """Get all items in a Trello checklist.

    Args:
        checklist_id: The ID of the checklist

    Returns:
        List of checklist item objects
    """
    try:
        client = get_client()
        items = client.get_checklist_items(checklist_id)
        context.info(f"Retrieved {len(items)} items from checklist {checklist_id}")
        return items
    except Exception as e:
        context.error(f"Failed to get items for checklist {checklist_id}: {str(e)}")
        return [{"error": str(e), "checklist_id": checklist_id}]


@mcp.tool()
def add_checklist_item(
    checklist_id: str,
    name: str,
    checked: Optional[bool] = None,
    pos: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Add an item to a Trello checklist.

    Args:
        checklist_id: The ID of the checklist
        name: Name/text of the checklist item
        checked: Whether the item is checked (default: False)
        pos: Position of the item (top, bottom, or a positive number)

    Returns:
        Created checklist item object
    """
    try:
        client = get_client()
        item = client.add_checklist_item(checklist_id, name, checked, pos)
        context.info(f"Added item '{name}' to checklist {checklist_id}")
        return item
    except Exception as e:
        context.error(f"Failed to add item to checklist {checklist_id}: {str(e)}")
        return {"error": str(e), "checklist_id": checklist_id, "name": name}


@mcp.tool()
def update_checklist_item(
    card_id: str,
    checklist_item_id: str,
    name: Optional[str] = None,
    state: Optional[str] = None,
    pos: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Update a checklist item.

    Args:
        card_id: The ID of the card containing the checklist
        checklist_item_id: The ID of the checklist item
        name: New name for the item
        state: New state ('complete' or 'incomplete')
        pos: New position for the item

    Returns:
        Updated checklist item object
    """
    try:
        client = get_client()
        item = client.update_checklist_item(card_id, checklist_item_id, name, state, pos)
        context.info(f"Updated checklist item {checklist_item_id}")
        return item
    except Exception as e:
        context.error(f"Failed to update checklist item {checklist_item_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "checklist_item_id": checklist_item_id}


@mcp.tool()
def delete_checklist_item(
    checklist_id: str, checklist_item_id: str, context: Context = None
) -> dict:
    """Delete an item from a Trello checklist.

    Args:
        checklist_id: The ID of the checklist
        checklist_item_id: The ID of the checklist item to delete

    Returns:
        Response confirming deletion
    """
    try:
        client = get_client()
        result = client.delete_checklist_item(checklist_id, checklist_item_id)
        context.info(f"Deleted checklist item {checklist_item_id}")
        return result
    except Exception as e:
        context.error(f"Failed to delete checklist item {checklist_item_id}: {str(e)}")
        return {
            "error": str(e),
            "checklist_id": checklist_id,
            "checklist_item_id": checklist_item_id,
        }


# ========== Label Tools ==========


@mcp.tool()
def get_board_labels(board_id: str, context: Context) -> list[dict]:
    """Get all labels on a Trello board.

    Args:
        board_id: The ID of the board

    Returns:
        List of label objects with id, name, color
    """
    try:
        client = get_client()
        labels = client.get_board_labels(board_id)
        context.info(f"Retrieved {len(labels)} labels from board {board_id}")
        return labels
    except Exception as e:
        context.error(f"Failed to get labels for board {board_id}: {str(e)}")
        return [{"error": str(e), "board_id": board_id}]


@mcp.tool()
def create_label(
    board_id: str,
    name: str,
    color: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Create a new label on a Trello board.

    Args:
        board_id: The ID of the board
        name: Name of the label
        color: Color of the label (green, yellow, orange, red, purple,
               blue, sky, lime, pink, black, or null for no color)

    Returns:
        Created label object
    """
    try:
        client = get_client()
        label = client.create_label(board_id, name, color)
        context.info(f"Created label '{name}' on board {board_id}")
        return label
    except Exception as e:
        context.error(f"Failed to create label '{name}' on board {board_id}: {str(e)}")
        return {"error": str(e), "board_id": board_id, "name": name}


@mcp.tool()
def update_label(
    label_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Update a Trello label.

    Args:
        label_id: The ID of the label to update
        name: New name for the label
        color: New color for the label

    Returns:
        Updated label object
    """
    try:
        client = get_client()
        label = client.update_label(label_id, name, color)
        context.info(f"Updated label {label_id}")
        return label
    except Exception as e:
        context.error(f"Failed to update label {label_id}: {str(e)}")
        return {"error": str(e), "label_id": label_id}


@mcp.tool()
def delete_label(label_id: str, context: Context) -> dict:
    """Delete a Trello label.

    Args:
        label_id: The ID of the label to delete

    Returns:
        Response confirming deletion
    """
    try:
        client = get_client()
        result = client.delete_label(label_id)
        context.info(f"Deleted label {label_id}")
        return result
    except Exception as e:
        context.error(f"Failed to delete label {label_id}: {str(e)}")
        return {"error": str(e), "label_id": label_id}


@mcp.tool()
def get_card_labels(card_id: str, context: Context) -> list[dict]:
    """Get all labels assigned to a Trello card.

    Args:
        card_id: The ID of the card

    Returns:
        List of label objects
    """
    try:
        client = get_client()
        labels = client.get_card_labels(card_id)
        context.info(f"Retrieved {len(labels)} labels from card {card_id}")
        return labels
    except Exception as e:
        context.error(f"Failed to get labels for card {card_id}: {str(e)}")
        return [{"error": str(e), "card_id": card_id}]


@mcp.tool()
def add_label_to_card(card_id: str, label_id: str, context: Context = None) -> dict:
    """Add a label to a Trello card.

    Args:
        card_id: The ID of the card
        label_id: The ID of the label to add

    Returns:
        Updated card or label list
    """
    try:
        client = get_client()
        result = client.add_label_to_card(card_id, label_id)
        context.info(f"Added label {label_id} to card {card_id}")
        return result
    except Exception as e:
        context.error(f"Failed to add label {label_id} to card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "label_id": label_id}


@mcp.tool()
def remove_label_from_card(
    card_id: str, label_id: str, context: Context = None
) -> dict:
    """Remove a label from a Trello card.

    Args:
        card_id: The ID of the card
        label_id: The ID of the label to remove

    Returns:
        Response confirming removal
    """
    try:
        client = get_client()
        result = client.remove_label_from_card(card_id, label_id)
        context.info(f"Removed label {label_id} from card {card_id}")
        return result
    except Exception as e:
        context.error(f"Failed to remove label {label_id} from card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "label_id": label_id}


@mcp.tool()
def set_card_labels(
    card_id: str, label_ids: list[str], context: Context = None
) -> dict:
    """Set all labels on a card, replacing any existing labels.

    Args:
        card_id: The ID of the card
        label_ids: List of label IDs to set on the card

    Returns:
        Updated card object
    """
    try:
        client = get_client()
        result = client.set_card_labels(card_id, label_ids)
        context.info(f"Set {len(label_ids)} labels on card {card_id}")
        return result
    except Exception as e:
        context.error(f"Failed to set labels on card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "label_ids": label_ids}


# ========== Due Date Tools ==========


@mcp.tool()
def set_card_due_date(card_id: str, due_date: str, context: Context = None) -> dict:
    """Set or update a card's due date.

    Args:
        card_id: The ID of the card
        due_date: Due date in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ)
                  Example: "2026-01-25T12:00:00.000Z"

    Returns:
        Updated card object
    """
    try:
        client = get_client()
        card = client.set_card_due_date(card_id, due_date)
        context.info(f"Set due date on card {card_id} to {due_date}")
        return card
    except Exception as e:
        context.error(f"Failed to set due date on card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "due_date": due_date}


@mcp.tool()
def mark_due_date_complete(
    card_id: str, complete: bool = True, context: Context = None
) -> dict:
    """Mark a card's due date as complete or incomplete.

    Args:
        card_id: The ID of the card
        complete: True to mark complete, False for incomplete (default: True)

    Returns:
        Updated card object
    """
    try:
        client = get_client()
        card = client.mark_due_date_complete(card_id, complete)
        status = "complete" if complete else "incomplete"
        context.info(f"Marked due date on card {card_id} as {status}")
        return card
    except Exception as e:
        context.error(f"Failed to mark due date on card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id}


@mcp.tool()
def clear_card_due_date(card_id: str, context: Context = None) -> dict:
    """Remove the due date from a card.

    Args:
        card_id: The ID of the card

    Returns:
        Updated card object
    """
    try:
        client = get_client()
        card = client.clear_card_due_date(card_id)
        context.info(f"Cleared due date on card {card_id}")
        return card
    except Exception as e:
        context.error(f"Failed to clear due date on card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id}


# ========== Attachment Tools ==========


@mcp.tool()
def get_card_attachments(card_id: str, context: Context) -> list[dict]:
    """Get all attachments on a Trello card.

    Args:
        card_id: The ID of the card

    Returns:
        List of attachment objects with id, name, url, and other details
    """
    try:
        client = get_client()
        attachments = client.get_card_attachments(card_id)
        context.info(f"Retrieved {len(attachments)} attachments from card {card_id}")
        return attachments
    except Exception as e:
        context.error(f"Failed to get attachments for card {card_id}: {str(e)}")
        return [{"error": str(e), "card_id": card_id}]


@mcp.tool()
def get_attachment(card_id: str, attachment_id: str, context: Context) -> dict:
    """Get details of a specific attachment.

    Args:
        card_id: The ID of the card
        attachment_id: The ID of the attachment

    Returns:
        Attachment object with detailed information
    """
    try:
        client = get_client()
        attachment = client.get_attachment(card_id, attachment_id)
        context.info(f"Retrieved attachment: {attachment.get('name', attachment_id)}")
        return attachment
    except Exception as e:
        context.error(f"Failed to get attachment {attachment_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "attachment_id": attachment_id}


@mcp.tool()
def add_attachment_url(
    card_id: str,
    url: str,
    name: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Add a URL attachment to a Trello card.

    Args:
        card_id: The ID of the card
        url: The URL to attach
        name: Optional name for the attachment

    Returns:
        Created attachment object
    """
    try:
        client = get_client()
        attachment = client.add_attachment_url(card_id, url, name)
        context.info(f"Added URL attachment to card {card_id}")
        return attachment
    except Exception as e:
        context.error(f"Failed to add URL attachment to card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "url": url}


@mcp.tool()
def add_attachment_file(
    card_id: str,
    file_path: str,
    name: Optional[str] = None,
    context: Context = None,
) -> dict:
    """Upload a local file as an attachment to a Trello card.

    Args:
        card_id: The ID of the card
        file_path: Local path to the file to upload
        name: Optional name for the attachment (defaults to filename)

    Returns:
        Created attachment object
    """
    try:
        client = get_client()
        attachment = client.add_attachment_file(card_id, file_path, name)
        context.info(f"Uploaded file attachment to card {card_id}")
        return attachment
    except FileNotFoundError as e:
        context.error(f"File not found: {file_path}")
        return {"error": str(e), "card_id": card_id, "file_path": file_path}
    except Exception as e:
        context.error(f"Failed to upload attachment to card {card_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "file_path": file_path}


@mcp.tool()
def download_attachment(
    card_id: str,
    attachment_id: str,
    output_path: str,
    context: Context = None,
) -> dict:
    """Download an attachment from a Trello card to a local file.

    Args:
        card_id: The ID of the card
        attachment_id: The ID of the attachment to download
        output_path: Local path where the file will be saved

    Returns:
        Dict with download details (success, path, size, name)
    """
    try:
        client = get_client()
        result = client.download_attachment(card_id, attachment_id, output_path)
        context.info(f"Downloaded attachment to {output_path}")
        return result
    except Exception as e:
        context.error(f"Failed to download attachment {attachment_id}: {str(e)}")
        return {
            "error": str(e),
            "card_id": card_id,
            "attachment_id": attachment_id,
            "output_path": output_path,
        }


@mcp.tool()
def delete_attachment(card_id: str, attachment_id: str, context: Context) -> dict:
    """Delete an attachment from a Trello card.

    Args:
        card_id: The ID of the card
        attachment_id: The ID of the attachment to delete

    Returns:
        Response confirming deletion
    """
    try:
        client = get_client()
        result = client.delete_attachment(card_id, attachment_id)
        context.info(f"Deleted attachment {attachment_id} from card {card_id}")
        return {"success": True, "card_id": card_id, "attachment_id": attachment_id, "result": result}
    except Exception as e:
        context.error(f"Failed to delete attachment {attachment_id}: {str(e)}")
        return {"error": str(e), "card_id": card_id, "attachment_id": attachment_id}


# ========== Resources ==========


@mcp.resource("trello://board/{board_id}")
def get_board_resource(board_id: str) -> str:
    """Load Trello board details with lists and cards into context.

    Args:
        board_id: The ID of the board to load

    Returns:
        Formatted board information for LLM context
    """
    try:
        client = get_client()

        # Get board details
        board = client.get_board(board_id)

        # Get lists on the board
        lists = client.get_board_lists(board_id)

        # Build formatted output
        output = [
            f"Board: {board.get('name', 'Unknown')}",
            f"URL: {board.get('url', 'N/A')}",
            f"Description: {board.get('desc', 'No description')}",
            f"\nLists ({len(lists)}):",
        ]

        for list_obj in lists:
            output.append(f"\n  - {list_obj.get('name', 'Unknown')} (ID: {list_obj.get('id')})")

            # Get cards in this list
            try:
                cards = client.list_cards(list_obj.get("id"))
                if cards:
                    output.append(f"    Cards ({len(cards)}):")
                    for card in cards:
                        card_name = card.get("name", "Unknown")
                        card_id = card.get("id", "N/A")
                        output.append(f"      • {card_name} (ID: {card_id})")
                        if card.get("desc"):
                            output.append(f"        Description: {card.get('desc')}")
                else:
                    output.append("    No cards")
            except Exception:
                output.append("    Error loading cards")

        return "\n".join(output)
    except Exception as e:
        return f"Error loading board {board_id}: {str(e)}"


@mcp.resource("trello://list/{list_id}")
def get_list_resource(list_id: str) -> str:
    """Load Trello list details with cards into context.

    Args:
        list_id: The ID of the list to load

    Returns:
        Formatted list information for LLM context
    """
    try:
        client = get_client()

        # Get cards in the list
        cards = client.list_cards(list_id)

        # Build formatted output
        output = [f"List ID: {list_id}", f"\nCards ({len(cards)}):"]

        if cards:
            for card in cards:
                card_name = card.get("name", "Unknown")
                card_id = card.get("id", "N/A")
                output.append(f"\n  • {card_name} (ID: {card_id})")
                if card.get("desc"):
                    output.append(f"    Description: {card.get('desc')}")
                if card.get("url"):
                    output.append(f"    URL: {card.get('url')}")
        else:
            output.append("  No cards in this list")

        return "\n".join(output)
    except Exception as e:
        return f"Error loading list {list_id}: {str(e)}"


@mcp.resource("trello://card/{card_id}")
def get_card_resource(card_id: str) -> str:
    """Load Trello card details into context.

    Args:
        card_id: The ID of the card to load

    Returns:
        Formatted card information for LLM context
    """
    try:
        client = get_client()
        card = client.get_card(card_id)

        # Build formatted output
        output = [
            f"Card: {card.get('name', 'Unknown')}",
            f"ID: {card.get('id', 'N/A')}",
            f"URL: {card.get('url', 'N/A')}",
            f"Description: {card.get('desc', 'No description')}",
            f"List ID: {card.get('idList', 'N/A')}",
            f"Board ID: {card.get('idBoard', 'N/A')}",
            f"Due Date: {card.get('due', 'None')}",
            f"Labels: {', '.join([label.get('name', 'Unnamed') for label in card.get('labels', [])])}",
        ]

        return "\n".join(output)
    except Exception as e:
        return f"Error loading card {card_id}: {str(e)}"
