"""
Utilities for normalizing and deriving VAPID keys.
"""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64


def _normalize_key_string(key: str) -> str:
    """Normalize env-provided key strings before parsing."""
    if not key:
        return key

    normalized = key.strip()

    # Remove wrapping quotes from .env / compose values.
    if (
        len(normalized) >= 2
        and normalized[0] == normalized[-1]
        and normalized[0] in {"'", '"'}
    ):
        normalized = normalized[1:-1].strip()

    # Convert escaped newlines into real PEM newlines.
    normalized = normalized.replace("\\n", "\n").replace("\\r", "\r")

    return normalized.strip()


def normalize_vapid_key_input(key: str) -> str:
    """Public helper for normalizing env-provided key material."""
    return _normalize_key_string(key)


def _load_private_key(key: str):
    """Load a VAPID private key from PEM, raw base64url, or DER."""
    normalized = _normalize_key_string(key)

    # PEM input
    if normalized.startswith("-----BEGIN"):
        return serialization.load_pem_private_key(
            normalized.encode("utf-8"),
            password=None,
            backend=default_backend()
        )

    # Raw base64url/base64 input
    key_standard = normalized.replace("-", "+").replace("_", "/")
    padding = len(key_standard) % 4
    if padding:
        key_standard += "=" * (4 - padding)

    decoded = base64.b64decode(key_standard)

    # Raw P-256 private key bytes
    if len(decoded) == 32:
        return ec.derive_private_key(
            int.from_bytes(decoded, "big"),
            ec.SECP256R1(),
            default_backend()
        )

    # DER-encoded key
    return serialization.load_der_private_key(
        decoded,
        password=None,
        backend=default_backend()
    )


def get_public_key_from_private(private_key_value: str) -> str:
    """Extract base64url public key from a VAPID private key."""
    try:
        private_key = _load_private_key(private_key_value)
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        return base64.urlsafe_b64encode(public_key_bytes).decode("utf-8").rstrip("=")
    except Exception as e:
        print(f"Error generating public key: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_vapid_private_key(key: str) -> str:
    """Return a normalized PEM private key string for pywebpush."""
    if not key:
        return key

    try:
        private_key = _load_private_key(key)
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode("utf-8")
    except Exception as e:
        print(f"Warning: Could not format VAPID key, using normalized original value: {e}")
        import traceback
        traceback.print_exc()
        return _normalize_key_string(key)
