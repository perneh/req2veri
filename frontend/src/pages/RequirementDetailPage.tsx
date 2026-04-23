import {
  Alert,
  Box,
  Button,
  Divider,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useLocation, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useEffect, useRef, useState } from "react";

import { apiFetch } from "../api/client";
import type { Requirement, RequirementCoverage, RequirementStatus, SubRequirement, Priority, VerificationTest } from "../api/types";
import { RequirementTestsPanel } from "../components/RequirementTestsPanel";
import { StatusChip } from "../components/StatusChip";

type Trace = {
  requirement: Requirement;
  tests_on_requirement: VerificationTest[];
  sub_requirements: { sub_requirement: SubRequirement; tests: VerificationTest[] }[];
};

export function RequirementDetailPage() {
  const { id } = useParams();
  const location = useLocation();
  const { t } = useTranslation();
  const qc = useQueryClient();
  const subSectionRef = useRef<HTMLDivElement | null>(null);
  const rid = Number(id);

  const [subKey, setSubKey] = useState("");
  const [subTitle, setSubTitle] = useState("");
  const [subDescription, setSubDescription] = useState("");
  const [subStatus, setSubStatus] = useState<RequirementStatus>("draft");
  const [subPriority, setSubPriority] = useState<Priority>("medium");
  const [subErr, setSubErr] = useState<string | null>(null);
  const [subOk, setSubOk] = useState(false);

  const reqQ = useQuery({
    queryKey: ["requirement", rid],
    queryFn: () => apiFetch<Requirement>(`/requirements/${rid}`),
    enabled: Number.isFinite(rid),
  });
  const subQ = useQuery({
    queryKey: ["subrequirements", rid],
    queryFn: () => apiFetch<SubRequirement[]>(`/requirements/${rid}/subrequirements`),
    enabled: Number.isFinite(rid),
  });
  const covQ = useQuery({
    queryKey: ["coverage", rid],
    queryFn: () => apiFetch<RequirementCoverage>(`/requirements/${rid}/coverage`),
    enabled: Number.isFinite(rid),
  });
  const traceQ = useQuery({
    queryKey: ["trace", rid],
    queryFn: () => apiFetch<Trace>(`/requirements/${rid}/traceability`),
    enabled: Number.isFinite(rid),
  });

  const createSub = useMutation({
    mutationFn: () =>
      apiFetch<SubRequirement>(`/requirements/${rid}/subrequirements`, {
        method: "POST",
        json: {
          key: subKey,
          title: subTitle,
          description: subDescription,
          status: subStatus,
          priority: subPriority,
        },
      }),
    onSuccess: () => {
      setSubErr(null);
      setSubOk(true);
      setSubKey("");
      setSubTitle("");
      setSubDescription("");
      void qc.invalidateQueries({ queryKey: ["subrequirements", rid] });
      void qc.invalidateQueries({ queryKey: ["coverage", rid] });
      void qc.invalidateQueries({ queryKey: ["trace", rid] });
      void qc.invalidateQueries({ queryKey: ["requirements"] });
    },
    onError: (e: Error) => setSubErr(e.message),
  });

  useEffect(() => {
    if (location.hash !== "#sub" || !reqQ.isSuccess) return;
    const timer = window.setTimeout(() => {
      subSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 200);
    return () => window.clearTimeout(timer);
  }, [location.hash, location.pathname, reqQ.isSuccess, reqQ.data?.id]);

  if (!Number.isFinite(rid)) return null;
  if (reqQ.isLoading) return <Typography>{t("common.loading")}</Typography>;
  if (reqQ.isError) return <Typography color="error">{reqQ.error instanceof Error ? reqQ.error.message : t("common.error")}</Typography>;
  const r = reqQ.data!;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {r.key} — {r.title}
      </Typography>
      <Typography color="text.secondary" variant="body2" gutterBottom>
        <StatusChip value={r.status} /> {t(`priority.${r.priority}` as never)}
      </Typography>
      <Typography variant="body1" sx={{ mb: 2, whiteSpace: "pre-wrap" }}>
        {r.description}
      </Typography>
      <Button component={Link} to="/requirements" sx={{ mb: 2 }}>
        ← {t("requirements.title")}
      </Button>

      <Paper ref={subSectionRef} id="sub" sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          {t("requirements.subListTitle")}
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          {t("requirements.subFormLead", { key: r.key })}
        </Alert>
        <Box sx={{ mb: 2, p: 1.5, border: 1, borderColor: "divider", borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" display="block">
            {t("requirements.subParentLabel")}
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            {r.key} — {r.title}
          </Typography>
        </Box>
        {subQ.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {subQ.error instanceof Error ? subQ.error.message : t("common.error")}
          </Alert>
        )}
        {subErr && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {subErr}
          </Alert>
        )}
        {subOk && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSubOk(false)}>
            {t("requirements.subCreated")}
          </Alert>
        )}
        <Typography variant="subtitle2" gutterBottom>
          {t("requirements.subFormTitle")}
        </Typography>
        <Box
          component="form"
          sx={{ display: "flex", flexDirection: "column", gap: 2, maxWidth: 520, mb: 2 }}
          onSubmit={(e) => {
            e.preventDefault();
            createSub.mutate();
          }}
        >
          <TextField
            required
            size="small"
            label={t("requirements.key")}
            value={subKey}
            onChange={(e) => setSubKey(e.target.value)}
            helperText={t("requirements.subKeyHelp", { parentKey: r.key })}
          />
          <TextField
            required
            size="small"
            label={t("requirements.reqTitle")}
            value={subTitle}
            onChange={(e) => setSubTitle(e.target.value)}
          />
          <TextField
            size="small"
            label={t("requirements.description")}
            value={subDescription}
            onChange={(e) => setSubDescription(e.target.value)}
            multiline
            minRows={2}
          />
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            <TextField
              select
              size="small"
              label={t("requirements.status")}
              value={subStatus}
              onChange={(e) => setSubStatus(e.target.value as RequirementStatus)}
              sx={{ minWidth: 180 }}
            >
              {(["draft", "approved", "implemented", "verified", "rejected"] as const).map((s) => (
                <MenuItem key={s} value={s}>
                  {t(`status.${s}`)}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              size="small"
              label={t("requirements.priority")}
              value={subPriority}
              onChange={(e) => setSubPriority(e.target.value as Priority)}
              sx={{ minWidth: 180 }}
            >
              {(["low", "medium", "high", "critical"] as const).map((p) => (
                <MenuItem key={p} value={p}>
                  {t(`priority.${p}`)}
                </MenuItem>
              ))}
            </TextField>
          </Box>
          <Button
            type="submit"
            variant="contained"
            disabled={createSub.isPending || !subKey.trim() || !subTitle.trim()}
            sx={{ alignSelf: "flex-start" }}
          >
            {t("requirements.addSub")}
          </Button>
        </Box>

        {subQ.isLoading && <Typography color="text.secondary">{t("common.loading")}</Typography>}
        {subQ.data && subQ.data.length === 0 && (
          <Typography color="text.secondary" variant="body2">
            {t("requirements.subEmpty")}
          </Typography>
        )}
        {subQ.data && subQ.data.length > 0 && (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t("requirements.key")}</TableCell>
                <TableCell>{t("requirements.reqTitle")}</TableCell>
                <TableCell>{t("requirements.status")}</TableCell>
                <TableCell>{t("requirements.priority")}</TableCell>
                <TableCell>{t("common.updatedAt")}</TableCell>
                <TableCell>{t("common.updatedBy")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {subQ.data.map((s) => (
                <TableRow key={s.id}>
                  <TableCell>{s.key}</TableCell>
                  <TableCell>{s.title}</TableCell>
                  <TableCell>
                    <StatusChip value={s.status} />
                  </TableCell>
                  <TableCell>{t(`priority.${s.priority}` as never)}</TableCell>
                  <TableCell>{new Date(s.updated_at).toLocaleString()}</TableCell>
                  <TableCell>{s.updated_by || "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Paper>

      <RequirementTestsPanel
        requirementId={rid}
        requirementKey={r.key}
        subRequirements={subQ.data ?? []}
      />

      {covQ.data && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t("requirements.coverage")}
          </Typography>
          <Typography variant="body2">
            {t("requirements.testsTotal")}: {covQ.data.tests_total} · {t("requirements.testsPassed")}:{" "}
            {covQ.data.tests_passed}
          </Typography>
          <Typography variant="body2">
            {t("requirements.subsWithTest")}: {covQ.data.subrequirements_with_test} /{" "}
            {covQ.data.subrequirements_total}
          </Typography>
          <Typography variant="body2">
            {t("requirements.allSubsCovered")}:{" "}
            {covQ.data.all_subrequirements_have_test ? t("requirements.yes") : t("requirements.no")}
          </Typography>
        </Paper>
      )}

      {traceQ.data && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t("requirements.traceability")}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {t("requirements.tests")} ({t("requirements.detailTitle")})
          </Typography>
          <Table size="small" sx={{ mb: 2 }}>
            <TableHead>
              <TableRow>
                <TableCell>{t("requirements.key")}</TableCell>
                <TableCell>{t("requirements.reqTitle")}</TableCell>
                <TableCell>{t("tests.status")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {traceQ.data.tests_on_requirement.map((te) => (
                <TableRow key={te.id}>
                  <TableCell>{te.key}</TableCell>
                  <TableCell>{te.title}</TableCell>
                  <TableCell>
                    <StatusChip value={te.status} kind="test" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Divider sx={{ my: 2 }} />
          {traceQ.data.sub_requirements.map((block) => (
            <Box key={block.sub_requirement.id} sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                {block.sub_requirement.key} — {block.sub_requirement.title}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                {t("requirements.testsOnSub")}
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t("requirements.key")}</TableCell>
                    <TableCell>{t("requirements.reqTitle")}</TableCell>
                    <TableCell>{t("tests.status")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {block.tests.map((te) => (
                    <TableRow key={te.id}>
                      <TableCell>{te.key}</TableCell>
                      <TableCell>{te.title}</TableCell>
                      <TableCell>
                        <StatusChip value={te.status} kind="test" />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          ))}
        </Paper>
      )}
    </Box>
  );
}
