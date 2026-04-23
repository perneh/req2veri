import {
  Alert,
  Box,
  Button,
  FormControl,
  FormControlLabel,
  MenuItem,
  Paper,
  Radio,
  RadioGroup,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { SubRequirement, TestMethod, VerificationTest } from "../api/types";
import { StatusChip } from "./StatusChip";

type LinkTarget = "requirement" | "sub" | "standalone";

type Props = {
  requirementId: number;
  requirementKey: string;
  subRequirements: SubRequirement[];
};

export function RequirementTestsPanel({ requirementId, requirementKey, subRequirements }: Props) {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const [linkTo, setLinkTo] = useState<LinkTarget>("requirement");
  const [subId, setSubId] = useState<number | "">("");

  const [tkey, setTkey] = useState("");
  const [ttitle, setTtitle] = useState("");
  const [tdesc, setTdesc] = useState("");
  const [tpre, setTpre] = useState("");
  const [taction, setTaction] = useState("");
  const [tmethod, setTmethod] = useState<TestMethod>("test");
  const [texp, setTexp] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  const testsOnReq = useQuery({
    queryKey: ["req-tests", requirementId],
    queryFn: () => apiFetch<VerificationTest[]>(`/requirements/${requirementId}/tests`),
  });

  const subTestQueries = useQueries({
    queries: subRequirements.map((s) => ({
      queryKey: ["sub-tests", s.id],
      queryFn: () => apiFetch<VerificationTest[]>(`/subrequirements/${s.id}/tests`),
    })),
  });

  const createTest = useMutation({
    mutationFn: async () => {
      const base = {
        key: tkey,
        title: ttitle,
        description: tdesc,
        precondition: tpre,
        action: taction,
        method: tmethod,
        expected_result: texp,
      };
      if (linkTo === "requirement") {
        return apiFetch<VerificationTest>(`/requirements/${requirementId}/tests`, {
          method: "POST",
          json: {
            ...base,
            requirement_id: requirementId,
            sub_requirement_id: null,
          },
        });
      }
      if (linkTo === "standalone") {
        return apiFetch<VerificationTest>("/tests", {
          method: "POST",
          json: {
            ...base,
            requirement_id: null,
            sub_requirement_id: null,
          },
        });
      }
      if (subId === "") throw new Error("sub");
      return apiFetch<VerificationTest>(`/subrequirements/${subId}/tests`, {
        method: "POST",
        json: {
          ...base,
          requirement_id: null,
          sub_requirement_id: subId,
        },
      });
    },
    onSuccess: () => {
      setErr(null);
      setOk(true);
      setTkey("");
      setTtitle("");
      setTdesc("");
      setTpre("");
      setTaction("");
      setTexp("");
      void qc.invalidateQueries({ queryKey: ["req-tests", requirementId] });
      void qc.invalidateQueries({ queryKey: ["trace", requirementId] });
      void qc.invalidateQueries({ queryKey: ["coverage", requirementId] });
      void qc.invalidateQueries({ queryKey: ["tests"] });
      subRequirements.forEach((s) => {
        void qc.invalidateQueries({ queryKey: ["sub-tests", s.id] });
      });
    },
    onError: (e: Error) => {
      setErr(e.message);
      setOk(false);
    },
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    setOk(false);
    if (linkTo === "sub" && subId === "") {
      setErr(t("tests.pickSub"));
      return;
    }
    createTest.mutate();
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="subtitle1" gutterBottom>
        {t("tests.writeTitle")}
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        {t("tests.writeHintDetail")}
      </Alert>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {t("tests.reportLaterHint")}
      </Typography>
      {err && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setErr(null)}>
          {err}
        </Alert>
      )}
      {ok && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setOk(false)}>
          {t("tests.created")}
        </Alert>
      )}

      <Box component="form" onSubmit={onSubmit} sx={{ maxWidth: 560, display: "flex", flexDirection: "column", gap: 2, mb: 3 }}>
        <FormControl>
          <Typography variant="body2" gutterBottom>
            {t("tests.linkTo")}
          </Typography>
          <RadioGroup
            value={linkTo}
            onChange={(_, v) => {
              setLinkTo(v as LinkTarget);
              if (v === "requirement" || v === "standalone") setSubId("");
            }}
          >
            <FormControlLabel value="requirement" control={<Radio size="small" />} label={t("tests.linkToReq", { key: requirementKey })} />
            <FormControlLabel
              value="sub"
              control={<Radio size="small" />}
              label={t("tests.linkToSub")}
              disabled={subRequirements.length === 0}
            />
            <FormControlLabel value="standalone" control={<Radio size="small" />} label={t("tests.linkNone")} />
          </RadioGroup>
        </FormControl>
        {linkTo === "sub" && (
          <TextField
            select
            required
            size="small"
            label={t("tests.pickSubLabel")}
            value={subId === "" ? "" : String(subId)}
            onChange={(e) => {
              const v = e.target.value;
              setSubId(v === "" ? "" : Number(v));
            }}
            sx={{ maxWidth: 400 }}
          >
            <MenuItem value="">{t("tests.pickSub")}</MenuItem>
            {subRequirements.map((s) => (
              <MenuItem key={s.id} value={String(s.id)}>
                {s.key} — {s.title}
              </MenuItem>
            ))}
          </TextField>
        )}
        <TextField size="small" required label={t("requirements.key")} value={tkey} onChange={(e) => setTkey(e.target.value)} />
        <TextField size="small" required label={t("requirements.reqTitle")} value={ttitle} onChange={(e) => setTtitle(e.target.value)} />
        <TextField
          size="small"
          label={t("requirements.description")}
          value={tdesc}
          onChange={(e) => setTdesc(e.target.value)}
          multiline
          minRows={2}
        />
        <TextField
          size="small"
          label={t("tests.precondition")}
          value={tpre}
          onChange={(e) => setTpre(e.target.value)}
          multiline
          minRows={2}
        />
        <TextField
          size="small"
          label={t("tests.action")}
          value={taction}
          onChange={(e) => setTaction(e.target.value)}
          multiline
          minRows={2}
        />
        <TextField
          select
          size="small"
          label={t("tests.method")}
          value={tmethod}
          onChange={(e) => setTmethod(e.target.value as TestMethod)}
          sx={{ minWidth: 200 }}
        >
          {(["inspection", "analysis", "test", "demonstration"] as const).map((m) => (
            <MenuItem key={m} value={m}>
              {t(`method.${m}`)}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          size="small"
          label={t("tests.expected")}
          value={texp}
          onChange={(e) => setTexp(e.target.value)}
          multiline
          minRows={2}
        />
        <Button type="submit" variant="contained" disabled={createTest.isPending || !tkey.trim() || !ttitle.trim()}>
          {t("tests.addTest")}
        </Button>
      </Box>

      <Typography variant="subtitle2" gutterBottom>
        {t("tests.listOnPage")}
      </Typography>
      {testsOnReq.isLoading && <Typography color="text.secondary">{t("common.loading")}</Typography>}
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t("tests.linked")}</TableCell>
            <TableCell>{t("requirements.key")}</TableCell>
            <TableCell>{t("requirements.reqTitle")}</TableCell>
            <TableCell>{t("tests.status")}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {testsOnReq.data?.map((te) => (
            <TableRow key={`r-${te.id}`}>
              <TableCell>
                {requirementKey} ({t("requirements.detailTitle")})
              </TableCell>
              <TableCell>{te.key}</TableCell>
              <TableCell>{te.title}</TableCell>
              <TableCell>
                <StatusChip value={te.status} kind="test" />
              </TableCell>
            </TableRow>
          ))}
          {subRequirements.flatMap((s, i) => {
            const q = subTestQueries[i];
            const rows = q?.data ?? [];
            return rows.map((te) => (
              <TableRow key={`s-${te.id}`}>
                <TableCell>
                  {s.key} ({t("requirements.subrequirements")})
                </TableCell>
                <TableCell>{te.key}</TableCell>
                <TableCell>{te.title}</TableCell>
                <TableCell>
                  <StatusChip value={te.status} kind="test" />
                </TableCell>
              </TableRow>
            ));
          })}
          {(!testsOnReq.data || testsOnReq.data.length === 0) &&
            subTestQueries.every((q) => !q.data || q.data.length === 0) &&
            !testsOnReq.isLoading && (
              <TableRow>
                <TableCell colSpan={4}>
                  <Typography color="text.secondary" variant="body2">
                    {t("tests.emptyOnDetail")}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
        </TableBody>
      </Table>
    </Paper>
  );
}
