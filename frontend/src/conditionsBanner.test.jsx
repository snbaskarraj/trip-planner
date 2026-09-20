import { render, screen } from "@testing-library/react";
import { ConditionsBanner } from "./components/ConditionsBanner";

describe("ConditionsBanner", () => {
  it("shows a loading state while conditions are fetching", () => {
    render(<ConditionsBanner state={{ loading: true }} />);
    expect(screen.getByRole("status")).toHaveTextContent("Checking weather");
  });

  it("renders an unavailable state when the maps/weather call times out", () => {
    render(<ConditionsBanner state={{ status: "unavailable" }} />);
    expect(screen.getByRole("status")).toHaveTextContent("Weather unavailable");
  });

  it("renders temperature and summary on success", () => {
    render(
      <ConditionsBanner
        state={{ status: "ok", temperature_c: 18.4, summary: "Partly cloudy", wind_kph: 9.2 }}
      />,
    );
    expect(screen.getByRole("status")).toHaveTextContent("18°C");
    expect(screen.getByRole("status")).toHaveTextContent("Partly cloudy");
  });
});
