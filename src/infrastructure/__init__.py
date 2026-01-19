from app.app_provider import AppProvider
from infrastructure.env_config import SettingsProvider
from infrastructure.infrastructure_provider import InfrastructureProvider

dependencies_providers = [SettingsProvider(), AppProvider(), InfrastructureProvider()]


__all__ = ["dependencies_providers"]
