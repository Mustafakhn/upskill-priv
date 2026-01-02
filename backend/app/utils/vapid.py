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
        # Load private key (try PEM first, then DER)
        private_key = None
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
        except:
            # Try loading as DER (base64 decoded)
            try:
                key_bytes = base64.b64decode(private_key_pem)
                private_key = serialization.load_der_private_key(
                    key_bytes,
                    password=None,
                    backend=default_backend()
                )
            except:
                raise ValueError("Could not parse private key")
        
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
    
    # pywebpush can accept the key in different formats
    # Try to handle base64 format by converting to PEM
    try:
        # Try to decode to see if it's valid base64
        decoded = base64.b64decode(key)
        
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
        except:
            # If DER loading fails, format as PEM with proper line breaks
            # Split into 64-char lines
            formatted_key = '\n'.join([key[i:i+64] for i in range(0, len(key), 64)])
            return f"""-----BEGIN PRIVATE KEY-----
{formatted_key}
-----END PRIVATE KEY-----"""
    except Exception as e:
        # If all else fails, return as is (pywebpush might accept raw base64)
        print(f"Warning: Could not format VAPID key, using as-is: {e}")
        return key
