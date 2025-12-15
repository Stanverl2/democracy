from asyncio import run

from communities.MyCommunity import MyCommunity

from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8
from ipv8.util import run_forever

import os

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


run(start_communities(3))
