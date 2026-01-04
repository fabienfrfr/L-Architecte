import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.langchain import LangChainInstrumentor

logger = logging.getLogger(__name__)


class PhoenixProvider:
    def __init__(self):
        self.endpoint = os.getenv(
            "PHOENIX_OTLP_ENDPOINT", "http://localhost:4318/v1/traces"
        )
        # Defining the project name factually
        self.project_name = "AgenticArchitect"

    def initialize(self) -> None:
        """
        Initializes OpenTelemetry with proper resource naming to avoid 'default' project.
        """
        try:
            # Check if already initialized
            current_provider = trace.get_tracer_provider()
            if hasattr(current_provider, "get_tracer"):
                return

            # SOLID: Defining the resource with the service name
            resource = Resource.create(
                {
                    "service.name": self.project_name,
                    "project.name": self.project_name,  # Phoenix uses this for UI grouping
                }
            )

            provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(provider)

            # OTLP/HTTP Exporter
            exporter = OTLPSpanExporter(endpoint=self.endpoint)
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)

            # Instrument LangChain/LangGraph
            if not LangChainInstrumentor().is_instrumented_by_opentelemetry:
                LangChainInstrumentor().instrument()

            logger.info(
                f"✅ Phoenix project '{self.project_name}' initialized at {self.endpoint}"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Phoenix provider: {e}")


def setup_observability() -> None:
    PhoenixProvider().initialize()
