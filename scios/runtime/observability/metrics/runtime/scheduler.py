# ==============================================================================
# Part 1. Header
# ==============================================================================

from __future__ import annotations


import json
import time
import threading
import copy


from typing import Any
from typing import Callable
from typing import TypeAlias
from typing import TypedDict


from collections import deque
from collections.abc import Iterator



# ==============================================================================
# Part 2. Constants
# ==============================================================================


DEFAULT_NAME: str = "runtime"


DEFAULT_ENABLED: bool = True


DEFAULT_RUNNING: bool = False


DEFAULT_INTERVAL: float = 1.0


DEFAULT_MAX_TICKS: int = 1024


DEFAULT_TICKS: int = 0


DEFAULT_EXECUTED: int = 0


DEFAULT_FAILED: int = 0


DEFAULT_SUCCESS: int = 0


DEFAULT_FAILURE: int = 0



__all__ = [

    # constants

    "DEFAULT_NAME",
    "DEFAULT_ENABLED",
    "DEFAULT_RUNNING",
    "DEFAULT_INTERVAL",
    "DEFAULT_MAX_TICKS",
    "DEFAULT_TICKS",
    "DEFAULT_EXECUTED",
    "DEFAULT_FAILED",
    "DEFAULT_SUCCESS",
    "DEFAULT_FAILURE",


    # types

    "ScheduledTask",
    "TaskList",
    "SchedulerState",
    "SchedulerStats",


    # runtime

    "RuntimeScheduler",

]



# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================


ScheduledTask: TypeAlias = dict[str, Any]


TaskList: TypeAlias = list[ScheduledTask]



class SchedulerState(TypedDict):

    name: str

    enabled: bool

    running: bool

    interval: float

    max_ticks: int

    ticks: int

    executed: int

    failed: int

    tasks: TaskList



class SchedulerStats(TypedDict):

    ticks: int

    executed: int

    failed: int

    success_rate: float

    failure_rate: float

    size: int



# ==============================================================================
# Part 4. RuntimeScheduler
# ==============================================================================


class RuntimeScheduler:


    __slots__ = (

        "_name",

        "_enabled",

        "_running",

        "_interval",

        "_max_ticks",

        "_tasks",

        "_ticks",

        "_executed",

        "_failed",

        "_successes",

        "_failures",

        "_thread",

        "_created_at",

        "_last_tick",

    )



    def __init__(
        self,
        *,
        name: str = DEFAULT_NAME,
        enabled: bool = DEFAULT_ENABLED,
        running: bool = DEFAULT_RUNNING,
        interval: float = DEFAULT_INTERVAL,
        max_ticks: int = DEFAULT_MAX_TICKS,
    ) -> None:


        # identity

        self._name = str(name)



        # lifecycle

        self._enabled = bool(enabled)

        self._running = bool(running)



        # configuration

        self._interval = float(interval)

        self._max_ticks = int(max_ticks)



        # tasks

        self._tasks = deque()



        # counters

        self._ticks = DEFAULT_TICKS

        self._executed = DEFAULT_EXECUTED

        self._failed = DEFAULT_FAILED



        # statistics

        self._successes = DEFAULT_SUCCESS

        self._failures = DEFAULT_FAILURE



        # threading

        self._thread = None



        # timestamps

        self._created_at = time.time()

        self._last_tick = None



    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------


    @property
    def name(self) -> str:

        return self._name



    @property
    def enabled(self) -> bool:

        return self._enabled



    @property
    def running(self) -> bool:

        return self._running



    @property
    def interval(self) -> float:

        return self._interval



    @property
    def max_ticks(self) -> int:

        return self._max_ticks



    @property
    def tasks(self) -> TaskList:

        return list(self._tasks)



    @property
    def ticks(self) -> int:

        return self._ticks



    @property
    def executed(self) -> int:

        return self._executed



    @property
    def failed(self) -> int:

        return self._failed



    @property
    def successes(self) -> int:

        return self._successes



    @property
    def failures(self) -> int:

        return self._failures



    @property
    def created_at(self) -> float:

        return self._created_at



    @property
    def last_tick(self) -> float | None:

        return self._last_tick



    @property
    def size(self) -> int:

        return len(self._tasks)



    @property
    def utilization(self) -> float:


        if self._max_ticks <= 0:

            return 0.0


        return min(
            1.0,
            self._ticks / self._max_ticks,
        )

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


    def start(self):

        self._running = True

        return self



    def stop(self):

        self._running = False


        if self._thread is not None:

            if self._thread.is_alive():

                self._thread.join(
                    timeout=self._interval * 2
                )


            self._thread = None


        return self



    def enable(self):

        self._enabled = True

        return self



    def disable(self):

        self._enabled = False

        return self



    def clear(self):

        self._tasks.clear()

        self.reset_statistics()

        self._ticks = DEFAULT_TICKS

        self._last_tick = None

        return self



    def reset(self):

        self.stop()


        self._enabled = DEFAULT_ENABLED

        self._running = DEFAULT_RUNNING

        self._interval = DEFAULT_INTERVAL

        self._max_ticks = DEFAULT_MAX_TICKS


        return self.clear()



    def tick(self):

        if not self._enabled:

            self.record_failure()

            return False


        if self._max_ticks > 0 and self._ticks >= self._max_ticks:

            return False


        self._ticks += 1

        self._last_tick = time.time()


        success = True


        for task in list(self._tasks):

            try:

                callback = task.get(
                    "callback"
                )


                if callable(callback):

                    callback()


                self._executed += 1

                self.record_success()


            except Exception:

                success = False

                self.record_failure()


        return success


    def run_once(self):
        """
        Execute one scheduler cycle.
        """


        if not self._enabled:

            return False



        if self._max_ticks > 0 and self._ticks >= self._max_ticks:

            return False



        self._ticks += 1

        self._last_tick = time.time()



        success = True



        for task in list(self._tasks):

            try:

                callback = task.get(
                    "callback"
                )


                if callable(callback):

                    callback()


                self._executed += 1

                self.record_success()



            except Exception:

                success = False

                self.record_failure()



        return success


    def run_forever(self):
        """
        Start scheduler loop in background thread.
        """

        if self._running:

            return self



        self._running = True



        def loop():

            while self._running:

                self.tick()


                time.sleep(
                    self._interval
                )



        self._thread = threading.Thread(

            target=loop,

            daemon=True,

            name=f"{self._name}-scheduler",

        )


        self._thread.start()


        return self



# ==============================================================================
# Part 6. Task API
# ==============================================================================


    def add(
        self,
        task: ScheduledTask,
    ) -> bool:


        if len(self._tasks) >= self._max_ticks:

            return False



        self._tasks.append(
            self.normalize(task)
        )


        return True



    def add_many(
        self,
        tasks: TaskList,
    ) -> bool:


        result = True


        for task in tasks:

            if not self.add(task):

                result = False


        return result



    def append(
        self,
        task: ScheduledTask,
    ) -> bool:


        return self.add(task)



    def extend(
        self,
        tasks: TaskList,
    ) -> bool:


        return self.add_many(tasks)



    def remove(
        self,
        task: ScheduledTask,
    ) -> bool:


        try:

            self._tasks.remove(task)

            return True


        except ValueError:

            return False



    def pop(
        self,
        index: int = -1,
    ):


        if not self._tasks:

            return None



        tasks = list(self._tasks)


        value = tasks.pop(index)


        self._tasks = deque(tasks)


        return value



    def latest(self):


        if not self._tasks:

            return None


        return self._tasks[-1]



    def first(self):


        if not self._tasks:

            return None


        return self._tasks[0]



    def get(
        self,
        index: int,
    ):


        try:

            return self.tasks[index]


        except IndexError:

            return None



    def task_list(self):

        return list(self._tasks)



    def clear_tasks(self):

        self._tasks.clear()

        return self



    def has_tasks(self):

        return bool(self._tasks)



    def task_count(self):

        return len(self._tasks)



# ==============================================================================
# Part 7. Statistics
# ==============================================================================


    def record_success(self):

        self._executed += 1

        self._successes += 1

        return self



    def record_failure(self):

        self._failed += 1

        self._failures += 1

        return self



    def success_rate(self):


        total = (
            self._successes
            +
            self._failures
        )


        if total == 0:

            return 0.0


        return self._successes / total



    def failure_rate(self):


        total = (
            self._successes
            +
            self._failures
        )


        if total == 0:

            return 0.0


        return self._failures / total



    def total_processed(self):

        return (
            self._successes
            +
            self._failures
        )



    def statistics(self):

        return {

            "ticks": self._ticks,

            "executed": self._executed,

            "failed": self._failed,

            "success_rate": self.success_rate(),

            "failure_rate": self.failure_rate(),

            "size": self.size,

        }



    def reset_statistics(self):

        self._executed = DEFAULT_EXECUTED

        self._failed = DEFAULT_FAILED

        self._successes = DEFAULT_SUCCESS

        self._failures = DEFAULT_FAILURE


        return self



# ==============================================================================
# Part 8. Operations
# ==============================================================================


    def clone(self):

        return self.from_dict(
            self.to_dict()
        )



    def copy(self):

        return self.clone()



    def merge(
        self,
        other,
    ):


        self.extend(
            other.tasks
        )


        self._ticks = other.ticks

        self._executed = other.executed

        self._failed = other.failed


        return self



    def update(
        self,
        values,
    ):


        if isinstance(values, dict):

            values = [
                values
            ]


        for value in values:

            self.add(value)


        return self



    def snapshot(self):

        return self.to_dict()



    def restore(
        self,
        state: dict,
    ):


        restored = self.from_dict(
            state
        )


        self._name = restored.name

        self._enabled = restored.enabled

        self._running = restored.running

        self._interval = restored.interval

        self._max_ticks = restored.max_ticks

        self._tasks = restored._tasks

        self._ticks = restored.ticks

        self._executed = restored.executed

        self._failed = restored.failed


        return self

# ==============================================================================
# Part 9. Validation
# ==============================================================================


    def validate_name(
        self,
        name: str | None = None,
    ) -> bool:
        """
        Validate scheduler name.
        """

        value = (
            self._name
            if name is None
            else name
        )


        return (

            isinstance(
                value,
                str,
            )

            and

            len(
                value.strip()
            ) > 0

        )





    def validate_tasks(
        self,
        tasks=None,
    ) -> bool:
        """
        Validate scheduled tasks.
        """


        values = (

            self._tasks

            if tasks is None

            else tasks

        )


        if not isinstance(
            values,
            (list, deque),
        ):

            return False



        for task in values:


            if isinstance(
                task,
                dict,
            ):

                continue



            if callable(task):

                continue



            return False



        return True





    def validate_limits(self) -> bool:
        """
        Validate scheduler limits.
        """


        return (

            isinstance(
                self._interval,
                (int, float),
            )

            and

            self._interval >= 0


            and


            isinstance(
                self._max_ticks,
                int,
            )

            and

            self._max_ticks >= 0

        )





    def validate(self) -> bool:
        """
        Validate scheduler state.
        """


        return (

            self.validate_name()

            and

            self.validate_tasks()

            and

            self.validate_limits()

        )





    def normalize(
        self,
        task=None,
    ):
        """
        Normalize task format.
        """


        if task is None:

            return {}



        if isinstance(
            task,
            dict,
        ):

            return dict(task)



        if callable(task):

            return {

                "callback": task

            }



        return task




# ==============================================================================
# Part 10. Serialization
# ==============================================================================


    def to_dict(self):
        """
        Convert scheduler state to dictionary.
        """

        tasks = []


        for task in self._tasks:

            if isinstance(task, dict):

                item = {}

                for key, value in task.items():

                    if key == "callback":

                        continue


                    item[key] = value


                tasks.append(item)

            else:

                tasks.append(task)



        return {

            "name":
                self.name,

            "enabled":
                self.enabled,

            "running":
                self.running,

            "interval":
                self.interval,

            "max_ticks":
                self.max_ticks,

            "tasks":
                tasks,

            "ticks":
                self.ticks,

            "executed":
                self.executed,

            "failed":
                self.failed,

        }



    @classmethod
    def from_dict(
        cls,
        data,
    ):
        """
        Restore scheduler from dictionary.
        """


        scheduler = cls(

            name=data.get(
                "name",
                DEFAULT_NAME,
            ),

            enabled=data.get(
                "enabled",
                DEFAULT_ENABLED,
            ),

            running=data.get(
                "running",
                DEFAULT_RUNNING,
            ),

            interval=data.get(
                "interval",
                DEFAULT_INTERVAL,
            ),

            max_ticks=data.get(
                "max_ticks",
                DEFAULT_MAX_TICKS,
            ),

        )


        scheduler._tasks = deque()



        for task in data.get(
            "tasks",
            [],
        ):


            if isinstance(task, dict):

                item = dict(task)

                # callback cannot be restored from JSON
                item.setdefault(
                    "callback",
                    None,
                )

                scheduler._tasks.append(
                    item
                )


            else:

                scheduler._tasks.append(
                    task
                )



        scheduler._ticks = data.get(
            "ticks",
            DEFAULT_TICKS,
        )


        scheduler._executed = data.get(
            "executed",
            DEFAULT_EXECUTED,
        )


        scheduler._failed = data.get(
            "failed",
            DEFAULT_FAILED,
        )


        return scheduler





    def to_tuple(self):
        """
        Convert scheduler state to tuple.
        """


        return (

            self.name,

            self.enabled,

            self.running,

            self.interval,

            self.max_ticks,

            tuple(
                self.to_dict()["tasks"]
            ),

            self.ticks,

            self.executed,

            self.failed,

        )





    @classmethod
    def from_tuple(
        cls,
        data,
    ):
        """
        Restore scheduler from tuple.
        """


        scheduler = cls(

            name=data[0],

            enabled=data[1],

            running=data[2],

            interval=data[3],

            max_ticks=data[4],

        )


        scheduler._tasks = deque()



        for task in data[5]:

            if isinstance(task, dict):

                item = dict(task)

                item.setdefault(
                    "callback",
                    None,
                )

                scheduler._tasks.append(
                    item
                )

            else:

                scheduler._tasks.append(
                    task
                )



        scheduler._ticks = data[6]

        scheduler._executed = data[7]

        scheduler._failed = data[8]


        return scheduler





    def to_json(self):
        """
        Serialize scheduler to JSON.
        """


        return json.dumps(
            self.to_dict()
        )





    @classmethod
    def from_json(
        cls,
        data,
    ):
        """
        Deserialize scheduler from JSON.
        """


        return cls.from_dict(
            json.loads(data)
        )

# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


    def summary(self):


        return {

            "name":
                self.name,

            "tasks":
                self.size,

            "ticks":
                self.ticks,

            "executed":
                self.executed,

            "failed":
                self.failed,

        }





    def diagnostics(self):


        return {


            "status":
                self.status(),


            "name":
                self.name,


            "enabled":
                self.enabled,


            "running":
                self.running,


            "size":
                self.size,


            "utilization":
                self.utilization,


        }





    def report(self):


        return {


            "summary":
                self.summary(),


            "diagnostics":
                self.diagnostics(),


            "status":
                self.status(),


        }





    def status(self):


        if not self.enabled:

            return "disabled"



        if self.running:

            return "running"



        return "enabled"





# ==============================================================================
# Part 12. Protocols
# ==============================================================================


    def __len__(self):

        return self.size




    def __contains__(
        self,
        item,
    ):


        return item in self._tasks




    def __iter__(self) -> Iterator:


        return iter(
            self._tasks
        )




    def __hash__(self):


        return hash(

            (

                self.name,

                self.interval,

                self.max_ticks,

            )

        )





    def __eq__(
        self,
        other,
    ):


        if not isinstance(
            other,
            RuntimeScheduler,
        ):

            return False



        return (

            self.to_dict()

            ==

            other.to_dict()

        )





    def __repr__(self):


        return (

            "RuntimeScheduler("

            f"name={self.name!r}, "

            f"tasks={self.size}, "

            f"running={self.running}"

            ")"

        )





    def __str__(self):


        return (

            f"{self.name}"

            f"(tasks={self.size})"

        )





    def __bool__(self):

        return (

            self.validate_name()

            and

            self._max_ticks > 0

        )             