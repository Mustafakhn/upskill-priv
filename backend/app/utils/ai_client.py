import requests
import json
import re
from typing import Dict, Any, Optional
from app.config import settings

# Import requests exceptions for error handling
from requests.exceptions import Timeout, ConnectionError, ReadTimeout


class AIClient:
    """Client for interacting with the LLM endpoint"""
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or settings.AI_ENDPOINT
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        extract_json: bool = False
    ) -> str:
        """
        Generate text using the LLM endpoint
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            extract_json: If True, attempts to extract JSON from response
            
        Returns:
            Generated text or extracted JSON string
        """
        try:
            # Merge system prompt into main prompt since endpoint doesn't accept system_prompt separately
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                "prompt": full_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=120,  # Increased timeout to 120 seconds for complex queries
                headers={"Content-Type": "application/json"},
                stream=True  # Enable streaming to handle chunked responses
            )
            response.raise_for_status()
            
            # Read streaming response line by line
            result_parts = []
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    result_parts.append(line)
            
            result = '\n'.join(result_parts).strip()
            
            # Handle streaming JSON format: {"thinking": "..."} or {"response": "..."}
            result = self._parse_streaming_json(result)
            
            if extract_json:
                result = self._extract_json(result)
            
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI request failed: {str(e)}")
    
    def _parse_streaming_json(self, text: str) -> str:
        """
        Parse streaming JSON response format
        Expected format: multiple JSON objects per line like:
        {"response": "text"}
        {"thinking": "text"}
        
        Returns concatenated response text
        """
        if not text:
            return ""
        
        response_parts = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Try to parse each line as JSON
                obj = json.loads(line)
                
                # Extract response field if present
                if "response" in obj:
                    response_parts.append(str(obj["response"]))
                # Ignore "thinking" tokens for now, only use "response"
                # If both are missing, try to use the whole object as string
                elif "thinking" not in obj:
                    # If it's not a known format, try to extract any string value
                    for key, value in obj.items():
                        if isinstance(value, str):
                            response_parts.append(value)
                            break
            except json.JSONDecodeError:
                # If JSON parsing fails, it might be plain text
                # Try to extract text between JSON objects
                continue
        
        # If we found JSON objects, join the parts
        if response_parts:
            result = "".join(response_parts)
        else:
            # If no JSON was found, return original text (fallback)
            result = text
        
        # Clean up weird tokens that might appear in the response
        # Remove patterns like @assistant, <|channel|>, <|message|>, etc.
        result = re.sub(r'@\w+\s*', '', result)  # Remove @assistant, @user, etc.
        result = re.sub(r'<\|[^|]+\|>', '', result)  # Remove <|channel|>, <|message|>, etc.
        result = re.sub(r'analysis\s*', '', result, flags=re.IGNORECASE)  # Remove "analysis" keyword
        result = re.sub(r'\s+', ' ', result)  # Normalize whitespace
        result = result.strip()
        
        return result
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON object or array in the response
        json_match = re.search(r'\{.*\}|\[.*\]', text, re.DOTALL)
        if json_match:
            try:
                # Validate it's valid JSON
                json.loads(json_match.group())
                return json_match.group()
            except json.JSONDecodeError:
                pass
        
        # If no JSON found, return original text
        return text
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_retries: int = 1
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON response with retry logic for timeouts
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_retries: Maximum number of retries for timeout errors (default: 1)
        
        Returns:
            Parsed JSON as dictionary
        """
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                response = self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    extract_json=True
                )
                
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    raise Exception(f"Failed to parse JSON from AI response: {response}")
            except Exception as e:
                error_msg = str(e)
                # Check if it's a timeout or connection error
                is_timeout = any(keyword in error_msg.lower() for keyword in ['timeout', 'timed out', 'read timeout'])
                is_connection = 'connection' in error_msg.lower()
                
                if (is_timeout or is_connection) and attempt < max_retries:
                    last_exception = e
                    print(f"AI request timeout/error (attempt {attempt + 1}/{max_retries + 1}), retrying...")
                    import time
                    time.sleep(2)  # Brief delay before retry
                else:
                    # For non-retryable errors or max retries exceeded, raise immediately
                    raise
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise Exception("Failed to generate JSON response")


ai_client = AIClient()

