import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { useAuth } from "./context/AuthContext";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { NewRequirementPage } from "./pages/NewRequirementPage";
import { RequirementDetailPage } from "./pages/RequirementDetailPage";
import { RequirementsListPage } from "./pages/RequirementsListPage";
import { RequirementsOverviewPage } from "./pages/RequirementsOverviewPage";
import { RequirementRelationsPage } from "./pages/RequirementRelationsPage";
import { SystemAddPage } from "./pages/SystemAddPage";
import { SystemExpandPage } from "./pages/SystemExpandPage";
import { SystemListPage } from "./pages/SystemListPage";
import { TestDetailPage } from "./pages/TestDetailPage";
import { TestReportPage } from "./pages/TestReportPage";
import { TestReportTrendsPage } from "./pages/TestReportTrendsPage";
import { TestsListPage } from "./pages/TestsListPage";
import { TestsNewPage } from "./pages/TestsNewPage";
import { VersionsPage } from "./pages/VersionsPage";

function PrivateRoute() {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export default function App() {
  const { token } = useAuth();
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<PrivateRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/requirements" element={<RequirementsListPage />} />
          <Route path="/requirements/new" element={<NewRequirementPage />} />
          <Route path="/requirements/overview" element={<RequirementsOverviewPage />} />
          <Route path="/requirements/relations" element={<RequirementRelationsPage />} />
          <Route path="/requirements/:id" element={<RequirementDetailPage />} />
          <Route path="/tests/new" element={<TestsNewPage />} />
          <Route path="/tests/:id" element={<TestDetailPage />} />
          <Route path="/test-report" element={<TestReportPage />} />
          <Route path="/test-report/trends" element={<TestReportTrendsPage />} />
          <Route path="/tests" element={<TestsListPage />} />
          <Route path="/systems/new" element={<SystemAddPage />} />
          <Route path="/systems" element={<SystemListPage />} />
          <Route path="/systems/expand" element={<SystemExpandPage />} />
          <Route path="/versions" element={<VersionsPage />} />
        </Route>
        <Route path="/" element={<Navigate to={token ? "/dashboard" : "/login"} replace />} />
      </Route>
    </Routes>
  );
}
