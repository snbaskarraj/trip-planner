import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { ConditionsBanner } from "../components/ConditionsBanner";
import { StatusMessage } from "../components/StatusMessage";

export default function ShareView() {
  const { token } = useParams();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [conditions, setConditions] = useState({});

  async function load() {
    setLoading(true);
    setError("");
    setNotFound(false);
    try {
      const data = await api.getShare(token);
      setTrip(data);
    } catch (err) {
      if (err.status === 404) {
        setNotFound(true);
      } else {
        setError(err.message || "Could not load shared itinerary.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [token]);

  useEffect(() => {
    if (!trip?.days?.length) {
      return;
    }
    let cancelled = false;
    async function loadConditions() {
      const next = {};
      await Promise.all(
        trip.days.map(async (day) => {
          try {
            next[day.id] = await api.getConditions(day.id);
          } catch {
            next[day.id] = { status: "unavailable" };
          }
        }),
      );
      if (!cancelled) {
        setConditions({ ...next });
      }
    }
    loadConditions();
    return () => {
      cancelled = true;
    };
  }, [trip]);

  if (loading) {
    return (
      <main className="page share">
        <StatusMessage>Loading shared itinerary…</StatusMessage>
      </main>
    );
  }

  if (notFound) {
    return (
      <main className="page share">
        <StatusMessage tone="error">This share link is invalid or has been removed.</StatusMessage>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page share">
        <StatusMessage tone="error" actionLabel="Retry" onAction={load}>
          {error}
        </StatusMessage>
      </main>
    );
  }

  return (
    <main className="page share">
      <p className="eyebrow">Shared itinerary · read only</p>
      <header className="hero compact">
        <h1>{trip.title}</h1>
        <p className="lede">
          {trip.destination} · {trip.start_date} → {trip.end_date}
        </p>
      </header>

      {!trip.days.length ? (
        <StatusMessage>This trip has no days published yet.</StatusMessage>
      ) : (
        <ol className="day-list">
          {trip.days.map((day) => (
            <li key={day.id} className="day-card">
              <div className="day-head">
                <div>
                  <h2>{day.date}</h2>
                  <p className="muted">
                    {day.start_time || "—"} to {day.end_time || "—"}
                  </p>
                </div>
                <ConditionsBanner state={conditions[day.id] || { loading: true }} />
              </div>
              {day.notes ? <p>{day.notes}</p> : null}
              <ul className="activity-list readonly">
                {day.activities.map((activity) => (
                  <li key={activity.id}>
                    <div>
                      <strong>{activity.title}</strong>
                      <span className="muted">
                        {[activity.start_time, activity.end_time].filter(Boolean).join("–") || "Untimed"}
                        {activity.location ? ` · ${activity.location}` : ""}
                      </span>
                      {activity.notes ? <p>{activity.notes}</p> : null}
                    </div>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ol>
      )}
      <p className="muted">
        <Link to="/">Make your own trip</Link>
      </p>
    </main>
  );
}
