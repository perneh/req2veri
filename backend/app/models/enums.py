from enum import Enum


class RequirementStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    implemented = "implemented"
    verified = "verified"
    rejected = "rejected"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TestMethod(str, Enum):
    inspection = "inspection"
    analysis = "analysis"
    test = "test"
    demonstration = "demonstration"


class TestStatus(str, Enum):
    not_run = "not_run"
    passed = "passed"
    failed = "failed"
    blocked = "blocked"
