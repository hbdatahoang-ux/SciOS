"""
SciOS-NG Dashboard Runtime Package

Package:

    scios.runtime.observability.dashboard


Provides:

    - DashboardWebServer
    - Dashboard Viewer integration
    - Web runtime APIs
    - WebSocket runtime
    - Middleware
    - Authentication
    - Static assets
    - Events & Hooks
    - Lifecycle
    - Serialization


Architecture:

    Kernel
      |
      |
    Runtime
      |
      |
    Observability
      |
      |
    Dashboard
      |
      ├── Web Server
      ├── API Router
      ├── WebSocket
      ├── Middleware
      ├── Auth
      └── Static UI


"""


from __future__ import annotations


# ==========================================================
# Package Metadata
# ==========================================================


__name__ = (
    "scios.runtime.observability.dashboard"
)


__version__ = (
    "0.1.0"
)


__description__ = (
    "SciOS-NG Dashboard Runtime"
)



# ==========================================================
# Core Dashboard Runtime
# ==========================================================


try:

    from .web import (
        DashboardWebServer,
    )

except ImportError:

    DashboardWebServer = None



# ==========================================================
# Optional Viewer Layer
# ==========================================================


try:

    from .viewer import (
        DashboardViewer,
    )

except ImportError:

    DashboardViewer = None



# ==========================================================
# Optional Components
# ==========================================================


try:

    from .router import (
        DashboardRouter,
    )

except ImportError:

    DashboardRouter = None



try:

    from .session import (
        DashboardSession,
    )

except ImportError:

    DashboardSession = None



try:

    from .events import (
        DashboardEventBus,
    )

except ImportError:

    DashboardEventBus = None



# ==========================================================
# Public API
# ==========================================================


__all__ = [

    # metadata

    "__version__",


    "__description__",


    # core

    "DashboardWebServer",


    # viewer

    "DashboardViewer",


    # routing

    "DashboardRouter",


    # session

    "DashboardSession",


    # events

    "DashboardEventBus",

]



# ==========================================================
# Factory Helpers
# ==========================================================


def create_dashboard_server(
    viewer=None,
    **kwargs,
):
    """
    Create Dashboard Web Server.

    Example:

        server = create_dashboard_server()

    """

    if DashboardWebServer is None:

        raise RuntimeError(

            "DashboardWebServer unavailable"

        )


    return DashboardWebServer(

        viewer=viewer,

        **kwargs,

    )



def dashboard_info():
    """
    Return package information.
    """

    return {

        "name":

            __name__,


        "version":

            __version__,


        "description":

            __description__,


        "components":

            {

                "web":

                    DashboardWebServer
                    is not None,


                "viewer":

                    DashboardViewer
                    is not None,


                "router":

                    DashboardRouter
                    is not None,


                "session":

                    DashboardSession
                    is not None,


                "events":

                    DashboardEventBus
                    is not None,

            },

    }