import { Alert, Box, Button, MenuItem, Paper, Stack, TextField, Typography } from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { Requirement, SubRequirement, VerificationTest } from "../api/types";
import { StatusChip } from "../components/StatusChip";

export function TestDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const testId = Number(id);
  const qc = useQueryClient();
  const [linkMode, setLinkMode] = useState<"none" | "requirement" | "sub">("none");
  const [selectedRequirementId, setSelectedRequirementId] = useState<number | "">("");
  const [selectedSubRequirementId, setSelectedSubRequirementId] = useState<number | "">("");
  const [linkMsg, setLinkMsg] = useState<string | null>(null);

  const q = useQuery({
    queryKey: ["test", testId],
    queryFn: () => apiFetch<VerificationTest>(`/tests/${testId}`),
    enabled: Number.isFinite(testId),
  });

  if (!Number.isFinite(testId)) return null;
  if (q.isLoading) return <Typography>{t("common.loading")}</Typography>;
  if (q.isError) return <Typography color="error">{q.error instanceof Error ? q.error.message : t("common.error")}</Typography>;
  const te = q.data!;

  const reqQ = useQuery({
    queryKey: ["requirements", "for-test-link"],
    queryFn: () => apiFetch<Requirement[]>("/requirements?limit=500"),
    enabled: Number.isFinite(testId),
  });

  const subQ = useQuery({
    queryKey: ["subrequirements", "for-test-link", selectedRequirementId],
    queryFn: () => apiFetch<SubRequirement[]>(`/requirements/${selectedRequirementId}/subrequirements`),
    enabled: Number.isFinite(selectedRequirementId),
  });

  useEffect(() => {
    if (te.sub_requirement_id != null) setLinkMode("sub");
    else if (te.requirement_id != null) setLinkMode("requirement");
    else setLinkMode("none");
    setSelectedRequirementId(te.requirement_id ?? "");
    setSelectedSubRequirementId(te.sub_requirement_id ?? "");
  }, [te.requirement_id, te.sub_requirement_id]);

  const linkMutation = useMutation({
    mutationFn: async () => {
      let requirementId: number | null = null;
      let subRequirementId: number | null = null;
      if (linkMode === "requirement") {
        if (!Number.isFinite(selectedRequirementId)) throw new Error(t("tests.linkSelectRequirement"));
        requirementId = Number(selectedRequirementId);
      } else if (linkMode === "sub") {
        if (!Number.isFinite(selectedRequirementId)) throw new Error(t("tests.linkSelectRequirement"));
        if (!Number.isFinite(selectedSubRequirementId)) throw new Error(t("tests.linkSelectSubRequirement"));
        subRequirementId = Number(selectedSubRequirementId);
      }
      return apiFetch<VerificationTest>(`/tests/${testId}`, {
        method: "PATCH",
        json: {
          requirement_id: requirementId,
          sub_requirement_id: subRequirementId,
        },
      });
    },
    onSuccess: async () => {
      setLinkMsg(t("tests.linkUpdated"));
      await qc.invalidateQueries({ queryKey: ["test", testId] });
      await qc.invalidateQueries({ queryKey: ["tests"] });
      await qc.invalidateQueries({ queryKey: ["requirements"] });
    },
    onError: (e: Error) => setLinkMsg(e.message),
  });

  const unlinkMutation = useMutation({
    mutationFn: () =>
      apiFetch<VerificationTest>(`/tests/${testId}`, {
        method: "PATCH",
        json: {
          requirement_id: null,
          sub_requirement_id: null,
        },
      }),
    onSuccess: async () => {
      setLinkMode("none");
      setSelectedRequirementId("");
      setSelectedSubRequirementId("");
      setLinkMsg(t("tests.linkRemoved"));
      await qc.invalidateQueries({ queryKey: ["test", testId] });
      await qc.invalidateQueries({ queryKey: ["tests"] });
      await qc.invalidateQueries({ queryKey: ["requirements"] });
    },
    onError: (e: Error) => setLinkMsg(e.message),
  });

  const linkedTo =
    te.requirement_id != null
      ? `REQ #${te.requirement_id}`
      : te.sub_requirement_id != null
        ? `SUB #${te.sub_requirement_id}`
        : t("tests.unlinkedLabel");

  return (
    <Box maxWidth={900}>
      <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" alignItems={{ sm: "center" }} sx={{ mb: 2 }}>
        <Typography variant="h5">
          {te.key} — {te.title}
        </Typography>
        <Button component={Link} to="/tests">
          {t("tests.backToList")}
        </Button>
      </Stack>

      <Paper sx={{ p: 2 }}>
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            <strong>{t("tests.status")}:</strong> <StatusChip value={te.status} kind="test" />{" "}
            · <strong>{t("tests.method")}:</strong> {t(`method.${te.method}` as never)} ·{" "}
            <strong>{t("tests.linked")}:</strong> {linkedTo}
          </Typography>

          <Box>
            <Typography variant="subtitle2">{t("requirements.description")}</Typography>
            <Typography sx={{ whiteSpace: "pre-wrap" }}>{te.description || t("tests.unlinkedLabel")}</Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2">{t("tests.precondition")}</Typography>
            <Typography sx={{ whiteSpace: "pre-wrap" }}>{te.precondition || t("tests.unlinkedLabel")}</Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2">{t("tests.action")}</Typography>
            <Typography sx={{ whiteSpace: "pre-wrap" }}>{te.action || t("tests.unlinkedLabel")}</Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2">{t("tests.expected")}</Typography>
            <Typography sx={{ whiteSpace: "pre-wrap" }}>{te.expected_result || t("tests.unlinkedLabel")}</Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2">{t("tests.actual")}</Typography>
            <Typography sx={{ whiteSpace: "pre-wrap" }}>{te.actual_result || t("tests.unlinkedLabel")}</Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              {t("tests.linkEditorTitle")}
            </Typography>
            <Stack spacing={1.5}>
              <TextField
                select
                size="small"
                label={t("tests.linkModeLabel")}
                value={linkMode}
                onChange={(e) => {
                  const next = e.target.value as "none" | "requirement" | "sub";
                  setLinkMode(next);
                  if (next !== "sub") setSelectedSubRequirementId("");
                }}
              >
                <MenuItem value="none">{t("tests.linkModeNone")}</MenuItem>
                <MenuItem value="requirement">{t("tests.linkModeRequirement")}</MenuItem>
                <MenuItem value="sub">{t("tests.linkModeSub")}</MenuItem>
              </TextField>

              {linkMode !== "none" && (
                <TextField
                  select
                  size="small"
                  label={t("tests.linkRequirementLabel")}
                  value={selectedRequirementId}
                  onChange={(e) => setSelectedRequirementId(e.target.value === "" ? "" : Number(e.target.value))}
                >
                  <MenuItem value="">{t("tests.linkSelectRequirement")}</MenuItem>
                  {(reqQ.data ?? []).map((r) => (
                    <MenuItem key={r.id} value={r.id}>
                      {r.key} - {r.title}
                    </MenuItem>
                  ))}
                </TextField>
              )}

              {linkMode === "sub" && (
                <TextField
                  select
                  size="small"
                  label={t("tests.linkSubRequirementLabel")}
                  value={selectedSubRequirementId}
                  onChange={(e) => setSelectedSubRequirementId(e.target.value === "" ? "" : Number(e.target.value))}
                >
                  <MenuItem value="">{t("tests.linkSelectSubRequirement")}</MenuItem>
                  {(subQ.data ?? []).map((s) => (
                    <MenuItem key={s.id} value={s.id}>
                      {s.key} - {s.title}
                    </MenuItem>
                  ))}
                </TextField>
              )}

              <Box>
                <Stack direction="row" spacing={1}>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => linkMutation.mutate()}
                    disabled={linkMutation.isPending || unlinkMutation.isPending}
                  >
                    {t("tests.linkSave")}
                  </Button>
                  {(te.requirement_id != null || te.sub_requirement_id != null) && (
                    <Button
                      size="small"
                      variant="outlined"
                      color="warning"
                      onClick={() => unlinkMutation.mutate()}
                      disabled={linkMutation.isPending || unlinkMutation.isPending}
                    >
                      {t("tests.linkRemove")}
                    </Button>
                  )}
                </Stack>
              </Box>
              {linkMsg && <Alert severity={linkMutation.isError || unlinkMutation.isError ? "error" : "success"}>{linkMsg}</Alert>}
            </Stack>
          </Box>
        </Stack>
      </Paper>
    </Box>
  );
}
