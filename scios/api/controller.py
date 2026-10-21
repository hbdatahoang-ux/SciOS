class SciOSController:
    """
    Controller layer: interacts only with SciOS Runtime/Kernel.
    """

    def __init__(self, scios):
        self._scios = scios

    def run(self, request):
        return self._scios.run(request.task)

    def reason(self, request):
        return self._scios.reason(request.context)

    def tool(self, request):
        return self._scios.tool(request.name, request.inputs)

    def graph(self, request):
        return self._scios.graph(request.operation)

    def status(self):
        return self._scios.status()

    def health(self):
        return {"status": "ok"}
