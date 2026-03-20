import requests


class PowensClient:
    """
    Powens API client adapter.
    
    This adapter encapsulates HTTP calls to the Powens API.
    It receives the access_token directly (not fetched from a repository)
    to maintain Clean Architecture—adapters should not depend on other adapters.
    """

    def __init__(self, access_token: str, domain: str):
        """
        Initialize Powens client with access token and domain.

        Args:
            access_token (str): User's Powens API access token.
            domain (str): Powens domain (e.g., 'powens.com').
        """
        self.base_url = f"https://{domain}/2.0"
        self.access_token = access_token

    def get_banks(self, id_connection: int) -> dict:
        """Fetch bank connection details."""
        response = requests.get(
            f"{self.base_url}/users/me/connections/{id_connection}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        connector_id = response.json().get("connector_uuid")
        response = requests.get(
            f"{self.base_url}/connectors/{connector_id}",
        )
        return response.json()

    def get_accounts(self) -> dict:
        """Fetch all user accounts."""
        response = requests.get(
            f"{self.base_url}/users/me/accounts",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        return response.json()

    def get_account(self, account_id: str) -> dict:
        """Fetch a specific account by ID."""
        response = requests.get(
            f"{self.base_url}/users/me/accounts/{account_id}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        return response.json()

    def get_transactions(
        self, account_id: str, limit: int = 1000, offset: int = 0
    ) -> dict:
        """Fetch transactions for a specific account."""
        response = requests.get(
            f"{self.base_url}/users/me/accounts/{account_id}/transactions",
            params={"limit": limit, "offset": offset},
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        return response.json()
