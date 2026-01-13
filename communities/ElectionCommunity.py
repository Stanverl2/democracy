import json

from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.peer import Peer

from config import COMMUNITY_ID
from messages.election_message import ElectionMessage
from models.election import Election
from models.vote import Vote
from storage.json_store import JSONStore


class ElectionCommunity(Community):
    """
    Community to manage and propagate elections and votes among peers.
    1. On start, broadcasts all known elections to connected peers.
    2. On receiving an election, adds it to the store if unknown and propagates it further.
    3. Provides a method to broadcast newly created elections to peers.

    Args:
        settings (CommunitySettings): Configuration for the community, including stores and callbacks.
    """
    community_id = COMMUNITY_ID

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)

        self.election_store: JSONStore[Election] = settings.election_store
        self.vote_store: JSONStore[Vote] = settings.vote_store
        self.election_added = settings.election_added

        # Register the message handlers for messages.
        self.add_message_handler(ElectionMessage, self.on_message)

    def on_start(self) -> None:
        """
        Called when the community starts. Sets up periodic broadcasting of known elections to peers.

        :return: None
        """
        async def start_communication() -> None:
            """
            Periodically broadcasts all known elections to connected peers.

            :return: None
            """
            elections = self.election_store.get_all()

            if not elections:
                return

            print(f"{self.my_peer}: Broadcasting {len(elections)} elections to peers.")

            for election in elections:
                payload = ElectionMessage(election_json=json.dumps(election.to_dict()))
                for peer in self.get_peers():
                    self.ez_send(peer, payload)

        # We register an asyncio task with this overlay.
        # This makes sure that the task ends when this overlay is unloaded.
        # We call the "start_communication" function every minute, starting now.
        self.register_task("start_communication", start_communication, interval=60.0, delay=0)

    @lazy_wrapper(ElectionMessage)
    def on_message(self, peer: Peer, payload: ElectionMessage) -> None:
        """
        Handles incoming election messages from peers. Adds unknown elections to the store and propagates them.

        :param peer: Peer that sent the message.
        :param payload: Received election message.
        :return: None
        """
        election = Election.from_dict(json.loads(payload.election_json))

        print(f"{self.my_peer}: Received election {election.id} from peer {peer}.")

        # Update store of known elections.
        if self.election_store.get(election.id):
            print(f"{self.my_peer}: Already knew about election {election.id}. Nothing updated.")
            return

        self.election_store.add(election)
        self.election_added()

        # Then synchronize with the rest of the network again.
        for p in self.get_peers():
            if p == peer:
                continue
            self.ez_send(p, payload)

    def on_create_election(self, election: Election) -> None:
        """
        Broadcasts a newly created election to all connected peers.

        :param election: Election to broadcast.
        :return: None
        """
        payload = ElectionMessage(election_json=json.dumps(election.to_dict()))

        for peer in self.get_peers():
            print(f"{self.my_peer}: Sending election {election.id} to peer {peer}.")
            self.ez_send(peer, payload)