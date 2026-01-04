import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.langchain import LangChainInstrumentor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObservabilityProvider(ABC):
    """Abstract Base Class for Observability Providers (Interface Segregation)."""

    @abstractmethod
    def initialize(self) -> None:
        pass


class PhoenixProvider(ObservabilityProvider):
    """
    Implementation of Phoenix Observability using OpenTelemetry.
    """

    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or os.getenv(
            "PHOENIX_OTLP_ENDPOINT", "http://localhost:4317/v1/traces"
        )
        self.service_name = "AgenticArchitect"

    def initialize(self) -> None:
        """Initializes the OTLP exporter and instruments LangChain."""
        try:
            # Set up the Tracer Provider
            provider = TracerProvider()
            trace.set_tracer_provider(provider)

            # Configure OTLP Exporter (HTTP)
            exporter = OTLPSpanExporter(endpoint=self.endpoint)
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)

            # Instrument LangChain/LangGraph
            if not LangChainInstrumentor().is_instrumented_by_opentelemetry:
                LangChainInstrumentor().instrument()

            logger.info(f"Phoenix observability initialized at {self.endpoint}")
        except Exception as e:
            logger.error(f"Failed to initialize Phoenix provider: {e}")
            raise


def setup_observability() -> None:
    """
    Factory function to initialize observability based on environment.
    Prevents initialization during test execution to honor TDD patterns.
    """
    if os.getenv("ENV") == "test":
        logger.info("Skipping observability initialization in test environment.")
        return

    provider = PhoenixProvider()
    provider.initialize()
