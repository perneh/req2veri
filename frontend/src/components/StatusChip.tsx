import { Chip } from "@mui/material";
import { useTranslation } from "react-i18next";

type Kind = "req" | "test";

export function StatusChip({ value, kind = "req" }: { value: string; kind?: Kind }) {
  const { t } = useTranslation();
  const label = kind === "test" ? t(`status.${value}` as never) : t(`status.${value}` as never);
  const color =
    value === "verified" || value === "passed"
      ? "success"
      : value === "failed" || value === "rejected"
        ? "error"
        : value === "blocked"
          ? "warning"
          : "default";
  return <Chip size="small" label={label} color={color} variant="outlined" />;
}
