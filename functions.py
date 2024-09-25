import re
import random
import asyncio
import datetime
import subprocess
from faker import Faker
from art import text2art
from telethon import errors
from rich.console import Console
from telethon.tl import functions
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest


class Functions:
    """
    A class containing various utility functions for interacting with Telegram using Telethon.

    Author: AXL033
    Contacts:
        - Telegram: @nakazanny_bogom
        - GitHub: https://github.com/nakazannybogom
    """
    def __init__(self):
        """Initializes the console for rich text output."""
        self.console = Console()

    def print_banner(self):
        """Prints the program banner using ASCII art."""
        self.console.print(f"[bold cyan]{text2art('TeleFam')}[/bold cyan]")

    def print_commands(self):
        """Prints the available commands for the user."""
        self.console.print("""
        [bold cyan]Available commands:[/bold cyan]
        /info - Account information
        /exit - Terminate script
        /clear - Clear console
        /join <chat_link> - Join a chat
        /leave <chat_link> - Leave a chat
        /send <target> <message> <delay> <count> - Send a message
        /random_names <male/female> <en/ru> - Change account first names to random names
        /random_last_names <male/female> <en/ru> - Change account last names to random names
        """)

    def clear_console(self):
        """Clears the console and re-displays the banner and commands."""
        subprocess.call("cls" if subprocess.os.name == "nt" else "clear", shell=True)
        self.print_banner()
        self.print_commands()

    async def join_chat(self, chat_link, client):
        """
        Joins a chat by link or invite hash.

        :param chat_link: The chat link or invite hash.
        :param client: The Telethon client used to join the chat.
        """
        try:
            # Extract invite hash if present in link
            invite_hash = chat_link.split('/')[-1].replace('+', '') if ('/joinchat/' in chat_link or '+' in chat_link) else None
            if invite_hash:
                await client(ImportChatInviteRequest(invite_hash))
            else:
                entity = await client.get_entity(chat_link)
                await client(JoinChannelRequest(entity))
            self.console.print(f"[bold yellow]Joined: {chat_link}[/bold yellow]")
        except errors.UserAlreadyParticipantError:
            self.console.print(f"[bold yellow]This account is already a member of {chat_link} chat[/bold yellow]")
        except errors.UserBannedInChannelError:
            self.console.print(f"[bold yellow]This account has been banned from {chat_link} chat[/bold yellow]")
        except Exception as e:
            self.console.print(f"[bold red]Failed to join {chat_link}: {e}[/bold red]")

    async def leave_chat(self, chat_link, client):
        """
        Leaves a chat by link.

        :param chat_link: The chat link.
        :param client: The Telethon client used to leave the chat.
        """
        try:
            entity = await client.get_entity(chat_link)
            await client(LeaveChannelRequest(entity))
            self.console.print(f"[bold yellow]Left: {chat_link}[/bold yellow]")
        except errors.UserNotParticipantError:
            self.console.print(f"[bold yellow]This account is not a participant of {chat_link} chat[/bold yellow]")
        except errors.ChannelPrivateError:
            self.console.print(f"[bold yellow]Cannot leave {chat_link}: This chat is private and access is restricted[/bold yellow]")
        except Exception as e:
            self.console.print(f"[bold red]Failed to leave {chat_link}: {e}[/bold red]")

    async def change_name(self, name_type, gender, language, client):
        """
        Changes the name (first or last) of an account to a random one based on gender and language.

        :param name_type: Type of name to change ('first' or 'last').
        :param gender: Gender for name selection ('male' or 'female').
        :param language: Language for name generation ('en' or 'ru').
        :param client: The Telethon client used to change the name.
        """
        locale = 'ru_RU' if language == 'ru' else 'en_US'
        fake = Faker(locale)

        # Get current profile info
        me = await client.get_me()
        current_first_name = me.first_name
        current_last_name = me.last_name

        # Select name based on gender and name type
        new_first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female() if name_type == 'first' else current_first_name
        new_last_name = fake.last_name_male() if gender == 'male' else fake.last_name_female() if name_type == 'last' else current_last_name

        try:
            # Update profile with new name
            await client(functions.account.UpdateProfileRequest(first_name=new_first_name, last_name=new_last_name))
            self.console.print(f"[bold green]Account {me.phone} updated: first name is now '{new_first_name}', last name is now '{new_last_name}'[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]Failed to change {name_type} name for {me.phone}: {e}[/bold red]")

    async def replace_placeholders(self, message, client):
        """
        Replaces placeholders like time, name, and random values in the message.

        :param message: The message with placeholders.
        :param client: The Telethon client used to fetch user data.
        :return: The message with placeholders replaced.
        """
        me = await client.get_me()
        replacements = {
            'phone': me.phone,
            'username': f'@{me.username}' if me.username else '',
            'surname': me.last_name or '',
            'name': me.first_name or '',
            'time': datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        }
        # Replace placeholders in the message
        message = re.sub(r'random\((-?\d+),\s*(-?\d+)\)', lambda m: str(random.randint(int(m.group(1)), int(m.group(2)))), message)
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)
        return message

    async def send_messages(self, target, message, timedelay, message_count, client):
        """
        Sends a specified number of messages to a target with a delay between each.

        :param target: The target username, user ID, or chat link.
        :param message: The message to send.
        :param timedelay: Delay between each message.
        :param message_count: Number of messages to send.
        :param client: The Telethon client used to send the messages.
        """
        try:
            user = await client.get_input_entity(target) if not target.isdigit() else await client.get_entity(int(target))
            message = await self.replace_placeholders(message, client)

            for _ in range(message_count):
                await client.send_message(user, message)
                await asyncio.sleep(timedelay)
            self.console.print(f"[bold green]Message sent to {target}[/bold green]")
        except (errors.ChatWriteForbiddenError, errors.rpcbaseerrors.ForbiddenError):
            self.console.print(f"[bold yellow]This account does not have permission to post to {target}[/bold yellow]")
        except errors.FloodWaitError as e:
            self.console.print(f"[bold yellow]Flood wait: Sleeping for {e.seconds} seconds before retrying[/bold yellow]")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            self.console.print(f"[bold red]Failed to send message to {target}. Error: {e}[/bold red]")

    async def show_info(self, client):
        """
        Shows account information.

        :param client: The Telethon client used to fetch user info.
        """
        try:
            me = await client.get_me()
            self.console.print(f"[bold yellow]Account: {me.phone} | Name: {me.first_name} | Username: @{me.username}[/bold yellow]")
        except Exception as e:
            self.console.print(f"[bold red]Failed to retrieve info: {e}[/bold red]")
