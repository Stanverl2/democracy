import os

from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.peer import Peer

from messages.message import MyMessage

class ElectionCommunity(Community):
    community_id = os.urandom(20)

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)

        # Register the message handlers for messages.
        self.add_message_handler(MyMessage, self.on_message)

        self.elections = []

    def started(self) -> None:
        async def start_communication() -> None:
            if not self.elections:
                # If we have not started counting, try boostrapping
                # communication with our other known peers.
                for p in self.get_peers():
                    self.ez_send(p, MyMessage(666))
            else:
                self.cancel_pending_task("start_communication")

        # We register an asyncio task with this overlay.
        # This makes sure that the task ends when this overlay is unloaded.
        # We call the "start_communication" function every 5.0 seconds, starting now.
        self.register_task("start_communication", start_communication, interval=5.0, delay=0)

    @lazy_wrapper(MyMessage)
    def on_message(self, peer: Peer, payload: MyMessage) -> None:
        # Update our known elections.
        self.elections.append(payload.electionId)
        print(self.my_peer, "last election:", self.elections[-1])
        # Then synchronize with the rest of the network again.
        # self.ez_send(peer, MyMessage(self.elections[-1]))