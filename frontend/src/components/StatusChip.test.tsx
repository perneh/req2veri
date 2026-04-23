import { render, screen, waitFor } from "@testing-library/react";
import { I18nextProvider } from "react-i18next";

import i18n from "../i18n";
import { StatusChip } from "./StatusChip";

describe("StatusChip", () => {
  it("renders translated label", async () => {
    render(
      <I18nextProvider i18n={i18n}>
        <StatusChip value="passed" kind="test" />
      </I18nextProvider>,
    );
    await waitFor(() => expect(screen.getByText("Passed")).toBeInTheDocument());
  });
});
