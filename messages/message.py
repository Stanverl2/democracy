from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import DataClassPayload

@dataclass
class MyMessage(DataClassPayload[1]):
    electionId: int