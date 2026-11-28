import httpx

API_URL = "http://127.0.0.1:8000"


class BankAPI:
    def __init__(self, token: str | None = None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.client = httpx.Client(base_url=API_URL, headers=headers, timeout=10)

    def _check(self, response: httpx.Response):
        if response.status_code >= 400:
            raise ValueError(response.json().get("detail", "Something went wrong"))
        return response.json()

    def register(self, name, email, password):
        return self._check(self.client.post("/auth/register", json={"name": name, "email": email, "password": password}))

    def login(self, email, password):
        return self._check(self.client.post("/auth/login", data={"username": email, "password": password}))["access_token"]

    def me(self):
        return self._check(self.client.get("/auth/me"))

    def accounts(self):
        return self._check(self.client.get("/accounts"))

    def beneficiaries(self):
        return self._check(self.client.get("/accounts/beneficiaries"))

    def add_beneficiary(self, name, account_number):
        return self._check(self.client.post("/accounts/beneficiaries", json={"name": name, "account_number": account_number}))

    def deposit(self, account_number, amount):
        return self._check(self.client.post("/transactions/deposit", json={"account_number": account_number, "amount": amount}))

    def withdraw(self, account_number, amount):
        return self._check(self.client.post("/transactions/withdraw", json={"account_number": account_number, "amount": amount}))

    def transfer(self, from_account, to_account, amount, note=None, idempotency_key=None):
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        data = {"from_account": from_account, "to_account": to_account, "amount": amount, "note": note}
        return self._check(self.client.post("/transactions/transfer", json=data, headers=headers))

    def transactions(self, limit=20):
        return self._check(self.client.get("/transactions", params={"limit": limit}))
