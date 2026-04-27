import { Accordion, AccordionDetails, AccordionSummary, Box, Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { useQueries, useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { TestObjectVersion, TestRun, VerificationTest } from "../api/types";
import { StatusChip } from "../components/StatusChip";

export function SystemExpandPage() {
  const { t } = useTranslation();
  const versionsQ = useQuery({
    queryKey: ["versions"],
    queryFn: () => apiFetch<TestObjectVersion[]>("/test-object-versions"),
  });
  const testsQ = useQuery({
    queryKey: ["tests", "for-system-expand"],
    queryFn: () => apiFetch<VerificationTest[]>("/tests?limit=500"),
  });

  const runsQueries = useQueries({
    queries: (versionsQ.data ?? []).map((v) => ({
      queryKey: ["runs", v.id],
      queryFn: () => apiFetch<TestRun[]>(`/test-object-versions/${v.id}/runs`),
      enabled: !!versionsQ.data,
    })),
  });

  const testById = useMemo(() => {
    const map = new Map<number, VerificationTest>();
    for (const te of testsQ.data ?? []) map.set(te.id, te);
    return map;
  }, [testsQ.data]);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {t("systems.expandTitle")}
      </Typography>
      {versionsQ.isLoading && <Typography>{t("common.loading")}</Typography>}
      {(versionsQ.data ?? []).map((version, index) => {
        const runs = runsQueries[index]?.data ?? [];
        return (
          <Accordion key={version.id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>{`${version.key} - ${version.name} (${runs.length})`}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t("tests.title")}</TableCell>
                    <TableCell>{t("tests.status")}</TableCell>
                    <TableCell>{t("testReport.information")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {runs.map((run) => {
                    const te = testById.get(run.verification_test_id);
                    return (
                      <TableRow key={run.id}>
                        <TableCell>
                          {te ? (
                            <Typography
                              component={Link}
                              to={`/tests/${te.id}`}
                              sx={{
                                textDecoration: "none",
                                color: "primary.main",
                                "&:hover": { textDecoration: "underline" },
                              }}
                            >
                              {`${te.key} - ${te.title}`}
                            </Typography>
                          ) : (
                            `#${run.verification_test_id}`
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography
                            component={Link}
                            to={`/test-report?versionId=${version.id}&testId=${run.verification_test_id}`}
                            sx={{
                              textDecoration: "none",
                              color: "inherit",
                              display: "inline-flex",
                              alignItems: "center",
                              "&:hover": { opacity: 0.85 },
                            }}
                          >
                            <StatusChip value={run.status} kind="test" />
                          </Typography>
                        </TableCell>
                        <TableCell>{run.information || "—"}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </AccordionDetails>
          </Accordion>
        );
      })}
    </Box>
  );
}
