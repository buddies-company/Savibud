import requests


class PowensClient:
    def __init__(self, client_id: str, client_secret: str, domain: str):
        self.base_url = f"https://{domain}/2.0"
        self.auth = (client_id, client_secret)

    def get_accounts(self, access_token: str):
        response = requests.get(
            f"{self.base_url}/users/me/accounts",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response.json()

    def get_transactions(self, access_token: str, account_id: int):
        response = requests.get(
            f"{self.base_url}/users/me/accounts/{account_id}/transactions",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response.json()
