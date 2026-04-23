import { Box, Card, CardContent, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { DashboardSummary } from "../api/types";

export function DashboardPage() {
  const { t } = useTranslation();
  const q = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardSummary>("/dashboard/summary"),
  });
  if (q.isLoading) return <Typography>{t("common.loading")}</Typography>;
  if (q.isError) return <Typography color="error">{t("common.error")}</Typography>;
  const s = q.data!;
  const items = [
    { label: t("dashboard.requirements"), value: s.requirements_total },
    { label: t("dashboard.subrequirements"), value: s.subrequirements_total },
    { label: t("dashboard.tests"), value: s.tests_total },
    { label: t("dashboard.verifiedReqs"), value: s.requirements_verified },
    { label: t("dashboard.passed"), value: s.tests_passed },
    { label: t("dashboard.failed"), value: s.tests_failed },
    { label: t("dashboard.notRun"), value: s.tests_not_run },
    { label: t("dashboard.blocked"), value: s.tests_blocked },
  ];
  return (
    <div>
      <Typography variant="h5" gutterBottom>
        {t("dashboard.title")}
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", sm: "repeat(2, 1fr)", md: "repeat(4, 1fr)" },
          gap: 2,
        }}
      >
        {items.map((it) => (
          <Card key={it.label}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">
                {it.label}
              </Typography>
              <Typography variant="h4">{it.value}</Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </div>
  );
}
