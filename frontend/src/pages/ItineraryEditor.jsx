import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { ConditionsBanner } from "../components/ConditionsBanner";
import { StatusMessage } from "../components/StatusMessage";

const emptyDay = { date: "", start_time: "", end_time: "", notes: "" };
const emptyActivity = { title: "", location: "", start_time: "", end_time: "", notes: "" };

export default function ItineraryEditor() {
  const { tripId } = useParams();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [dayForm, setDayForm] = useState(emptyDay);
  const [dayError, setDayError] = useState("");
  const [activityDrafts, setActivityDrafts] = useState({});
  const [activityErrors, setActivityErrors] = useState({});
  const [conditions, setConditions] = useState({});
  const [copied, setCopied] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    setNotFound(false);
    try {
      const data = await api.getTrip(tripId);
      setTrip(data);
    } catch (err) {
      if (err.status === 404) {
        setNotFound(true);
      } else {
        setError(err.message || "Could not load itinerary.");
      }
    } finally {
      setLoading(false);
    }
  }, [tripId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!trip?.days?.length) {
      return;
    }
    let cancelled = false;
    async function loadConditions() {
      const next = {};
      await Promise.all(
        trip.days.map(async (day) => {
          next[day.id] = { loading: true };
          try {
            const result = await api.getConditions(day.id);
            next[day.id] = result;
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

  function shareUrl() {
    return `${window.location.origin}/share/${trip.share_token}`;
  }

  async function copyShareLink() {
    try {
      await navigator.clipboard.writeText(shareUrl());
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
      window.prompt("Copy this share link", shareUrl());
    }
  }

  async function onCreateDay(event) {
    event.preventDefault();
    setDayError("");
    try {
      await api.createDay(trip.id, dayForm);
      setDayForm(emptyDay);
      await load();
    } catch (err) {
      setDayError(err.message || "Could not save day.");
    }
  }

  async function onDeleteDay(dayId) {
    try {
      await api.deleteDay(dayId);
      await load();
    } catch (err) {
      setError(err.message || "Could not delete day.");
    }
  }

  function updateActivityDraft(dayId, field, value) {
    setActivityDrafts((current) => ({
      ...current,
      [dayId]: { ...(current[dayId] || emptyActivity), [field]: value },
    }));
  }

  async function onCreateActivity(event, dayId) {
    event.preventDefault();
    setActivityErrors((current) => ({ ...current, [dayId]: "" }));
    try {
      await api.createActivity(dayId, activityDrafts[dayId] || emptyActivity);
      setActivityDrafts((current) => ({ ...current, [dayId]: emptyActivity }));
      await load();
    } catch (err) {
      setActivityErrors((current) => ({
        ...current,
        [dayId]: err.message || "Could not save activity.",
      }));
    }
  }

  async function onDeleteActivity(activityId) {
    try {
      await api.deleteActivity(activityId);
      await load();
    } catch (err) {
      setError(err.message || "Could not delete activity.");
    }
  }

  if (loading) {
    return (
      <main className="page">
        <StatusMessage>Loading itinerary…</StatusMessage>
      </main>
    );
  }

  if (notFound) {
    return (
      <main className="page">
        <StatusMessage tone="error">
          This trip does not exist.{" "}
          <Link to="/">Back to trips</Link>
        </StatusMessage>
      </main>
    );
  }

  if (error && !trip) {
    return (
      <main className="page">
        <StatusMessage tone="error" actionLabel="Retry" onAction={load}>
          {error}
        </StatusMessage>
      </main>
    );
  }

  return (
    <main className="page">
      <p className="crumb">
        <Link to="/">All trips</Link>
      </p>
      <header className="hero compact">
        <p className="eyebrow">{trip.destination}</p>
        <h1>{trip.title}</h1>
        <p className="lede">
          {trip.start_date} → {trip.end_date}
        </p>
        <div className="share-row">
          <code>{shareUrl()}</code>
          <button type="button" className="primary" onClick={copyShareLink}>
            {copied ? "Copied" : "Copy share link"}
          </button>
        </div>
      </header>

      {error ? (
        <StatusMessage tone="error" actionLabel="Retry" onAction={load}>
          {error}
        </StatusMessage>
      ) : null}

      <section className="panel">
        <h2>Add a day</h2>
        <form className="grid-form" onSubmit={onCreateDay}>
          <label>
            Date
            <input
              type="date"
              value={dayForm.date}
              onChange={(event) => setDayForm({ ...dayForm, date: event.target.value })}
              required
            />
          </label>
          <label>
            Start
            <input
              type="time"
              value={dayForm.start_time}
              onChange={(event) => setDayForm({ ...dayForm, start_time: event.target.value })}
            />
          </label>
          <label>
            End
            <input
              type="time"
              value={dayForm.end_time}
              onChange={(event) => setDayForm({ ...dayForm, end_time: event.target.value })}
            />
          </label>
          <label className="wide">
            Notes
            <input
              value={dayForm.notes}
              onChange={(event) => setDayForm({ ...dayForm, notes: event.target.value })}
              placeholder="Neighborhood, pace, reservations…"
            />
          </label>
          <button type="submit" className="primary">
            Save day
          </button>
        </form>
        {dayError ? <StatusMessage tone="error">{dayError}</StatusMessage> : null}
      </section>

      {!trip.days.length ? (
        <StatusMessage>No days yet. Add the first day of the plan above.</StatusMessage>
      ) : (
        <ol className="day-list">
          {trip.days.map((day) => {
            const draft = activityDrafts[day.id] || emptyActivity;
            return (
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
                <ul className="activity-list">
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
                      <button type="button" className="ghost danger" onClick={() => onDeleteActivity(activity.id)}>
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
                <form className="inline-form" onSubmit={(event) => onCreateActivity(event, day.id)}>
                  <input
                    placeholder="Activity title"
                    value={draft.title}
                    onChange={(event) => updateActivityDraft(day.id, "title", event.target.value)}
                    required
                  />
                  <input
                    placeholder="Location"
                    value={draft.location}
                    onChange={(event) => updateActivityDraft(day.id, "location", event.target.value)}
                  />
                  <input
                    type="time"
                    value={draft.start_time}
                    onChange={(event) => updateActivityDraft(day.id, "start_time", event.target.value)}
                  />
                  <input
                    type="time"
                    value={draft.end_time}
                    onChange={(event) => updateActivityDraft(day.id, "end_time", event.target.value)}
                  />
                  <button type="submit" className="primary">
                    Add activity
                  </button>
                </form>
                {activityErrors[day.id] ? (
                  <StatusMessage tone="error">{activityErrors[day.id]}</StatusMessage>
                ) : null}
                <button type="button" className="text-btn danger" onClick={() => onDeleteDay(day.id)}>
                  Delete day
                </button>
              </li>
            );
          })}
        </ol>
      )}
    </main>
  );
}
