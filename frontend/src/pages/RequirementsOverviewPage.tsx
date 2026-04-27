import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Link as MuiLink,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { RequirementHierarchyItem } from "../api/types";
import { StatusChip } from "../components/StatusChip";

export function RequirementsOverviewPage() {
  const { t } = useTranslation();
  const q = useQuery({
    queryKey: ["requirements-hierarchy"],
    queryFn: () => apiFetch<RequirementHierarchyItem[]>("/requirements/hierarchy"),
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {t("overview.title")}
      </Typography>
      <Typography color="text.secondary" variant="body2" sx={{ mb: 2 }}>
        {t("overview.lead")}
      </Typography>
      {q.isLoading && <Typography>{t("common.loading")}</Typography>}
      {q.isError && <Typography color="error">{q.error instanceof Error ? q.error.message : t("common.error")}</Typography>}
      {q.data?.map((row) => (
        <Accordion key={row.requirement.id} defaultExpanded={false} disableGutters>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, flexWrap: "wrap" }}>
              <MuiLink component={Link} to={`/requirements/${row.requirement.id}`} onClick={(e) => e.stopPropagation()}>
                {row.requirement.key}
              </MuiLink>
              <Typography fontWeight={600}>{row.requirement.title}</Typography>
              <StatusChip value={row.requirement.status} />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            {row.sub_requirements.length === 0 ? (
              <Typography color="text.secondary" variant="body2">
                {t("overview.noSubs")}
              </Typography>
            ) : (
              <Box component="ul" sx={{ m: 0, pl: 2 }}>
                {row.sub_requirements.map((s) => (
                  <li key={s.id}>
                    <Typography variant="body2" component="div">
                      <strong>{s.key}</strong> — {s.title} <StatusChip value={s.status} />
                    </Typography>
                  </li>
                ))}
              </Box>
            )}
            <MuiLink component={Link} to={`/requirements/${row.requirement.id}#sub`} variant="body2" sx={{ mt: 1, display: "inline-block" }}>
              {t("overview.openDetail")}
            </MuiLink>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}
