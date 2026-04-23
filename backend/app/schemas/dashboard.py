from pydantic import BaseModel


class DashboardSummary(BaseModel):
    requirements_total: int
    subrequirements_total: int
    tests_total: int
    requirements_verified: int
    tests_passed: int
    tests_failed: int
    tests_not_run: int
    tests_blocked: int
