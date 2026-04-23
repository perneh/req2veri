import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { useAuth } from "./context/AuthContext";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { NewRequirementPage } from "./pages/NewRequirementPage";
import { RequirementDetailPage } from "./pages/RequirementDetailPage";
import { RequirementsListPage } from "./pages/RequirementsListPage";
import { RequirementsOverviewPage } from "./pages/RequirementsOverviewPage";
import { TestDetailPage } from "./pages/TestDetailPage";
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
          <Route path="/requirements/:id" element={<RequirementDetailPage />} />
          <Route path="/tests/new" element={<TestsNewPage />} />
          <Route path="/tests/:id" element={<TestDetailPage />} />
          <Route path="/tests" element={<TestsListPage />} />
          <Route path="/versions" element={<VersionsPage />} />
        </Route>
        <Route path="/" element={<Navigate to={token ? "/dashboard" : "/login"} replace />} />
      </Route>
    </Routes>
  );
}
