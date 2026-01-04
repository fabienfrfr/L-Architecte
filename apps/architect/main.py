import multiprocessing
import sys
import logging

from nicegui import ui
from apps.architect.ui.layout import ArchitectLayout
from apps.architect.controller import ArchitectController
from apps.architect.core.observability import setup_observability

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TheArchitectApp:
    """
    Main Application class following the Controller-View pattern.
    Responsible for orchestrating the UI and the Agentic Pipeline.
    """

    def __init__(self) -> None:
        # Initialize Observability (Phoenix/OTLP) before the controller starts
        setup_observability()

        self.controller = ArchitectController()
        self.view = ArchitectLayout(on_start=self.handle_analysis)

    async def handle_analysis(self, requirements: str) -> None:
        """Handles the full pipeline execution with UI feedback."""
        self.view.toggle_loader(True)
        try:
            # The Phoenix instrumentation will automatically capture this call
            result = await self.controller.run_full_pipeline(requirements)
            self.view.display_results(result)
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            ui.notify(f"Error: {str(e)}", type="negative")
        finally:
            self.view.toggle_loader(False)


def start_app() -> None:
    """
    Bootstrap function to handle platform-specific configurations
    and launch the NiceGUI interface.
    """
    if sys.platform != "win32":
        try:
            multiprocessing.set_start_method("spawn", force=True)
        except RuntimeError:
            pass

    # Instantiate the App (which triggers observability)
    TheArchitectApp()

    # Run NiceGUI
    ui.run(
        title="TheArchitect",
        port=8080,
        native=False,
        reload=False,  # Recommended when using complex instrumentation/multiprocessing
    )


if __name__ in {"__main__", "__mp_main__"}:
    start_app()
