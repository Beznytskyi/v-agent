from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    requires_approval: bool
    reason: str


class PolicyEngine:
    """Central authorization boundary for agent actions."""

    def check(self, *, action: str, risk_level: str) -> PolicyDecision:
        if risk_level in {"R0", "R1"}:
            return PolicyDecision(True, False, "low-risk action")
        return PolicyDecision(False, True, "approval policy not yet configured")
