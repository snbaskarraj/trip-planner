export function ConditionsBanner({ state }) {
  if (!state || state.loading) {
    return (
      <div className="weather weather-loading" role="status">
        Checking weather…
      </div>
    );
  }

  if (state.status === "unavailable" || state.error) {
    return (
      <div className="weather weather-unavailable" role="status">
        Weather unavailable
      </div>
    );
  }

  if (state.status === "ok") {
    const temp =
      typeof state.temperature_c === "number"
        ? `${Math.round(state.temperature_c)}°C`
        : "";
    return (
      <div className="weather weather-ok" role="status">
        <strong>{temp}</strong>
        <span>{state.summary}</span>
        {state.wind_kph != null ? <em>{Math.round(state.wind_kph)} km/h wind</em> : null}
      </div>
    );
  }

  return null;
}
