import os

from ipv8.configuration import ConfigBuilder, default_bootstrap_defs, Strategy, WalkerDefinition
from ipv8_service import IPv8
from ipv8.util import run_forever
from pathlib import Path

from communities.MyCommunity import MyCommunity
from config import DATA_PATH
from models.election import Election
from models.vote import Vote
from storage.json_store import JSONStore
from ui.app import Application

def main():
    election_store = JSONStore[Election](
        path=Path(DATA_PATH + "elections.json"),
        model_factory=Election.from_dict,
        dictify=lambda e: e.to_dict()
    )
    vote_store = JSONStore[Vote](
        path=Path(DATA_PATH + "votes.json"),
        model_factory=Vote.from_dict,
        dictify=lambda v: v.to_dict()
    )
    app = Application(election_store, vote_store)
    app.run()

async def start_communities(n: int) -> None:
    for i in range(0, n):
        builder = ConfigBuilder().clear_keys().clear_overlays()
        os.makedirs("keys", exist_ok=True)
        builder.add_key("my peer", "medium", f"keys/ec{i}.pem")
        builder.add_overlay("MyCommunity", "my peer",
                            [WalkerDefinition(Strategy.RandomWalk,
                                              10, {"timeout": 3.0})],
                            default_bootstrap_defs, {}, [("started",)])
        await IPv8(builder.finalize(),
                   extra_communities={"MyCommunity": MyCommunity}).start()
    await run_forever()

if __name__ == "__main__":
    main()
