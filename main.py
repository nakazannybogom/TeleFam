import shlex
import random
import asyncio
from config import *
from rich.prompt import Prompt
from functions import Functions
from accounts_manager import AccountsManage

class Main:
    """
    Main class to process user commands and interact with Telegram clients.

    Author: AXL033
    Contacts:
        - Telegram: @nakazanny_bogom
        - GitHub: https://github.com/nakazannybogom
    """
    def __init__(self):
        """Initializes the necessary function and account management instances."""
        self.functions = Functions()
        self.account_manager = AccountsManage()
        self.console = self.functions.console

    async def process_command(self, command):
        """
        Processes the user command and performs the corresponding action.

        :param command: The user input command as a string.
        """
        command_parts = shlex.split(command)
        cmd = command_parts[0]

        match cmd:
            case '/info':
                # Show account info for all authorized clients
                await asyncio.gather(*(self.functions.show_info(client) for client in self.account_manager.authorized_clients))
            case '/exit':
                # Exit the script
                self.console.print("[red]Script is terminating![/red]")
                exit(0)
            case '/join':
                if len(command_parts) >= 2:
                    # Join a chat for all authorized clients
                    await asyncio.gather(*(self.functions.join_chat(command_parts[1], client) for client in self.account_manager.authorized_clients))
                else:
                    self.console.print("[bold red]Incorrect command usage![/bold red]")
            case '/leave':
                if len(command_parts) >= 2:
                    # Leave a chat for all authorized clients
                    await asyncio.gather(*(self.functions.leave_chat(command_parts[1], client) for client in self.account_manager.authorized_clients))
                else:
                    self.console.print("[bold red]Incorrect command usage![/bold red]")
            case '/send':
                if len(command_parts) >= 5:
                    # Send messages to the target
                    target = command_parts[1]
                    message_type_or_custom = command_parts[2]
                    timedelay = float(command_parts[3])
                    message_count = int(command_parts[4])

                    # If the message type is predefined, retrieve it; otherwise, treat it as custom input
                    message_list = globals().get(message_type_or_custom, [message_type_or_custom])
                    await asyncio.gather(
                        *(self.functions.send_messages(target, random.choice(message_list), timedelay, message_count, client)
                          for client in self.account_manager.authorized_clients)
                    )
                else:
                    self.console.print("[bold red]Incorrect command format. Use: /send <target> <message> <timedelay> <message_count>[/bold red]")
            case '/clear':
                # Clear the console
                self.functions.clear_console()
            case '/random_names':
                if len(command_parts) >= 3:
                    # Change the first names of the accounts
                    gender = command_parts[1]
                    language = command_parts[2]
                    await asyncio.gather(*(self.functions.change_name('first', gender, language, client) for client in self.account_manager.authorized_clients))
                else:
                    self.console.print("[bold red]Incorrect command format. Use: /random_names <male/female> <en/ru>[/bold red]")
            case '/random_last_names':
                if len(command_parts) >= 3:
                    # Change the last names of the accounts
                    gender = command_parts[1]
                    language = command_parts[2]
                    await asyncio.gather(*(self.functions.change_name('last', gender, language, client) for client in self.account_manager.authorized_clients))
                else:
                    self.console.print("[bold red]Incorrect command format. Use: /random_last_names <male/female> <en/ru>[/bold red]")

    async def main(self, accounts):
        """
        Main function to start processing user commands.

        :param accounts: A list of account dictionaries to manage.
        """
        self.functions.clear_console()
        await self.account_manager.process_accounts(accounts)

        # Command loop to keep the bot running and processing commands
        while True:
            command = Prompt.ask("[?] Command")
            await self.process_command(command)

if __name__ == "__main__":
    main_obj = Main()
    asyncio.run(main_obj.main(accounts))
