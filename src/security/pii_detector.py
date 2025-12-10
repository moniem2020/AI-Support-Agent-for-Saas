"""
PII Detector - Detect and anonymize personally identifiable information.
Uses regex patterns for common PII types with reversible tokenization.
"""
import re
import uuid
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class PIIMatch:
    """A detected PII match."""
    pii_type: str
    value: str
    start: int
    end: int
    token: str = ""


class PIIDetector:
    """
    Detect and anonymize PII in text.
    Supports emails, phone numbers, SSNs, credit cards, and more.
    """
    
    # PII patterns
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}\b',
        "ssn": r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "date_of_birth": r'\b(?:0?[1-9]|1[0-2])[/\-](?:0?[1-9]|[12]\d|3[01])[/\-](?:19|20)\d{2}\b',
    }
    
    def __init__(self):
        self._token_map: Dict[str, str] = {}  # token -> original value
        self._reverse_map: Dict[str, str] = {}  # original value -> token
        self._compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }
    
    def detect_pii(self, text: str) -> List[PIIMatch]:
        """
        Detect all PII in text.
        
        Args:
            text: Input text to scan
            
        Returns:
            List of PIIMatch objects
        """
        matches = []
        
        for pii_type, pattern in self._compiled_patterns.items():
            for match in pattern.finditer(text):
                matches.append(PIIMatch(
                    pii_type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end()
                ))
        
        # Sort by position
        matches.sort(key=lambda m: m.start)
        return matches
    
    def anonymize(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize PII in text with reversible tokens.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (anonymized_text, token_map)
        """
        matches = self.detect_pii(text)
        
        if not matches:
            return text, {}
        
        # Process in reverse order to preserve positions
        result = text
        token_map = {}
        
        for match in reversed(matches):
            # Check if we've seen this value before
            if match.value in self._reverse_map:
                token = self._reverse_map[match.value]
            else:
                # Generate new token
                token = f"[{match.pii_type.upper()}_{uuid.uuid4().hex[:8]}]"
                self._token_map[token] = match.value
                self._reverse_map[match.value] = token
            
            token_map[token] = match.value
            result = result[:match.start] + token + result[match.end:]
        
        return result, token_map
    
    def deanonymize(self, text: str, token_map: Dict[str, str] = None) -> str:
        """
        Restore original values from tokens.
        
        Args:
            text: Anonymized text
            token_map: Optional token map (uses internal map if not provided)
            
        Returns:
            Original text with PII restored
        """
        combined_map = {**self._token_map, **(token_map or {})}
        result = text
        
        for token, original in combined_map.items():
            result = result.replace(token, original)
        
        return result
    
    def has_pii(self, text: str) -> bool:
        """Check if text contains any PII."""
        return len(self.detect_pii(text)) > 0
    
    def get_pii_summary(self, text: str) -> Dict[str, int]:
        """Get count of each PII type found."""
        matches = self.detect_pii(text)
        summary = {}
        for match in matches:
            summary[match.pii_type] = summary.get(match.pii_type, 0) + 1
        return summary
    
    def clear_mappings(self) -> None:
        """Clear all stored token mappings."""
        self._token_map.clear()
        self._reverse_map.clear()


# Singleton instance
pii_detector = PIIDetector()
