import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { StatusMessage } from "../components/StatusMessage";

const emptyForm = {
  title: "",
  destination: "",
  start_date: "",
  end_date: "",
};

export default function TripList() {
  const navigate = useNavigate();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await api.listTrips();
      setTrips(data.trips || []);
    } catch (err) {
      setError(err.message || "Could not load trips.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function onCreate(event) {
    event.preventDefault();
    setSaving(true);
    setFormError("");
    try {
      const trip = await api.createTrip(form);
      navigate(`/trips/${trip.id}`);
    } catch (err) {
      setFormError(err.message || "Could not create trip.");
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(event, tripId) {
    event.preventDefault();
    event.stopPropagation();
    if (!window.confirm("Delete this trip and all of its days?")) {
      return;
    }
    try {
      await api.deleteTrip(tripId);
      setTrips((current) => current.filter((trip) => trip.id !== tripId));
    } catch (err) {
      setError(err.message || "Could not delete trip.");
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">Trip Planner</p>
        <h1>Plan the days. Share the itinerary.</h1>
        <p className="lede">
          Multi-day trips, day-by-day plans, and a read-only link for anyone traveling with you.
        </p>
      </header>

      <section className="panel">
        <h2>New trip</h2>
        <form className="grid-form" onSubmit={onCreate}>
          <label>
            Title
            <input name="title" value={form.title} onChange={updateField} required maxLength={200} />
          </label>
          <label>
            Destination
            <input
              name="destination"
              value={form.destination}
              onChange={updateField}
              required
              maxLength={200}
              placeholder="Kyoto"
            />
          </label>
          <label>
            Start
            <input type="date" name="start_date" value={form.start_date} onChange={updateField} required />
          </label>
          <label>
            End
            <input type="date" name="end_date" value={form.end_date} onChange={updateField} required />
          </label>
          <button type="submit" className="primary" disabled={saving}>
            {saving ? "Saving…" : "Create trip"}
          </button>
        </form>
        {formError ? <StatusMessage tone="error">{formError}</StatusMessage> : null}
      </section>

      <section>
        <h2>Your trips</h2>
        {loading ? <StatusMessage>Loading trips…</StatusMessage> : null}
        {error ? (
          <StatusMessage tone="error" actionLabel="Retry" onAction={load}>
            {error}
          </StatusMessage>
        ) : null}
        {!loading && !error && trips.length === 0 ? (
          <StatusMessage>
            No trips yet. Create your first itinerary above — it only takes a destination and dates.
          </StatusMessage>
        ) : null}
        <ul className="trip-grid">
          {trips.map((trip) => (
            <li key={trip.id}>
              <Link className="trip-card" to={`/trips/${trip.id}`}>
                <h3>{trip.title}</h3>
                <p>{trip.destination}</p>
                <p className="muted">
                  {trip.start_date} → {trip.end_date}
                </p>
                <button type="button" className="ghost danger" onClick={(event) => onDelete(event, trip.id)}>
                  Delete
                </button>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
