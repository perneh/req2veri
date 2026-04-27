import { Box, MenuItem, Paper, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { Requirement, SubRequirement, VerificationTest } from "../api/types";
import { StatusChip } from "../components/StatusChip";

type TraceabilityPayload = {
  requirement: Requirement;
  tests_on_requirement: VerificationTest[];
  sub_requirements: { sub_requirement: SubRequirement; tests: VerificationTest[] }[];
};

function uniqTests(items: VerificationTest[]): VerificationTest[] {
  const seen = new Set<number>();
  const out: VerificationTest[] = [];
  for (const t of items) {
    if (seen.has(t.id)) continue;
    seen.add(t.id);
    out.push(t);
  }
  return out;
}

export function RequirementRelationsPage() {
  const { t } = useTranslation();
  const [selectedRequirementId, setSelectedRequirementId] = useState<number | "">("");

  const reqQ = useQuery({
    queryKey: ["requirements", "relations-page"],
    queryFn: () => apiFetch<Requirement[]>("/requirements?limit=500"),
  });

  const traceQ = useQuery({
    queryKey: ["traceability", selectedRequirementId],
    queryFn: () => apiFetch<TraceabilityPayload>(`/requirements/${selectedRequirementId}/traceability`),
    enabled: Number.isFinite(selectedRequirementId),
  });

  const allRelatedTests = useMemo(() => {
    if (!traceQ.data) return [];
    const fromSubs = traceQ.data.sub_requirements.flatMap((x) => x.tests);
    return uniqTests([...traceQ.data.tests_on_requirement, ...fromSubs]);
  }, [traceQ.data]);

  return (
    <Box>
      <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ md: "center" }} sx={{ mb: 2 }} spacing={2}>
        <Typography variant="h5">{t("relations.title")}</Typography>
        <TextField
          select
          size="small"
          label={t("relations.requirementPick")}
          value={selectedRequirementId}
          onChange={(e) => setSelectedRequirementId(e.target.value === "" ? "" : Number(e.target.value))}
          sx={{ minWidth: 320 }}
        >
          <MenuItem value="">{t("relations.requirementPickAny")}</MenuItem>
          {(reqQ.data ?? []).map((r) => (
            <MenuItem key={r.id} value={r.id}>
              {r.key} - {r.title}
            </MenuItem>
          ))}
        </TextField>
      </Stack>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {t("relations.lead")}
      </Typography>

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1fr 1fr 1fr" }, gap: 2 }}>
        <Paper sx={{ p: 1.5 }}>
          <Typography variant="subtitle1" sx={{ mb: 1 }}>
            {t("relations.colRequirement")}
          </Typography>
          {reqQ.isLoading && <Typography>{t("common.loading")}</Typography>}
          {reqQ.isError && <Typography color="error">{t("common.error")}</Typography>}
          {reqQ.data && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t("requirements.key")}</TableCell>
                  <TableCell>{t("requirements.reqTitle")}</TableCell>
                  <TableCell>{t("requirements.status")}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reqQ.data.map((r) => (
                  <TableRow
                    key={r.id}
                    hover
                    selected={selectedRequirementId === r.id}
                    onClick={() => setSelectedRequirementId(r.id)}
                    sx={{ cursor: "pointer" }}
                  >
                    <TableCell>{r.key}</TableCell>
                    <TableCell>{r.title}</TableCell>
                    <TableCell>
                      <StatusChip value={r.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Paper>

        <Paper sx={{ p: 1.5 }}>
          <Typography variant="subtitle1" sx={{ mb: 1 }}>
            {t("relations.colRelatedRequirements")}
          </Typography>
          {!Number.isFinite(selectedRequirementId) && <Typography color="text.secondary">{t("relations.selectRequirementHint")}</Typography>}
          {traceQ.isLoading && Number.isFinite(selectedRequirementId) && <Typography>{t("common.loading")}</Typography>}
          {traceQ.data && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t("requirements.key")}</TableCell>
                  <TableCell>{t("requirements.reqTitle")}</TableCell>
                  <TableCell>{t("requirements.status")}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {traceQ.data.sub_requirements.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={3} sx={{ color: "text.secondary" }}>
                      {t("overview.noSubs")}
                    </TableCell>
                  </TableRow>
                )}
                {traceQ.data.sub_requirements.map((x) => (
                  <TableRow key={x.sub_requirement.id}>
                    <TableCell>{x.sub_requirement.key}</TableCell>
                    <TableCell>{x.sub_requirement.title}</TableCell>
                    <TableCell>
                      <StatusChip value={x.sub_requirement.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Paper>

        <Paper sx={{ p: 1.5 }}>
          <Typography variant="subtitle1" sx={{ mb: 1 }}>
            {t("relations.colRelatedTests")}
          </Typography>
          {!Number.isFinite(selectedRequirementId) && <Typography color="text.secondary">{t("relations.selectRequirementHint")}</Typography>}
          {traceQ.isLoading && Number.isFinite(selectedRequirementId) && <Typography>{t("common.loading")}</Typography>}
          {traceQ.data && (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t("requirements.key")}</TableCell>
                  <TableCell>{t("requirements.reqTitle")}</TableCell>
                  <TableCell>{t("tests.status")}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {allRelatedTests.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={3} sx={{ color: "text.secondary" }}>
                      {t("tests.emptyOnDetail")}
                    </TableCell>
                  </TableRow>
                )}
                {allRelatedTests.map((te) => (
                  <TableRow key={te.id}>
                    <TableCell>{te.key}</TableCell>
                    <TableCell>
                      <Typography
                        component={Link}
                        to={`/tests/${te.id}`}
                        sx={{ textDecoration: "none", color: "primary.main", "&:hover": { textDecoration: "underline" } }}
                      >
                        {te.title}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <StatusChip value={te.status} kind="test" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Paper>
      </Box>
    </Box>
  );
}
