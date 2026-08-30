class SeverityEngine:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    SEVERITY_ORDER = [INFO, LOW, MEDIUM, HIGH, CRITICAL]

    @staticmethod
    def evaluate(label: str, confidence: float, is_anomaly: bool, anomaly_score: float, threshold: float) -> str:
        if not is_anomaly and label == "benign":
            return SeverityEngine.INFO

        if label == "benign" and is_anomaly:
            ratio = anomaly_score / threshold if threshold > 0 else 0
            if ratio > 3.0:
                return SeverityEngine.HIGH
            if ratio > 1.5:
                return SeverityEngine.MEDIUM
            return SeverityEngine.LOW

        attack_keywords = ["ddos", "dos", "bot", "injection", "xss", "brute", "force", "exploit", "backdoor", "malware"]
        is_known_attack = any(kw in label.lower() for kw in attack_keywords)

        if is_known_attack:
            if confidence >= 0.9:
                return SeverityEngine.CRITICAL
            if confidence >= 0.75:
                return SeverityEngine.HIGH
            if confidence >= 0.5:
                return SeverityEngine.MEDIUM
            return SeverityEngine.LOW

        if is_anomaly:
            ratio = anomaly_score / threshold if threshold > 0 else 0
            if ratio > 3.0:
                return SeverityEngine.HIGH
            if ratio > 1.5:
                return SeverityEngine.MEDIUM
            return SeverityEngine.LOW

        return SeverityEngine.INFO
