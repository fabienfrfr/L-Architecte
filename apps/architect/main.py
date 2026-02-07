import os
import multiprocessing
import sys
import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from nicegui import ui

# Internal project imports
from apps.architect.ui.layout import ArchitectLayout
from apps.architect.api.controller import ArchitectController
from apps.architect.api.observability import setup_observability
from apps.architect.agents.orchestrator import app_workflow

# Configure Logger for production-level feedback
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


# Check if we are in development mode via environment variable
is_dev_mode = os.getenv("APP_ENV", "prod") == "dev"

class TheArchitectApp:
    """
    Main Application class following the Controller-View pattern.
    Responsible for orchestrating the UI and the Agentic Pipeline.
    """
    def __init__(self) -> None:

        # Core logic controller (LangGraph orchestration)
        self.controller = ArchitectController()

        # UI Layout with callback to the analysis handler
        self.view = ArchitectLayout(on_start=self.handle_analysis)

        # Display the graph structure on the home page
        self.view.update_graph(app_workflow)

    async def handle_analysis(self, requirements: str) -> None:
        """
        Handles the full pipeline execution with UI feedback.
        """
        self.view.toggle_loader(True)
        try:
            result = await self.controller.run_full_pipeline(requirements)
            self.view.display_results(result)
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            ui.notify(f"Error: {str(e)}", type="negative")
        finally:
            self.view.toggle_loader(False)

# Lifecycle Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown of global shared resources.
    """
    logger.info("🚀 Starting API Engine & Observability...")
    # Global init for tracing all requests (FastAPI + NiceGUI)
    setup_observability()
    yield
    logger.info("🛑 Shutting down API Engine...")


# Instantiate FastAPI with Lifespan Swagger/OpenAPI
app = FastAPI(
    title="TheArchitect API",
    version="1.0.0",
    lifespan=lifespan,
    # Swagger need to be reform, For sure !
    docs_url="/docs" if is_dev_mode else None,
    openapi_url="/openapi.json" if is_dev_mode else None,
)


@app.get("/api/status")
async def get_status() -> Dict[str, str]:
    """
    Endpoint status.
    """
    return {"status": "ok"}

# Integrate NiceGUI

@ui.page('/')
def index_page() -> None:
    """
    Unique entry point for each web client.
    """
    TheArchitectApp()

ui.run_with(
    app,
    title="TheArchitect",
    dark=False,
)

def start_app() -> None:
    """
    Bootstrap function using ui.run_with(app) to merge FastAPI and NiceGUI.
    """
    # Necessary for OpenTelemetry and Ollama calls in multi-agent environments
    if sys.platform != "win32":
        try:
            multiprocessing.set_start_method("spawn", force=True)
        except RuntimeError:
            pass

    # Use uvicorn to serve the FastAPI app (which now contains NiceGUI)
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8080, 
        reload=False, 
        workers=1
    )

if __name__ in {"__main__", "__mp_main__"}:
    start_app()