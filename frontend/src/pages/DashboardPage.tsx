import { Box, Card, CardContent, Typography } from "@mui/material";
import { alpha, useTheme } from "@mui/material/styles";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { DashboardSummary } from "../api/types";

export function DashboardPage() {
  const { t } = useTranslation();
  const theme = useTheme();
  const q = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardSummary>("/dashboard/summary"),
  });
  if (q.isLoading) return <Typography>{t("common.loading")}</Typography>;
  if (q.isError) return <Typography color="error">{q.error instanceof Error ? q.error.message : t("common.error")}</Typography>;
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
  const tileBg =
    theme.palette.mode === "dark"
      ? alpha(theme.palette.background.paper, 0.38)
      : alpha(theme.palette.background.paper, 0.52);

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        {t("dashboard.title")}
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", sm: "repeat(2, 1fr)", md: "repeat(4, 1fr)" },
          gap: { xs: 2, sm: 2.5, md: 3 },
          /* Slightly inset grid so more background shows at the edges of the content area */
          mx: { xs: 0, md: -0.5 },
        }}
      >
        {items.map((it) => (
          <Card
            key={it.label}
            elevation={0}
            sx={{
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 2,
              bgcolor: tileBg,
              backdropFilter: "blur(12px) saturate(1.1)",
              WebkitBackdropFilter: "blur(12px) saturate(1.1)",
              boxShadow: "none",
              overflow: "hidden",
            }}
          >
            <CardContent sx={{ py: 2.5, "&:last-child": { pb: 2.5 } }}>
              <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 500 }}>
                {it.label}
              </Typography>
              <Typography variant="h4" component="p" sx={{ mt: 0.5, mb: 0, fontWeight: 600 }}>
                {it.value}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
}
