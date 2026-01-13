from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import DataClassPayload

@dataclass
class ElectionMessage(DataClassPayload[1]):
    """
    Message to propagate election data in JSON format.

    Attributes:
        election_json (str): The election data serialized as a JSON string.
    """
    election_json: str

# Force schema generation once on import
_ = ElectionMessage(election_json="")