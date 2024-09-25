import asyncio
from rich.console import Console
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest

class AccountsManage:
    """
    A class to manage multiple Telegram accounts for authorization and session handling.

    Author: AXL033
    Contacts:
        - Telegram: @nakazanny_bogom
        - GitHub: https://github.com/nakazannybogom
    """
    def __init__(self):
        """Initializes the console for output and sets up lists to track client statuses."""
        self.console = Console()
        self.authorized_clients = []
        self.unauthorized_clients = []

    async def check_session(self, account):
        """
        Checks if a Telegram session for a given account is authorized.

        :param account: A dictionary containing 'phone', 'api_id', and 'api_hash' of the account.
        """
        client = TelegramClient(account['phone'], account['api_id'], account['api_hash'])
        await client.connect()
        try:
            # Check if the account is authorized
            if await client.is_user_authorized():
                self.console.print(f"[bold green]Authorized: {account['phone']}[/bold green]")
                self.authorized_clients.append(client)
            else:
                self.console.print(f"[bold red]Unauthorized: {account['phone']}[/bold red]")
                self.unauthorized_clients.append(account)
        except Exception as e:
            self.console.print(f"[bold red]Error with {account['phone']}: {e}[/bold red]")
        finally:
            # Disconnect after checking
            await client.disconnect()

    async def start_client(self, account):
        """
        Starts and authorizes a Telegram client for an unauthorized account.

        :param account: A dictionary containing 'phone', 'api_id', and 'api_hash' of the account.
        :return: An instance of the authorized Telegram client.
        """
        client = TelegramClient(account['phone'], account['api_id'], account['api_hash'])
        self.console.print(f"[bold yellow]Authorizing {account['phone']}[/bold yellow]")
        try:
            # Start the client, triggering the authorization process
            await client.start(phone=account['phone'])
        except Exception as e:
            self.console.print(f"[bold red]Authorization failed: {e}[/bold red]")
        return client

    async def process_accounts(self, accounts):
        """
        Processes a list of accounts, checks their session status, and attempts authorization for unauthorized accounts.

        :param accounts: A list of account dictionaries, each containing 'phone', 'api_id', and 'api_hash'.
        """
        # Check session for all accounts
        await asyncio.gather(*(self.check_session(acc) for acc in accounts))

        # If authorized clients exist, connect them
        if self.authorized_clients:
            await asyncio.gather(*(client.connect() for client in self.authorized_clients))

        # Attempt to authorize unauthorized clients
        for account in self.unauthorized_clients:
            await self.start_client(account)
