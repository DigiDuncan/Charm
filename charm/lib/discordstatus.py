from typing import Optional
from pypresence import Presence, DiscordNotFound, DiscordError

import logging

logger = logging.getLogger("charm")

RPC_CLIENT_ID = "1056710104348639305"  # Charm app on Discord.

class DiscordStatus:
    def __init__(self, status: Optional[str] = None):
        self.old_status: Optional[str] = None
        self.new_status: Optional[str] = status
        self.last_update_time: float = 0
        self.rpc: Optional[Presence] = None

    def connect(self):
        if self.rpc is not None:
            return

        try:
            rpc = Presence(RPC_CLIENT_ID)
            rpc.connect()
        except (DiscordNotFound, DiscordError):
            logger.warn("Discord could not connect the rich presence.")
            return

        self.rpc = rpc

    def set(self, new_status: Optional[str]):
        self.new_status = new_status

    def update(self, now: float):
        if not self.rpc:
            return
        if self.new_status is None:
            return
        if self.new_status == self.old_status:
            return
        if now < self.last_update_time + 1:
            return

        self.rpc.update(
            state=self.new_status,
            large_image="charm-icon-square",
            large_text="Charm Logo"
        )
        self.last_update_time = now
        self.old_status = self.new_status
