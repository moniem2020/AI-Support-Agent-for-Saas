"""
Injection Defense - Detect and prevent prompt injection attacks.
Pattern-based detection with configurable thresholds.
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class InjectionAlert:
    """An injection attempt detection."""
    pattern_name: str
    matched_text: str
    severity: str  # low, medium, high, critical
    score: float


class InjectionDefense:
    """
    Detect and prevent prompt injection attacks.
    Uses pattern matching and heuristics to identify malicious inputs.
    """
    
    # Injection patterns with severity and score
    PATTERNS = {
        # Instruction override attempts
        "ignore_instructions": {
            "pattern": r"(?:ignore|forget|disregard|override)\s+(?:all|previous|above|your)\s+(?:instructions?|rules?|guidelines?)",
            "severity": "critical",
            "score": 0.9
        },
        "new_instructions": {
            "pattern": r"(?:new|updated?|real|actual)\s+(?:instructions?|rules?|guidelines?)\s*[:=]",
            "severity": "critical",
            "score": 0.85
        },
        "role_play": {
            "pattern": r"(?:you\s+are|act\s+as|pretend\s+to\s+be|roleplay\s+as)\s+(?:a|an|the)\s+(?:different|new|evil|malicious)",
            "severity": "high",
            "score": 0.8
        },
        
        # System prompt extraction
        "prompt_extraction": {
            "pattern": r"(?:show|reveal|display|print|output)\s+(?:your|the|system)\s+(?:prompt|instructions?|rules?)",
            "severity": "high",
            "score": 0.8
        },
        "repeat_instructions": {
            "pattern": r"repeat\s+(?:your|the|all)\s+(?:above|previous)?\s*(?:instructions?|prompt|text)",
            "severity": "high",
            "score": 0.75
        },
        
        # Jailbreak attempts
        "jailbreak_dan": {
            "pattern": r"\b(?:dan|jailbreak|do\s+anything\s+now)\b",
            "severity": "high",
            "score": 0.7
        },
        "developer_mode": {
            "pattern": r"(?:developer|debug|admin|root)\s+mode\s*(?:enabled?|on|activate)",
            "severity": "high",
            "score": 0.75
        },
        
        # Code/command injection
        "code_execution": {
            "pattern": r"(?:exec|eval|run|execute)\s*\(|`[^`]+`|os\.system|subprocess",
            "severity": "critical",
            "score": 0.9
        },
        "sql_injection": {
            "pattern": r"(?:union\s+select|drop\s+table|delete\s+from|insert\s+into|;\s*--)",
            "severity": "critical",
            "score": 0.85
        },
        
        # Boundary manipulation
        "end_marker": {
            "pattern": r"(?:</?(?:system|user|assistant)>|```\s*(?:end|exit|quit))",
            "severity": "medium",
            "score": 0.6
        },
        "output_format": {
            "pattern": r"(?:respond|reply|answer)\s+(?:only\s+)?(?:with|using)\s*[\"']?(?:yes|no|true|false)",
            "severity": "low",
            "score": 0.4
        }
    }
    
    def __init__(self, block_threshold: float = 0.7):
        """
        Initialize injection defense.
        
        Args:
            block_threshold: Score threshold above which to block the request
        """
        self.block_threshold = block_threshold
        self._compiled_patterns = {
            name: re.compile(info["pattern"], re.IGNORECASE | re.MULTILINE)
            for name, info in self.PATTERNS.items()
        }
    
    def analyze(self, text: str) -> Tuple[float, List[InjectionAlert]]:
        """
        Analyze text for injection attempts.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (suspicious_score, list of alerts)
        """
        alerts = []
        max_score = 0.0
        
        for name, pattern in self._compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                info = self.PATTERNS[name]
                for match in matches:
                    matched_text = match if isinstance(match, str) else match[0]
                    alerts.append(InjectionAlert(
                        pattern_name=name,
                        matched_text=matched_text[:100],  # Truncate long matches
                        severity=info["severity"],
                        score=info["score"]
                    ))
                    max_score = max(max_score, info["score"])
        
        # Apply heuristics
        heuristic_score = self._apply_heuristics(text)
        final_score = max(max_score, heuristic_score)
        
        return final_score, alerts
    
    def _apply_heuristics(self, text: str) -> float:
        """Apply additional heuristics for detection."""
        score = 0.0
        
        # Excessive special characters
        special_ratio = len(re.findall(r'[<>\[\]{}|\\^~`]', text)) / max(len(text), 1)
        if special_ratio > 0.1:
            score = max(score, 0.4)
        
        # Very long input (potential prompt stuffing)
        if len(text) > 5000:
            score = max(score, 0.3)
        
        # Multiple "assistant:" or "system:" markers
        role_markers = len(re.findall(r'\b(?:assistant|system|user)\s*:', text, re.IGNORECASE))
        if role_markers > 2:
            score = max(score, 0.5)
        
        # Nested quotes suggesting prompt manipulation
        nested_quotes = len(re.findall(r'["\'][^"\']*["\'][^"\']*["\']', text))
        if nested_quotes > 3:
            score = max(score, 0.4)
        
        return score
    
    def is_safe(self, text: str) -> bool:
        """Check if text is safe (below block threshold)."""
        score, _ = self.analyze(text)
        return score < self.block_threshold
    
    def sanitize(self, text: str) -> str:
        """
        Sanitize text by removing potentially dangerous patterns.
        Use with caution - may alter legitimate content.
        """
        result = text
        
        # Remove common injection markers
        result = re.sub(r'</?(?:system|user|assistant)>', '', result, flags=re.IGNORECASE)
        result = re.sub(r'```\s*(?:end|exit|quit)\s*```', '', result, flags=re.IGNORECASE)
        
        # Escape special characters that could be used for injection
        result = result.replace('\\n', ' ').replace('\\r', ' ')
        
        return result.strip()
    
    def get_risk_assessment(self, text: str) -> Dict:
        """Get detailed risk assessment of text."""
        score, alerts = self.analyze(text)
        
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in alerts:
            severity_counts[alert.severity] += 1
        
        risk_level = "safe"
        if score >= 0.8:
            risk_level = "critical"
        elif score >= 0.6:
            risk_level = "high"
        elif score >= 0.4:
            risk_level = "medium"
        elif score >= 0.2:
            risk_level = "low"
        
        return {
            "score": score,
            "risk_level": risk_level,
            "should_block": score >= self.block_threshold,
            "alert_count": len(alerts),
            "severity_breakdown": severity_counts,
            "alerts": [
                {"pattern": a.pattern_name, "severity": a.severity, "matched": a.matched_text}
                for a in alerts
            ]
        }


# Singleton instance
injection_defense = InjectionDefense()
