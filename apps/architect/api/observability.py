import os
import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.langchain import LangChainInstrumentor

# Use a dedicated logger for the observability layer
logger = logging.getLogger(__name__)


class PhoenixConfig:
    """Handles configuration parameters for the Phoenix/OTLP provider."""
    
    def __init__(self) -> None:
        # Phoenix gRPC default is 4317.
        # Using 127.0.0.1 instead of localhost to avoid IPv6 resolution delays.
        self.endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:4317")
        self.project_name = "AgenticArchitect"


class PhoenixProvider:
    """
    Service responsible for initializing the OpenTelemetry tracing pipeline.
    Follows SOLID principles by isolating the telemetry setup.
    """

    def __init__(self, config: Optional[PhoenixConfig] = None) -> None:
        self.config = config or PhoenixConfig()
        self._provider: Optional[TracerProvider] = None

    def _build_resource(self) -> Resource:
        """Creates the resource metadata for the traces."""
        return Resource.create(
            {
                "service.name": self.config.project_name,
                "project.name": self.config.project_name,
            }
        )

    def initialize(self) -> None:
        """
        Configures the TracerProvider, Exporter, and Instruments LangChain.
        Uses SimpleSpanProcessor for immediate trace visibility.
        """
        try:
            # Check if global provider is already set to avoid multiple initializations
            if isinstance(trace.get_tracer_provider(), TracerProvider):
                logger.info("Phoenix Provider already initialized. Skipping.")
                return

            # Initialize Provider with Resource
            self._provider = TracerProvider(resource=self._build_resource())

            # Setup OTLP gRPC Exporter
            # Note: insecure=True is required if your local Phoenix doesn't use TLS
            exporter = OTLPSpanExporter(endpoint=self.config.endpoint, insecure=True)

            # Use SimpleSpanProcessor for development: sends spans immediately
            processor = SimpleSpanProcessor(exporter)
            self._provider.add_span_processor(processor)

            # Set global tracer provider
            trace.set_tracer_provider(self._provider)

            # Patch LangChain/Pydantic(?) to emit OpenInference spans
            self._instrument_libraries()

            logger.info(
                f"✅ Phoenix observability initialized at {self.config.endpoint}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to initialize Phoenix provider: {str(e)}")

    def _instrument_libraries(self) -> None:
        """Handles the instrumentation logic for external libraries."""
        instrumentor = LangChainInstrumentor()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()


def setup_observability() -> None:
    """Bootstrap function to start the observability service."""
    provider = PhoenixProvider()
    provider.initialize()
