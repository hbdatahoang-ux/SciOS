# ==============================================================================
# pipeline.py
# ==============================================================================


from __future__ import annotations


import json
import time
import copy

from typing import Any
from typing import Callable
from typing import TypeAlias

from collections import deque
from collections.abc import Iterator



# ==============================================================================
# Part 2. Constants
# ==============================================================================


DEFAULT_NAME = "runtime"

DEFAULT_ENABLED = True

DEFAULT_RUNNING = False


DEFAULT_STAGES = 0


DEFAULT_EXECUTED = 0

DEFAULT_FAILED = 0


DEFAULT_SUCCESS = 0

DEFAULT_FAILURE = 0



__all__ = [

    "RuntimePipeline",

    "PipelineStage",

    "StageList",

    "PipelineState",

    "PipelineStats",

]



# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================


PipelineStage: TypeAlias = dict[str, Any]


StageList: TypeAlias = list[PipelineStage]


PipelineState: TypeAlias = dict[str, Any]


PipelineStats: TypeAlias = dict[str, int]



# ==============================================================================
# Part 4. RuntimePipeline
# ==============================================================================


class RuntimePipeline:
    """
    Runtime execution pipeline.

    Manages ordered execution stages.
    """


    __slots__ = (

        "_name",

        "_enabled",

        "_running",

        "_stages",

        "_executed",

        "_failed",

        "_successes",

        "_failures",

        "_created_at",

        "_last_run",

    )



    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------


    def __init__(

        self,

        name: str = DEFAULT_NAME,

        enabled: bool = DEFAULT_ENABLED,

        running: bool = DEFAULT_RUNNING,

    ):


        self._name = name


        self._enabled = enabled


        self._running = running


        self._stages = deque()


        self._executed = DEFAULT_EXECUTED


        self._failed = DEFAULT_FAILED


        self._successes = DEFAULT_SUCCESS


        self._failures = DEFAULT_FAILURE


        self._created_at = time.time()


        self._last_run = None



    # ==========================================================================
    # Properties
    # ==========================================================================


    @property
    def name(self):

        return self._name



    @property
    def enabled(self):

        return self._enabled



    @property
    def running(self):

        return self._running



    @property
    def stages(self):

        return list(self._stages)



    @property
    def executed(self):

        return self._executed



    @property
    def failed(self):

        return self._failed



    @property
    def successes(self):

        return self._successes



    @property
    def failures(self):

        return self._failures



    @property
    def created_at(self):

        return self._created_at



    @property
    def last_run(self):

        return self._last_run



    @property
    def size(self):

        return len(self._stages)



    @property
    def utilization(self):

        if not self._stages:

            return 0.0


        return (

            self._executed

            /

            len(self._stages)

        )

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


    def start(self):

        self._running = True

        return self



    def stop(self):

        self._running = False

        return self



    def enable(self):

        self._enabled = True

        return self



    def disable(self):

        self._enabled = False

        return self



    def clear(self):

        self._stages.clear()

        return self



    def reset(self):

        self._running = False
        self._enabled = True

        self._stages.clear()

        self._executed = 0
        self._failed = 0
        self._successes = 0
        self._failures = 0

        self._last_run = None

        return self



    def run(self, data=None):

        if not self._enabled:

            return False


        success = True


        self._last_run = time.time()


        for stage in list(self._stages):

            result = self.run_stage(
                stage,
                data,
            )


            if result is False:

                success = False



        return success



    def run_stage(
        self,
        stage,
        *args,
        **kwargs,
    ):

        try:

            callback = None


            if isinstance(stage, dict):

                callback = stage.get(
                    "callback"
                )


            elif callable(stage):

                callback = stage



            if callback:

                result = callback(
                    *args,
                    **kwargs
                )

            else:

                result = stage



            self.record_success()

            return result



        except Exception:

            self.record_failure()

            raise


    def execute(self, data=None):

        return self.run(data)





# ==============================================================================
# Part 6. Stage API
# ==============================================================================


    def add(
        self,
        stage,
    ):
        self._stages.append(
            self.normalize(stage)
        )

        return self



    def add_many(
        self,
        stages,
    ):

        for stage in stages:
            self.add(stage)

        return self



    def append(
        self,
        stage,
    ):

        return self.add(stage)



    def extend(
        self,
        stages,
    ):

        return self.add_many(stages)



    def remove(
        self,
        stage,
    ):

        if isinstance(stage, int):

            del self._stages[stage]

        else:

            self._stages.remove(stage)


        return self



    def pop(
        self,
        index=-1,
    ):

        if index == -1:
            return self._stages.pop()


        value = self._stages[index]

        del self._stages[index]

        return value



    def latest(self):

        if not self._stages:
            return None

        return self._stages[-1]



    def first(self):

        if not self._stages:
            return None

        return self._stages[0]



    def get(
        self,
        index,
    ):

        return self._stages[index]



    def stage_list(self):

        return list(self._stages)



    def clear_stages(self):

        self._stages.clear()

        return self



    def has_stages(self):

        return len(self._stages) > 0



    @property
    def stage_count(self):

        return len(self._stages)





# ==============================================================================
# Part 7. Statistics
# ==============================================================================


    def record_success(self):

        self._successes += 1

        self._executed += 1

        return self



    def record_failure(self):

        self._failures += 1

        self._failed += 1

        return self



    def success_rate(self):

        total = self.total_processed()

        if total == 0:

            return 0.0


        return self._successes / total



    def failure_rate(self):

        total = self.total_processed()

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

            "executed":
                self._executed,

            "failed":
                self._failed,

            "successes":
                self._successes,

            "failures":
                self._failures,

            "total":
                self.total_processed(),

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

        return copy.deepcopy(
            self
        )



    def copy(self):

        return self.clone()



    def merge(
        self,
        other,
    ):

        self._stages.extend(
            other.stages
        )

        return self



    def update(
        self,
        data=None,
        **kwargs,
    ):


        if data is None:
            data = {}


        if "name" in data:
            self._name = data["name"]


        if "enabled" in data:
            self._enabled = data["enabled"]


        if "running" in data:
            self._running = data["running"]


        if "stages" in data:

            self._stages = deque(
                data["stages"]
            )


        for key,value in kwargs.items():

            if hasattr(
                self,
                f"_{key}"
            ):

                setattr(
                    self,
                    f"_{key}",
                    value,
                )


        return self


    def snapshot(self):

        return self.to_dict()



    def restore(
        self,
        snapshot,
    ):

        restored = self.from_dict(
            snapshot
        )


        self._name = restored._name

        self._enabled = restored._enabled

        self._running = restored._running

        self._stages = restored._stages

        self._executed = restored._executed

        self._failed = restored._failed

        self._successes = restored._successes

        self._failures = restored._failures

        self._last_run = restored._last_run


        return self

# ==============================================================================
# Part 9. Validation
# ==============================================================================


    def validate_name(
        self,
        name: str | None = None,
    ) -> bool:


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

            and len(value.strip()) > 0

        )



    def validate_stages(
        self,
        stages=None,
    ) -> bool:


        values = (

            self._stages

            if stages is None

            else stages

        )


        if not isinstance(
            values,
            (list, deque),
        ):

            return False



        for stage in values:


            if not isinstance(
                stage,
                dict,
            ):

                return False



        return True




    def validate(self) -> bool:


        return (

            self.validate_name()

            and self.validate_stages()

        )




    def normalize(
        self,
        stage=None,
    ):


        if stage is None:

            return {}



        if isinstance(
            stage,
            dict,
        ):

            return dict(stage)



        if callable(stage):

            return {

                "callback": stage

            }



        return stage





# ==============================================================================
# Part 10. Serialization
# ==============================================================================


    def to_dict(self):


        return {


            "name":

                self.name,


            "enabled":

                self.enabled,


            "running":

                self.running,


            "stages":

                [

                    self._serialize_stage(stage)

                    for stage in self._stages

                ],



            "executed":

                self.executed,


            "failed":

                self.failed,


            "successes":

                self.successes,


            "failures":

                self.failures,


            "created_at":

                self.created_at,


            "last_run":

                self.last_run,

        }




    def _serialize_stage(
        self,
        stage,
    ):


        if not isinstance(
            stage,
            dict,
        ):

            return stage



        result = {}


        for key, value in stage.items():


            if callable(value):

                result[key] = None

            else:

                result[key] = value



        return result




    @classmethod
    def from_dict(
        cls,
        data,
    ):


        pipeline = cls(

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

        )



        pipeline._stages = deque(

            data.get(
                "stages",
                [],
            )

        )



        pipeline._executed = data.get(
            "executed",
            DEFAULT_EXECUTED,
        )


        pipeline._failed = data.get(
            "failed",
            DEFAULT_FAILED,
        )


        pipeline._successes = data.get(
            "successes",
            DEFAULT_SUCCESS,
        )


        pipeline._failures = data.get(
            "failures",
            DEFAULT_FAILURE,
        )


        pipeline._created_at = data.get(
            "created_at",
            time.time(),
        )


        pipeline._last_run = data.get(
            "last_run",
            None,
        )


        return pipeline




    def to_tuple(self):


        return (

            self.name,

            self.enabled,

            self.running,

            tuple(self.stages),

            self.executed,

            self.failed,

            self.successes,

            self.failures,

        )




    @classmethod
    def from_tuple(
        cls,
        data,
    ):


        pipeline = cls(

            name=data[0],

            enabled=data[1],

            running=data[2],

        )


        pipeline._stages = deque(
            data[3]
        )


        pipeline._executed = data[4]

        pipeline._failed = data[5]

        pipeline._successes = data[6]

        pipeline._failures = data[7]


        return pipeline




    def to_json(self):


        return json.dumps(

            self.to_dict()

        )




    @classmethod
    def from_json(
        cls,
        data,
    ):


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


            "stages":

                self.size,


            "running":

                self.running,


            "enabled":

                self.enabled,


            "executed":

                self.executed,


            "failed":

                self.failed,

        }




    def diagnostics(self):


        return {


            "summary":

                self.summary(),


            "statistics":

                self.statistics(),


            "valid":

                self.validate(),

        }




    def report(self):


        return {


            "pipeline":

                self.name,


            "diagnostics":

                self.diagnostics(),

        }




    def status(self):


        if not self.enabled:

            return "disabled"



        if self.running:

            return "running"



        return "ready"





# ==============================================================================
# Part 12. Protocols
# ==============================================================================


    def __len__(self):

        return len(self._stages)




    def __contains__(
        self,
        item,
    ):

        return item in self._stages




    def __iter__(self) -> Iterator:

        return iter(
            self._stages
        )




    def __hash__(self):

        return hash(
            (
                self._name,
                self._created_at,
            )
        )




    def __eq__(
        self,
        other,
    ):


        if not isinstance(
            other,
            RuntimePipeline,
        ):

            return False



        return (

            self.to_tuple()

            ==

            other.to_tuple()

        )




    def __repr__(self):


        return (

            f"RuntimePipeline("

            f"name={self._name!r}, "

            f"stages={len(self._stages)}, "

            f"running={self._running}"

            f")"

        )




    def __str__(self):

        return self.__repr__()




    def __bool__(self):


        return (

            self._enabled

            and

            self.validate()

        )                