import {
  Box,
  Button,
  Link as MuiLink,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableContainer,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMemo, useState } from "react";

import { apiFetch } from "../api/client";
import type { Requirement, RequirementStatus } from "../api/types";
import { StatusChip } from "../components/StatusChip";

export function RequirementsListPage() {
  const { t } = useTranslation();
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<RequirementStatus | "">("");
  const params = useMemo(() => {
    const p = new URLSearchParams();
    if (q) p.set("q", q);
    if (status) p.set("status", status);
    return p.toString();
  }, [q, status]);

  const query = useQuery({
    queryKey: ["requirements", params],
    queryFn: () => apiFetch<Requirement[]>(`/requirements?${params}`),
  });

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h5">{t("requirements.title")}</Typography>
        <Button component={Link} to="/requirements/new" variant="contained">
          {t("requirements.new")}
        </Button>
      </Box>
      <Typography color="text.secondary" variant="body2" sx={{ mb: 2 }}>
        {t("requirements.rowClickHint")}
      </Typography>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          <TextField
            size="small"
            label={t("requirements.search")}
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <TextField
            select
            size="small"
            label={t("requirements.status")}
            value={status}
            onChange={(e) => setStatus(e.target.value as RequirementStatus | "")}
            sx={{ minWidth: 160 }}
          >
            <MenuItem value="">{t("requirements.status")}</MenuItem>
            {(["draft", "approved", "implemented", "verified", "rejected"] as const).map((s) => (
              <MenuItem key={s} value={s}>
                {t(`status.${s}`)}
              </MenuItem>
            ))}
          </TextField>
        </Box>
      </Paper>
      {query.isLoading && <Typography>{t("common.loading")}</Typography>}
      {query.isError && <Typography color="error">{query.error instanceof Error ? query.error.message : t("common.error")}</Typography>}
      {query.data && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t("requirements.key")}</TableCell>
                <TableCell>{t("requirements.reqTitle")}</TableCell>
                <TableCell>{t("requirements.status")}</TableCell>
                <TableCell>{t("requirements.priority")}</TableCell>
                <TableCell>{t("requirements.approvedBy")}</TableCell>
                <TableCell>{t("requirements.approvedAt")}</TableCell>
                <TableCell>{t("common.updatedAt")}</TableCell>
                <TableCell>{t("common.updatedBy")}</TableCell>
                <TableCell>{t("requirements.actions")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {query.data.map((r) => (
                <TableRow key={r.id} hover>
                  <TableCell>
                    <MuiLink component={Link} to={`/requirements/${r.id}`} underline="hover" color="primary">
                      {r.key}
                    </MuiLink>
                  </TableCell>
                  <TableCell>
                    <MuiLink component={Link} to={`/requirements/${r.id}`} underline="hover" color="inherit">
                      {r.title}
                    </MuiLink>
                  </TableCell>
                  <TableCell>
                    <StatusChip value={r.status} />
                  </TableCell>
                  <TableCell>{t(`priority.${r.priority}` as never)}</TableCell>
                  <TableCell>{r.status === "approved" ? r.approved_by || "—" : "—"}</TableCell>
                  <TableCell>
                    {r.status === "approved" && r.approved_at ? new Date(r.approved_at).toLocaleString() : "—"}
                  </TableCell>
                  <TableCell>{new Date(r.updated_at).toLocaleString()}</TableCell>
                  <TableCell>{r.updated_by || "—"}</TableCell>
                  <TableCell sx={{ whiteSpace: "nowrap" }}>
                    <Button component={Link} to={`/requirements/${r.id}`} size="small">
                      {t("requirements.view")}
                    </Button>{" "}
                    <Button component={Link} to={`/requirements/${r.id}#sub`} size="small" variant="outlined">
                      {t("requirements.openDetailForSubs")}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
