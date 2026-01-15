import re

class LGPDSanitizer:
    def __init__(self):
        self.counter = 1
        self.mapping = {}

    def mask_pii(self, text: str) -> str:
        """
        Naive PII masking for demo purposes.
        In production, this would use NER (Spacy/Bert).
        Replaces 2+ Capitalized words in sequence with [PESSOA_TERC_###].
        """
        # Heuristic: Match "Name Surname" pattern (Capitalized words)
        # Avoiding Start of Sentence false positives is hard without NLP.
        # This is a baseline implementation.
        
        def replace(match):
            name = match.group(0)
            if name not in self.mapping:
                label = f"[PESSOA_TERC_{self.counter:03d}]"
                self.mapping[name] = label
                self.counter += 1
            return self.mapping[name]

        # Regex for Name Surname (simplified)
        # Excludes common stopwords if needed
        pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b" 
        
        masked_text = re.sub(pattern, replace, text)
        return masked_text
