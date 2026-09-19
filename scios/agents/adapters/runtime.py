from scios.agents.base import Agent
from scios.runtime.agent.agent import Agent as RuntimeAgent


class RuntimeAgentAdapter(Agent):
    """Agency-level adapter over the canonical runtime Agent."""

    def __init__(
        self,
        name: str,
        version: str = "0.3.0",
        *,
        memory=None,
        router=None,
        runtime_agent=None,
        planner=None,
    ) -> None:
        self._runtime_agent = (
            runtime_agent
            if runtime_agent is not None
            else RuntimeAgent(
                name=name,
                memory=memory,
                router=router,
                planner=planner,
            )
        )

        self._id = str(__import__("uuid").uuid4())
        self._name = name
        self._version = version
        self._created_at = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()

        self._state = "idle"
        self._enabled = True
        self._executions = 0

    @property
    def runtime_agent(self):
        return self._runtime_agent

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def created_at(self):
        return self._created_at

    @property
    def state(self):
        return self._state

    @property
    def enabled(self):
        return self._enabled

    @property
    def executions(self):
        return self._executions

    @property
    def memory(self):
        return self._runtime_agent.memory

    @property
    def router(self):
        return self._runtime_agent.router

    @property
    def tool_router(self):
        return self._runtime_agent.tool_router

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def reset(self):
        self._runtime_agent.reset()
        self._state = "idle"
        self._executions = 0

    def remember(self, key, value):
        self._runtime_agent.remember(key, value)

    def recall(self, key, default=None):
        return self._runtime_agent.recall(key, default)

    def execute_tool(self, name: str, **kwargs):
        return self._runtime_agent.execute_tool(name, **kwargs)

    def run(self, task, *args, **kwargs):
        if args:
            raise TypeError(
                "RuntimeAgentAdapter.run() does not support positional "
                "execution arguments."
            )
        return self._runtime_agent.run(task, **kwargs)

    def execute(self, task, *args, **kwargs):
        if task is None:
            raise ValueError("Task cannot be None.")
        if not self._enabled:
            raise RuntimeError(
                f"Agent '{self._name}' is disabled."
            )

        self._state = "running"
        try:
            return self.run(task, *args, **kwargs)
        finally:
            self._executions += 1
            self._state = "idle"

    def __call__(self, task, *args, **kwargs):
        return self.execute(task, *args, **kwargs)

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} "
            f"name={self._name!r} "
            f"version={self._version!r} "
            f"state={self._state!r}>"
        )

    def status(self):
        return {
            "id": self._id,
            "name": self._name,
            "version": self._version,
            "state": self._state,
            "enabled": self._enabled,
            "executions": self._executions,
            "created_at": self._created_at,
        }


__all__ = ["RuntimeAgentAdapter"]
