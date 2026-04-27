export type RequirementStatus =
  | "draft"
  | "approved"
  | "implemented"
  | "verified"
  | "rejected";
export type Priority = "low" | "medium" | "high" | "critical";
export type TestMethod = "inspection" | "analysis" | "test" | "demonstration";
export type TestStatus = "not_run" | "passed" | "failed" | "blocked";

export type Requirement = {
  id: number;
  key: string;
  title: string;
  description: string;
  status: RequirementStatus;
  priority: Priority;
  created_at: string;
  updated_at: string;
  updated_by: string;
  approved_by: string;
  approved_at: string | null;
};

export type SubRequirement = {
  id: number;
  key: string;
  parent_requirement_id: number;
  title: string;
  description: string;
  status: RequirementStatus;
  priority: Priority;
  created_at: string;
  updated_at: string;
  updated_by: string;
  approved_by: string;
  approved_at: string | null;
};

export type VerificationTest = {
  id: number;
  key: string;
  title: string;
  description: string;
  precondition: string;
  action: string;
  method: TestMethod;
  status: TestStatus;
  requirement_id: number | null;
  sub_requirement_id: number | null;
  expected_result: string;
  actual_result: string;
  created_at: string;
  updated_at: string;
  updated_by: string;
};

export type DashboardSummary = {
  requirements_total: number;
  subrequirements_total: number;
  tests_total: number;
  requirements_verified: number;
  tests_passed: number;
  tests_failed: number;
  tests_not_run: number;
  tests_blocked: number;
};

export type RequirementCoverage = {
  requirement_id: number;
  requirement_key: string;
  tests_total: number;
  tests_passed: number;
  subrequirements_total: number;
  subrequirements_with_test: number;
  all_subrequirements_have_test: boolean;
};

export type TestObjectVersion = {
  id: number;
  key: string;
  name: string;
  description: string;
  created_at: string;
};

export type TestRun = {
  id: number;
  verification_test_id: number;
  test_object_version_id: number;
  status: TestStatus;
  information: string;
  reported_by: string;
  ran_at: string;
};

export type TestRunUpsert = {
  status: TestStatus;
  information: string;
  ran_at?: string;
};

export type RequirementHierarchyItem = {
  requirement: Requirement;
  sub_requirements: SubRequirement[];
};
