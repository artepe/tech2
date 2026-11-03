"""OEM authorization integration point - intentionally fail-closed, no unlock tricks."""
from dataclasses import dataclass

class AuthorizationRequired(PermissionError):
    pass

@dataclass(frozen=True)
class SecurityCapability:
    feature: str
    status: str = "OEM authorization/vehicle-specific implementation required"
    implemented: bool = False

PROTECTED_ACTIONS = (
    SecurityCapability("Immobilizer / avaimet"),
    SecurityCapability("Ohjainlaitteiden ohjelmointi (SPS)"),
    SecurityCapability("ECU-konfigurointi / add-remove"),
    SecurityCapability("Bi-directionaaliset laitetestit"),
    SecurityCapability("Turvapääsyn avaaminen"),
    SecurityCapability("Airbag/ABS-huoltotoiminnot"),
)

def require_verified_oem_authorization(*_, **__):
    """No default allow-path; implement a provider only with legitimate OEM authorization."""
    raise AuthorizationRequired("OEM-turvapääsy ei ole toteutettu. Ei seed-key-arvausta eikä ohitusta.")
