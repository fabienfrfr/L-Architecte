import multiprocessing
import sys
import logging

from nicegui import ui
from apps.architect.ui.layout import ArchitectLayout
from apps.architect.controller import ArchitectController
from apps.architect.core.observability import setup_observability

# Configure Logger for production-level feedback
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class TheArchitectApp:
    """
    Main Application class following the Controller-View pattern.
    Responsible for orchestrating the UI and the Agentic Pipeline.
    """

    def __init__(self) -> None:
        # Initialize Observability (Phoenix/OTLP) to trace agentic traces
        setup_observability()

        # Core logic controller (LangGraph orchestration)
        self.controller = ArchitectController()

        # UI Layout with callback to the analysis handler
        self.view = ArchitectLayout(on_start=self.handle_analysis)

    async def handle_analysis(self, requirements: str) -> None:
        """
        Handles the full pipeline execution with UI feedback.
        Triggers the Analyst -> Architect -> Engineer swimlane.
        """
        self.view.toggle_loader(True)
        try:
            # The controller runs the LangGraph workflow
            # Observability captures the nested agent calls automatically
            result = await self.controller.run_full_pipeline(requirements)
            self.view.display_results(result)
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            ui.notify(f"Error: {str(e)}", type="negative")
        finally:
            self.view.toggle_loader(False)


def start_app() -> None:
    """
    Bootstrap function to handle platform-specific configurations
    and launch the NiceGUI interface on port 8080.
    """
    # Necessary for OpenTelemetry and Ollama calls in multi-agent environments
    if sys.platform != "win32":
        try:
            multiprocessing.set_start_method("spawn", force=True)
        except RuntimeError:
            pass

    # Instantiate the application
    TheArchitectApp()

    # Start NiceGUI server
    ui.run(
        title="TheArchitect",
        port=8080,
        native=False,
        reload=False,
        dark=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    start_app()
