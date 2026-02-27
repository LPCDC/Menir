"""
Menir MCP Security Middleware
Responsible on-the-fly PII redaction and access control enforcement.
"""
import re
from typing import Dict, Any, List

class PiiFilter:
    """
    Filters sensitive PII (Personally Identifiable Information) from Node properties.
    """
    
    # Sensitive keys to redact unless explicitly authorized
    SENSITIVE_KEYS = {
        "cpf", "rg", "ssn", "passport", 
        "credit_card", "cc_number", 
        "email_personal", "phone_mobile", 
        "address_home", "salary", "net_worth"
    }

    @staticmethod
    def redact_node(node_props: Dict[str, Any], allowed_fields: List[str] = None) -> Dict[str, Any]:
        """
        Returns a sanitized copy of node properties.
        """
        if not node_props:
            return {}
            
        sanitized = {}
        allowed = set(allowed_fields) if allowed_fields else set()

        for key, value in node_props.items():
            lower_key = key.lower()
            
            # If key is sensitive and NOT in allowed list -> REDACT
            if lower_key in PiiFilter.SENSITIVE_KEYS and key not in allowed:
                sanitized[key] = "[REDACTED_PII]"
            else:
                sanitized[key] = value
                
        return sanitized

    @staticmethod
    def redact_log_line(line: str) -> str:
        """
        Basic regex redaction for logs (e.g. email patterns).
        """
        # Redact Emails
        line = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REDACTED]', line)
        # Redact CPF-like patterns (XXX.XXX.XXX-XX)
        line = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF_REDACTED]', line)
        return line
