"""
SciOS Coordinator

Coordinates collaboration among cognitive agents.
"""

from typing import Dict, List

from .message import Message


class Coordinator:
    """
    Multi-agent coordinator.

    Responsibilities
    ----------------
    - Register agents
    - Route messages
    - Coordinate task execution
    - Broadcast events
    """

    def __init__(self):
        self._agents: Dict[str, object] = {}

    def register(self, name: str, agent):
        """
        Register an agent.
        """
        self._agents[name] = agent

    def unregister(self, name: str):
        """
        Remove an agent.
        """
        self._agents.pop(name, None)

    def get(self, name: str):
        """
        Retrieve an agent.
        """
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """
        List registered agents.
        """
        return sorted(self._agents.keys())

    def send(
        self,
        sender: str,
        receiver: str,
        payload,
    ) -> Message:
        """
        Send a message between agents.
        """

        if receiver not in self._agents:
            raise ValueError(
                f"Unknown agent: {receiver}"
            )

        message = Message(
            sender=sender,
            receiver=receiver,
            payload=payload,
        )

        agent = self._agents[receiver]

        if hasattr(agent, "receive"):
            agent.receive(message)

        return message

    def broadcast(
        self,
        sender: str,
        payload,
    ):
        """
        Broadcast a message to all agents.
        """

        messages = []

        for receiver in self._agents:

            if receiver == sender:
                continue

            messages.append(
                self.send(
                    sender,
                    receiver,
                    payload,
                )
            )

        return messages

    def status(self):
        """
        Coordinator status.
        """

        return {
            "registered_agents": len(self._agents),
            "agents": self.list_agents(),
        }