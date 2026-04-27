import { Box, Button, Paper, Slider, Stack, Tooltip, Typography } from "@mui/material";
import { useQueries, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { TestObjectVersion, TestRun } from "../api/types";

type StatusSummary = {
  not_run: number;
  passed: number;
  failed: number;
  blocked: number;
  total: number;
};

function summarize(runs: TestRun[]): StatusSummary {
  const summary: StatusSummary = {
    not_run: 0,
    passed: 0,
    failed: 0,
    blocked: 0,
    total: runs.length,
  };
  for (const run of runs) {
    summary[run.status] += 1;
  }
  return summary;
}

export function TestReportTrendsPage() {
  const { t } = useTranslation();
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState(0);
  const versionsQ = useQuery({
    queryKey: ["versions"],
    queryFn: () => apiFetch<TestObjectVersion[]>("/test-object-versions"),
  });

  const runsQueries = useQueries({
    queries: (versionsQ.data ?? []).map((v) => ({
      queryKey: ["runs", v.id],
      queryFn: () => apiFetch<TestRun[]>(`/test-object-versions/${v.id}/runs`),
      enabled: !!versionsQ.data,
    })),
  });

  const rows = useMemo(() => {
    const byDate = new Map<string, TestRun[]>();
    (versionsQ.data ?? []).forEach((_, index) => {
      const runs = runsQueries[index]?.data ?? [];
      for (const run of runs) {
        const d = new Date(run.ran_at);
        if (Number.isNaN(d.getTime())) continue;
        const dateKey = d.toISOString().slice(0, 10);
        if (!byDate.has(dateKey)) byDate.set(dateKey, []);
        byDate.get(dateKey)!.push(run);
      }
    });
    return Array.from(byDate.entries())
      .map(([dateKey, runs]) => ({ dateKey, summary: summarize(runs) }))
      .sort((a, b) => new Date(a.dateKey).getTime() - new Date(b.dateKey).getTime());
  }, [runsQueries, versionsQ.data]);

  const visibleCount = useMemo(() => {
    if (rows.length <= 1) return rows.length;
    const baseWindow = 10;
    const zoomedWindow = Math.max(2, Math.round(baseWindow / zoom));
    return Math.min(rows.length, zoomedWindow);
  }, [rows.length, zoom]);

  const maxOffset = Math.max(0, rows.length - visibleCount);
  const clampedOffset = Math.min(offset, maxOffset);
  const visibleRows = rows.slice(clampedOffset, clampedOffset + visibleCount);
  const maxStatusCount = Math.max(
    1,
    ...rows.flatMap((x) => [
      x.summary.passed,
      x.summary.failed,
      x.summary.blocked,
      x.summary.not_run,
    ]),
  );

  const statusLegend = useMemo(
    () =>
      [
        { key: "passed" as const, label: t("status.passed"), color: "success.main" },
        { key: "failed" as const, label: t("status.failed"), color: "error.main" },
        { key: "blocked" as const, label: t("status.blocked"), color: "warning.main" },
        { key: "not_run" as const, label: t("status.not_run"), color: "grey.500" },
      ] as const,
    [t],
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {t("testReport.trendsTitle")}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {t("testReport.trendsLead")}
      </Typography>
      <Paper sx={{ p: 1.5, mb: 2 }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ md: "center" }} sx={{ mb: 1 }}>
          <Typography variant="body2">{t("testReport.zoom")}</Typography>
          <Stack direction="row" spacing={1}>
            <Button
              size="small"
              variant="outlined"
              onClick={() => setZoom(Math.max(1, zoom - 1))}
              disabled={zoom <= 1}
            >
              {t("testReport.less")}
            </Button>
            <Button
              size="small"
              variant="outlined"
              onClick={() => setZoom(Math.min(6, zoom + 1))}
              disabled={zoom >= 6}
            >
              {t("testReport.more")}
            </Button>
          </Stack>
          <Typography variant="caption" color="text.secondary">
            {`${clampedOffset + 1}-${Math.min(rows.length, clampedOffset + visibleCount)} / ${rows.length}`}
          </Typography>
        </Stack>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ md: "center" }}>
          <Typography variant="body2">{t("testReport.timeline")}</Typography>
          <Slider
            min={0}
            max={maxOffset}
            step={1}
            value={clampedOffset}
            onChange={(_, value) => setOffset(value as number)}
            sx={{ maxWidth: 420 }}
            aria-label={t("testReport.timeline")}
            disabled={maxOffset === 0}
          />
          <Stack direction="row" spacing={1}>
            <Button size="small" variant="outlined" onClick={() => setOffset(Math.max(0, clampedOffset - 1))}>
              {t("testReport.prev")}
            </Button>
            <Button
              size="small"
              variant="outlined"
              onClick={() => setOffset(Math.min(maxOffset, clampedOffset + 1))}
            >
              {t("testReport.next")}
            </Button>
          </Stack>
        </Stack>
      </Paper>
      {versionsQ.isLoading && <Typography>{t("common.loading")}</Typography>}
      {visibleRows.length > 0 && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            {t("testReport.trendsBarsLegend")}
          </Typography>
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap sx={{ mb: 1.5, gap: 1.5 }}>
            {statusLegend.map((item) => (
              <Stack key={item.key} direction="row" spacing={0.75} alignItems="center">
                <Box sx={{ width: 12, height: 12, borderRadius: 0.5, bgcolor: item.color, flexShrink: 0 }} />
                <Typography variant="caption" color="text.secondary">
                  {item.label}
                </Typography>
              </Stack>
            ))}
          </Stack>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: `repeat(${visibleRows.length}, minmax(0, 1fr))`,
              gap: 1.25,
              alignItems: "end",
              minHeight: 320,
              border: 1,
              borderColor: "divider",
              borderRadius: 1,
              p: 1,
              bgcolor: "background.paper",
              width: "100%",
              maxWidth: "100%",
              overflow: "hidden",
            }}
          >
            {visibleRows.map(({ dateKey, summary }) => {
              const bars = [
                { key: "passed" as const, label: t("status.passed"), value: summary.passed, color: "success.main" },
                { key: "failed" as const, label: t("status.failed"), value: summary.failed, color: "error.main" },
                { key: "blocked" as const, label: t("status.blocked"), value: summary.blocked, color: "warning.main" },
                { key: "not_run" as const, label: t("status.not_run"), value: summary.not_run, color: "grey.500" },
              ] as const;
              const tooltipTitle = (
                <Box sx={{ py: 0.25 }}>
                  <Typography variant="caption" sx={{ fontWeight: 600, display: "block", mb: 0.5 }}>
                    {new Date(dateKey).toLocaleDateString()}
                  </Typography>
                  {bars.map((bar) => (
                    <Typography key={bar.key} variant="caption" sx={{ display: "block" }}>
                      {`${bar.label}: ${bar.value}`}
                    </Typography>
                  ))}
                  <Typography variant="caption" color="text.secondary" sx={{ display: "block", mt: 0.5 }}>
                    {`${t("testReport.totalRuns")}: ${summary.total}`}
                  </Typography>
                </Box>
              );
              return (
                <Tooltip key={dateKey} title={tooltipTitle} arrow placement="top">
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "stretch",
                      justifyContent: "end",
                      p: 0.75,
                      borderRadius: 1,
                      border: 1,
                      borderColor: "divider",
                      cursor: "default",
                      transition: "border-color 120ms ease",
                      "&:hover": { borderColor: "primary.main" },
                    }}
                  >
                    <Box sx={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 0.75, alignItems: "end", height: 210 }}>
                      {bars.map((bar) => (
                        <Box
                          key={bar.key}
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "end",
                            gap: 0.4,
                          }}
                        >
                          <Typography variant="caption" sx={{ fontVariantNumeric: "tabular-nums" }}>
                            {bar.value}
                          </Typography>
                          <Box
                            sx={{
                              width: 16,
                              height: `${(bar.value / maxStatusCount) * 150 + 4}px`,
                              bgcolor: bar.color,
                              borderRadius: 0.6,
                              flexShrink: 0,
                            }}
                          />
                        </Box>
                      ))}
                    </Box>
                    <Typography variant="caption" sx={{ mt: 0.6, textAlign: "center", fontWeight: 600 }}>
                      {new Date(dateKey).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Tooltip>
              );
            })}
          </Box>
        </Paper>
      )}
    </Box>
  );
}
