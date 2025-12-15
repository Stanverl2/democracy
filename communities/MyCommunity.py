import os

from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.peer import Peer

from messages.message import MyMessage


class MyCommunity(Community):
    community_id = os.urandom(20)

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        # Register the message handler for messages (with the identifier "1").
        self.add_message_handler(MyMessage, self.on_message)
        # The Lamport clock this peer maintains.
        # This is for the example of global clock synchronization.
        self.lamport_clock = 0

    def started(self) -> None:
        async def start_communication() -> None:
            if not self.lamport_clock:
                # If we have not started counting, try boostrapping
                # communication with our other known peers.
                for p in self.get_peers():
                    self.ez_send(p, MyMessage(self.lamport_clock))
            else:
                self.cancel_pending_task("start_communication")

        # We register an asyncio task with this overlay.
        # This makes sure that the task ends when this overlay is unloaded.
        # We call the "start_communication" function every 5.0 seconds, starting now.
        self.register_task("start_communication", start_communication, interval=5.0, delay=0)

    @lazy_wrapper(MyMessage)
    def on_message(self, peer: Peer, payload: MyMessage) -> None:
        # Update our Lamport clock.
        self.lamport_clock = max(self.lamport_clock, payload.electionId) + 1
        print(self.my_peer, "current clock:", self.lamport_clock)
        # Then synchronize with the rest of the network again.
        self.ez_send(peer, MyMessage(self.lamport_clock))