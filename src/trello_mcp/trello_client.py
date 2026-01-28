"""Trello API client wrapper for making authenticated requests."""

import os
from typing import Any, Optional
import httpx


class TrelloClient:
    """Client for interacting with the Trello REST API."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self, api_key: Optional[str] = None, api_token: Optional[str] = None):
        """Initialize the Trello client.

        Args:
            api_key: Trello API key (defaults to TRELLO_API_KEY env var)
            api_token: Trello API token (defaults to TRELLO_API_TOKEN env var)
        """
        self.api_key = api_key or os.getenv("TRELLO_API_KEY")
        self.api_token = api_token or os.getenv("TRELLO_API_TOKEN")

        if not self.api_key or not self.api_token:
            raise ValueError(
                "Trello API credentials not found. Please set TRELLO_API_KEY and "
                "TRELLO_API_TOKEN environment variables."
            )

        self.client = httpx.Client(timeout=30.0)

    def _add_auth(self, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Add authentication parameters to request.

        Args:
            params: Existing query parameters

        Returns:
            Parameters with auth credentials added
        """
        auth_params = {"key": self.api_key, "token": self.api_token}
        if params:
            return {**params, **auth_params}
        return auth_params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an authenticated request to the Trello API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., "/boards/{id}")
            params: Query parameters
            json: JSON body for POST/PUT requests

        Returns:
            Response data as dict or list

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = self._add_auth(params)

        try:
            response = self.client.request(method, url, params=params, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid Trello API credentials") from e
            elif e.response.status_code == 404:
                raise Exception(f"Resource not found: {endpoint}") from e
            elif e.response.status_code == 429:
                raise Exception(
                    "Trello API rate limit exceeded. Consider using webhooks for "
                    "frequent updates."
                ) from e
            else:
                raise Exception(f"Trello API error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}") from e

    # Board methods

    def list_boards(self) -> list[dict[str, Any]]:
        """Get all boards for the authenticated user.

        Returns:
            List of board objects
        """
        return self._request("GET", "/members/me/boards")

    def get_board(self, board_id: str) -> dict[str, Any]:
        """Get details of a specific board.

        Args:
            board_id: The board ID

        Returns:
            Board object with details
        """
        return self._request("GET", f"/boards/{board_id}")

    def create_board(self, name: str, desc: Optional[str] = None) -> dict[str, Any]:
        """Create a new board.

        Args:
            name: Name of the board
            desc: Optional description

        Returns:
            Created board object
        """
        params = {"name": name}
        if desc:
            params["desc"] = desc
        return self._request("POST", "/boards/", params=params)

    # List methods

    def get_board_lists(self, board_id: str) -> list[dict[str, Any]]:
        """Get all lists on a board.

        Args:
            board_id: The board ID

        Returns:
            List of list objects
        """
        return self._request("GET", f"/boards/{board_id}/lists")

    def create_list(
        self, board_id: str, name: str, pos: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new list on a board.

        Args:
            board_id: The board ID
            name: Name of the list
            pos: Position of the list (top, bottom, or a positive number)

        Returns:
            Created list object
        """
        params = {"name": name}
        if pos:
            params["pos"] = pos
        return self._request("POST", f"/boards/{board_id}/lists", params=params)

    def archive_list(self, list_id: str) -> dict[str, Any]:
        """Archive (close) a list.

        Args:
            list_id: The list ID

        Returns:
            Updated list object
        """
        return self._request("PUT", f"/lists/{list_id}/closed", params={"value": "true"})

    # Card methods

    def list_cards(self, list_id: str) -> list[dict[str, Any]]:
        """Get all cards in a list.

        Args:
            list_id: The list ID

        Returns:
            List of card objects
        """
        return self._request("GET", f"/lists/{list_id}/cards")

    def get_card(self, card_id: str) -> dict[str, Any]:
        """Get details of a specific card.

        Args:
            card_id: The card ID

        Returns:
            Card object with details
        """
        return self._request("GET", f"/cards/{card_id}")

    def create_card(
        self,
        list_id: str,
        name: str,
        desc: Optional[str] = None,
        pos: Optional[str] = None,
        due: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new card in a list.

        Args:
            list_id: The list ID where the card will be created
            name: Name of the card
            desc: Optional description
            pos: Position of the card (top, bottom, or a positive number)
            due: Optional due date (ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ)

        Returns:
            Created card object
        """
        params = {"idList": list_id, "name": name}
        if desc:
            params["desc"] = desc
        if pos:
            params["pos"] = pos
        if due:
            params["due"] = due
        return self._request("POST", "/cards", params=params)

    def update_card(
        self,
        card_id: str,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        list_id: Optional[str] = None,
        due: Optional[str] = None,
        due_complete: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Update a card.

        Args:
            card_id: The card ID
            name: New name for the card
            desc: New description for the card
            list_id: New list ID to move the card to
            due: New due date (ISO 8601 format or null to clear)
            due_complete: Mark due date as complete (true/false)

        Returns:
            Updated card object
        """
        params = {}
        if name:
            params["name"] = name
        if desc:
            params["desc"] = desc
        if list_id:
            params["idList"] = list_id
        if due is not None:
            params["due"] = due
        if due_complete is not None:
            params["dueComplete"] = due_complete
        return self._request("PUT", f"/cards/{card_id}", params=params)

    def delete_card(self, card_id: str) -> dict[str, Any]:
        """Delete a card.

        Args:
            card_id: The card ID

        Returns:
            Response confirming deletion
        """
        return self._request("DELETE", f"/cards/{card_id}")

    def move_card(
        self, card_id: str, list_id: str, pos: Optional[str] = None
    ) -> dict[str, Any]:
        """Move a card to a different list.

        Args:
            card_id: The card ID
            list_id: The destination list ID
            pos: Position in the new list (top, bottom, or a positive number)

        Returns:
            Updated card object
        """
        params = {"idList": list_id}
        if pos:
            params["pos"] = pos
        return self._request("PUT", f"/cards/{card_id}", params=params)

    # Due date methods

    def set_card_due_date(self, card_id: str, due_date: str) -> dict[str, Any]:
        """Set or update a card's due date.

        Args:
            card_id: The card ID
            due_date: Due date in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.sssZ)

        Returns:
            Updated card object
        """
        params = {"due": due_date}
        return self._request("PUT", f"/cards/{card_id}", params=params)

    def mark_due_date_complete(
        self, card_id: str, complete: bool = True
    ) -> dict[str, Any]:
        """Mark a card's due date as complete or incomplete.

        Args:
            card_id: The card ID
            complete: True to mark complete, False for incomplete

        Returns:
            Updated card object
        """
        params = {"dueComplete": complete}
        return self._request("PUT", f"/cards/{card_id}", params=params)

    def clear_card_due_date(self, card_id: str) -> dict[str, Any]:
        """Remove the due date from a card.

        Args:
            card_id: The card ID

        Returns:
            Updated card object
        """
        params = {"due": None}
        return self._request("PUT", f"/cards/{card_id}", params=params)

    # Checklist methods

    def get_card_checklists(self, card_id: str) -> list[dict[str, Any]]:
        """Get all checklists on a card.

        Args:
            card_id: The card ID

        Returns:
            List of checklist objects
        """
        return self._request("GET", f"/cards/{card_id}/checklists")

    def create_checklist(
        self, card_id: str, name: str, pos: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new checklist on a card.

        Args:
            card_id: The card ID to add the checklist to
            name: Name of the checklist
            pos: Position of the checklist (top, bottom, or a positive number)

        Returns:
            Created checklist object
        """
        params = {"idCard": card_id}
        if name:
            params["name"] = name
        if pos:
            params["pos"] = pos
        return self._request("POST", "/checklists", params=params)

    def get_checklist(self, checklist_id: str) -> dict[str, Any]:
        """Get checklist details.

        Args:
            checklist_id: The checklist ID

        Returns:
            Checklist object with details
        """
        return self._request("GET", f"/checklists/{checklist_id}")

    def update_checklist(
        self,
        checklist_id: str,
        name: Optional[str] = None,
        pos: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a checklist.

        Args:
            checklist_id: The checklist ID
            name: New name for the checklist
            pos: New position for the checklist

        Returns:
            Updated checklist object
        """
        params = {}
        if name:
            params["name"] = name
        if pos:
            params["pos"] = pos
        return self._request("PUT", f"/checklists/{checklist_id}", params=params)

    def delete_checklist(self, checklist_id: str) -> dict[str, Any]:
        """Delete a checklist.

        Args:
            checklist_id: The checklist ID

        Returns:
            Response confirming deletion
        """
        return self._request("DELETE", f"/checklists/{checklist_id}")

    # Checklist item methods

    def get_checklist_items(self, checklist_id: str) -> list[dict[str, Any]]:
        """Get all items in a checklist.

        Args:
            checklist_id: The checklist ID

        Returns:
            List of checklist item objects
        """
        return self._request("GET", f"/checklists/{checklist_id}/checkItems")

    def add_checklist_item(
        self,
        checklist_id: str,
        name: str,
        checked: Optional[bool] = None,
        pos: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add an item to a checklist.

        Args:
            checklist_id: The checklist ID
            name: Name/text of the checklist item
            checked: Whether the item is checked (default: False)
            pos: Position of the item (top, bottom, or a positive number)

        Returns:
            Created checklist item object
        """
        params = {"name": name}
        if checked is not None:
            params["checked"] = str(checked).lower()
        if pos:
            params["pos"] = pos
        return self._request("POST", f"/checklists/{checklist_id}/checkItems", params=params)

    def update_checklist_item(
        self,
        card_id: str,
        checklist_item_id: str,
        name: Optional[str] = None,
        state: Optional[str] = None,
        pos: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a checklist item.

        Args:
            card_id: The card ID containing the checklist
            checklist_item_id: The checklist item ID
            name: New name for the item
            state: New state ('complete' or 'incomplete')
            pos: New position for the item

        Returns:
            Updated checklist item object
        """
        params = {}
        if name:
            params["name"] = name
        if state:
            params["state"] = state
        if pos:
            params["pos"] = pos
        return self._request(
            "PUT", f"/cards/{card_id}/checkItem/{checklist_item_id}", params=params
        )

    def delete_checklist_item(
        self, checklist_id: str, checklist_item_id: str
    ) -> dict[str, Any]:
        """Delete an item from a checklist.

        Args:
            checklist_id: The checklist ID
            checklist_item_id: The checklist item ID

        Returns:
            Response confirming deletion
        """
        return self._request(
            "DELETE", f"/checklists/{checklist_id}/checkItems/{checklist_item_id}"
        )

    # Label methods

    def get_board_labels(self, board_id: str) -> list[dict[str, Any]]:
        """Get all labels on a board.

        Args:
            board_id: The board ID

        Returns:
            List of label objects
        """
        return self._request("GET", f"/boards/{board_id}/labels")

    def create_label(
        self,
        board_id: str,
        name: str,
        color: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new label on a board.

        Args:
            board_id: The board ID
            name: Label name
            color: Label color (green, yellow, orange, red, purple, blue,
                   sky, lime, pink, black, or null for no color)

        Returns:
            Created label object
        """
        params = {"idBoard": board_id, "name": name}
        if color is not None:
            params["color"] = color
        return self._request("POST", "/labels", params=params)

    def get_label(self, label_id: str) -> dict[str, Any]:
        """Get label details.

        Args:
            label_id: The label ID

        Returns:
            Label object
        """
        return self._request("GET", f"/labels/{label_id}")

    def update_label(
        self,
        label_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a label.

        Args:
            label_id: The label ID
            name: New label name
            color: New label color

        Returns:
            Updated label object
        """
        params = {}
        if name is not None:
            params["name"] = name
        if color is not None:
            params["color"] = color
        return self._request("PUT", f"/labels/{label_id}", params=params)

    def delete_label(self, label_id: str) -> dict[str, Any]:
        """Delete a label.

        Args:
            label_id: The label ID

        Returns:
            Response confirming deletion
        """
        return self._request("DELETE", f"/labels/{label_id}")

    def get_card_labels(self, card_id: str) -> list[dict[str, Any]]:
        """Get labels assigned to a card.

        Args:
            card_id: The card ID

        Returns:
            List of label objects
        """
        return self._request("GET", f"/cards/{card_id}/labels")

    def add_label_to_card(self, card_id: str, label_id: str) -> dict[str, Any]:
        """Add a label to a card.

        Args:
            card_id: The card ID
            label_id: The label ID to add

        Returns:
            Updated card object or label list
        """
        params = {"value": label_id}
        return self._request("POST", f"/cards/{card_id}/idLabels", params=params)

    def remove_label_from_card(self, card_id: str, label_id: str) -> dict[str, Any]:
        """Remove a label from a card.

        Args:
            card_id: The card ID
            label_id: The label ID to remove

        Returns:
            Response confirming removal
        """
        return self._request("DELETE", f"/cards/{card_id}/idLabels/{label_id}")

    def set_card_labels(self, card_id: str, label_ids: list[str]) -> dict[str, Any]:
        """Set all labels on a card (replaces existing labels).

        Args:
            card_id: The card ID
            label_ids: List of label IDs to set

        Returns:
            Updated card object
        """
        params = {"idLabels": ",".join(label_ids)}
        return self._request("PUT", f"/cards/{card_id}", params=params)

    # Attachment methods

    def get_card_attachments(self, card_id: str) -> list[dict[str, Any]]:
        """Get all attachments on a card.

        Args:
            card_id: The card ID

        Returns:
            List of attachment objects
        """
        return self._request("GET", f"/cards/{card_id}/attachments")

    def get_attachment(self, card_id: str, attachment_id: str) -> dict[str, Any]:
        """Get details of a specific attachment.

        Args:
            card_id: The card ID
            attachment_id: The attachment ID

        Returns:
            Attachment object with details
        """
        return self._request("GET", f"/cards/{card_id}/attachments/{attachment_id}")

    def add_attachment_url(
        self,
        card_id: str,
        url: str,
        name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add a URL attachment to a card.

        Args:
            card_id: The card ID
            url: URL to attach
            name: Optional name for the attachment

        Returns:
            Created attachment object
        """
        params = {"url": url}
        if name:
            params["name"] = name
        return self._request("POST", f"/cards/{card_id}/attachments", params=params)

    def add_attachment_file(
        self,
        card_id: str,
        file_path: str,
        name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Upload a file attachment to a card.

        Args:
            card_id: The card ID
            file_path: Local path to the file to upload
            name: Optional name for the attachment (defaults to filename)

        Returns:
            Created attachment object

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: On API errors
        """
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        url = f"{self.BASE_URL}/cards/{card_id}/attachments"
        params = self._add_auth()

        # Use the provided name or default to the filename
        attachment_name = name or os.path.basename(file_path)

        try:
            with open(file_path, "rb") as f:
                files = {"file": (attachment_name, f)}
                response = self.client.post(url, params=params, files=files)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid Trello API credentials") from e
            elif e.response.status_code == 404:
                raise Exception(f"Card not found: {card_id}") from e
            elif e.response.status_code == 429:
                raise Exception("Trello API rate limit exceeded") from e
            else:
                raise Exception(f"Trello API error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}") from e

    def download_attachment(
        self,
        card_id: str,
        attachment_id: str,
        output_path: str,
    ) -> dict[str, Any]:
        """Download an attachment to a local file.

        Args:
            card_id: The card ID
            attachment_id: The attachment ID
            output_path: Local path to save the file

        Returns:
            Dict with download details (path, size, name)

        Raises:
            Exception: On API or file errors
        """
        # Get attachment details to find the filename
        attachment = self.get_attachment(card_id, attachment_id)
        filename = attachment.get("fileName") or attachment.get("name") or "download"

        # Use the Trello API download endpoint with authentication
        # Format: /cards/{cardId}/attachments/{attachmentId}/download/{filename}
        download_url = f"{self.BASE_URL}/cards/{card_id}/attachments/{attachment_id}/download/{filename}"
        params = self._add_auth()

        try:
            response = self.client.get(download_url, params=params)
            response.raise_for_status()

            # Write to output path
            with open(output_path, "wb") as f:
                f.write(response.content)

            return {
                "success": True,
                "path": output_path,
                "size": len(response.content),
                "name": filename,
                "attachment_id": attachment_id,
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid Trello API credentials") from e
            elif e.response.status_code == 404:
                raise Exception(f"Attachment not found: {attachment_id}") from e
            elif e.response.status_code == 429:
                raise Exception("Trello API rate limit exceeded") from e
            else:
                raise Exception(f"Failed to download attachment: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise Exception(f"Network error during download: {str(e)}") from e
        except IOError as e:
            raise Exception(f"Failed to write file: {str(e)}") from e

    def delete_attachment(self, card_id: str, attachment_id: str) -> dict[str, Any]:
        """Delete an attachment from a card.

        Args:
            card_id: The card ID
            attachment_id: The attachment ID to delete

        Returns:
            Response confirming deletion
        """
        return self._request("DELETE", f"/cards/{card_id}/attachments/{attachment_id}")

    def close(self):
        """Close the HTTP client."""
        self.client.close()
