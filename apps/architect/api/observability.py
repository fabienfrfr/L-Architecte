import os
import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor

# Dedicated logger for the observability layer
logger = logging.getLogger(__name__)

class PhoenixConfig:
    """Configuration for Phoenix/OTLP provider."""
    
    def __init__(self) -> None:
        # Default to gRPC port 4317. Using service name 'phoenix' for K8s/Docker networking.
        self.endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://phoenix:4317")
        self.project_name = "L-Architecte"

class PhoenixProvider:
    """
    Handles OpenTelemetry initialization for Pydantic AI.
    Integrates with Arize Phoenix using OpenInference standards.
    """

    def __init__(self, config: Optional[PhoenixConfig] = None) -> None:
        self.config = config or PhoenixConfig()
        self._provider: Optional[TracerProvider] = None

    def _build_resource(self) -> Resource:
        """Resource metadata for traces."""
        return Resource.create({
            "service.name": self.config.project_name,
            "project.name": self.config.project_name,
        })

    def initialize(self) -> None:
        """Sets up the TracerProvider and OpenInference processors."""
        try:
            if isinstance(trace.get_tracer_provider(), TracerProvider):
                return

            self._provider = TracerProvider(resource=self._build_resource())
            
            # OTLP Exporter for Phoenix (Insecure mode for local/dev cluster)
            exporter = OTLPSpanExporter(endpoint=self.config.endpoint, insecure=True)

            # Essential for Pydantic AI: translates tool calls and agent runs into spans
            self._provider.add_span_processor(OpenInferenceSpanProcessor())
            
            # Standard processor to export spans to the collector
            self._provider.add_span_processor(SimpleSpanProcessor(exporter))

            trace.set_tracer_provider(self._provider)
            logger.info(f"✅ Phoenix observability initialized at {self.config.endpoint}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Phoenix provider: {e}")

def setup_observability() -> None:
    """Bootstrap observability service."""
    PhoenixProvider().initialize()