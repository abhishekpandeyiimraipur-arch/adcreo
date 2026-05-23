"""
backend/app/gateway/__init__.py
Thin public interface for the gateway package.
All logic lives in router.py, config.py, health.py.
Workers import from here — interface unchanged.
"""
from app.gateway.router import (
    GatewayResponse,
    ModelGateway,
    StubGateway,
    get_gateway,
)

__all__ = [
    "GatewayResponse",
    "ModelGateway",
    "StubGateway",
    "get_gateway",
]
