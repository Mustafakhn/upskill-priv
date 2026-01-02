"""
Utility to generate VAPID public key from private key
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import base64


def get_public_key_from_private(private_key_pem: str) -> str:
    """Extract public key from VAPID private key"""
    try:
        # Load private key (try PEM first)
        private_key = None
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
        except Exception as e:
            # If PEM loading fails, try to handle as raw base64url
            try:
                # Convert base64url to standard base64
                key_standard = private_key_pem.replace('-', '+').replace('_', '/')
                padding = len(key_standard) % 4
                if padding:
                    key_standard += '=' * (4 - padding)
                
                # Decode and try to create EC key
                key_bytes = base64.b64decode(key_standard)
                if len(key_bytes) == 32:
                    # This is a raw private key for P-256 curve
                    from cryptography.hazmat.primitives.asymmetric import ec
                    private_key = ec.derive_private_key(
                        int.from_bytes(key_bytes, 'big'),
                        ec.SECP256R1(),
                        default_backend()
                    )
                else:
                    # Try loading as DER
                    private_key = serialization.load_der_private_key(
                        key_bytes,
                        password=None,
                        backend=default_backend()
                    )
            except Exception as e2:
                raise ValueError(f"Could not parse private key: {e}, {e2}")
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize public key in uncompressed format
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        
        # Convert to base64url (URL-safe base64 without padding)
        public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
        
        return public_key_b64
    except Exception as e:
        print(f"Error generating public key: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_vapid_private_key(key: str) -> str:
    """Format VAPID private key as PEM if needed"""
    if not key:
        return key
    
    # If already in PEM format, return as is
    if key.startswith('-----BEGIN'):
        return key
    
    # VAPID keys are typically provided as base64url (URL-safe base64)
    # Convert base64url to standard base64 first
    try:
        # Replace URL-safe characters with standard base64 characters
        # Add padding if needed
        key_standard = key.replace('-', '+').replace('_', '/')
        padding = len(key_standard) % 4
        if padding:
            key_standard += '=' * (4 - padding)
        
        # Decode base64 to get raw bytes
        decoded = base64.b64decode(key_standard)
        
        # Try to load as DER and convert to PEM
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        
        try:
            private_key = serialization.load_der_private_key(
                decoded,
                password=None,
                backend=default_backend()
            )
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            return pem.decode('utf-8')
        except Exception as e:
            # If DER loading fails, the key might be in a different format
            # Try to generate EC key from raw bytes
            try:
                from cryptography.hazmat.primitives.asymmetric import ec
                # For VAPID, we need to create an EC private key
                # The key should be 32 bytes for P-256 curve
                if len(decoded) == 32:
                    numbers = ec.derive_private_key(
                        int.from_bytes(decoded, 'big'),
                        ec.SECP256R1(),
                        default_backend()
                    )
                    pem = numbers.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                    return pem.decode('utf-8')
                else:
                    raise ValueError(f"Invalid key length: {len(decoded)} bytes, expected 32")
            except Exception as e2:
                print(f"Warning: Could not format VAPID key as PEM: {e2}")
                # Return the original key - pywebpush might accept it
                return key
    except Exception as e:
        # If all else fails, return as is (pywebpush might accept raw base64url)
        print(f"Warning: Could not format VAPID key, using as-is: {e}")
        return key
