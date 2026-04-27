import {
  Box,
  Button,
  Link as MuiLink,
  MenuItem,
  Paper,
  Stack,
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
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { VerificationTest } from "../api/types";
import { StatusChip } from "../components/StatusChip";

type ReferenceFilter = "any" | "linked" | "unlinked";

function parseReference(v: string | null): ReferenceFilter {
  if (v === "linked" || v === "unlinked" || v === "any") return v;
  return "any";
}

export function TestsListPage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const reference = parseReference(searchParams.get("reference"));

  const q = useQuery({
    queryKey: ["tests", reference],
    queryFn: () => {
      const qs = new URLSearchParams();
      if (reference !== "any") qs.set("reference", reference);
      const suffix = qs.toString();
      return apiFetch<VerificationTest[]>(suffix ? `/tests?${suffix}` : "/tests");
    },
  });

  return (
    <Box>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ sm: "center" }} justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h5">{t("tests.title")}</Typography>
        <Button component={Link} to="/tests/new" variant="contained" size="small">
          {t("tests.newStandalone")}
        </Button>
      </Stack>
      <TextField
        select
        size="small"
        label={t("tests.referenceFilter")}
        value={reference}
        onChange={(e) => {
          const next = e.target.value as ReferenceFilter;
          setSearchParams(next === "any" ? {} : { reference: next });
        }}
        sx={{ minWidth: 240, mb: 2 }}
      >
        <MenuItem value="any">{t("tests.referenceAny")}</MenuItem>
        <MenuItem value="linked">{t("tests.referenceLinked")}</MenuItem>
        <MenuItem value="unlinked">{t("tests.referenceUnlinked")}</MenuItem>
      </TextField>
      {q.isLoading && <Typography>{t("common.loading")}</Typography>}
      {q.isError && <Typography color="error">{q.error instanceof Error ? q.error.message : t("common.error")}</Typography>}
      {q.data && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t("requirements.reqTitle")}</TableCell>
                <TableCell>{t("tests.method")}</TableCell>
                <TableCell>{t("tests.status")}</TableCell>
                <TableCell>{t("tests.linked")}</TableCell>
                <TableCell>{t("common.updatedAt")}</TableCell>
                <TableCell>{t("common.updatedBy")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {q.data.map((te) => (
                <TableRow key={te.id}>
                  <TableCell>
                    <MuiLink component={Link} to={`/tests/${te.id}`} underline="hover">
                      {te.title}
                    </MuiLink>
                  </TableCell>
                  <TableCell>{t(`method.${te.method}` as never)}</TableCell>
                  <TableCell>
                    <StatusChip value={te.status} kind="test" />
                  </TableCell>
                  <TableCell>
                    {te.requirement_id != null
                      ? `REQ #${te.requirement_id}`
                      : te.sub_requirement_id != null
                        ? `SUB #${te.sub_requirement_id}`
                        : t("tests.unlinkedLabel")}
                  </TableCell>
                  <TableCell>{new Date(te.updated_at).toLocaleString()}</TableCell>
                  <TableCell>{te.updated_by || "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
