import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the product identity", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Day-ahead wind, without hindsight." })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "WindSight UK home" })).toBeInTheDocument();
  });
});
