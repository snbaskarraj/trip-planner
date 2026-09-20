const BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(`${BASE}${path}`, { ...options, headers });
  if (response.status === 204) {
    return null;
  }
  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }
  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : data.detail?.detail || `Request failed (${response.status})`;
    const error = new Error(message);
    error.status = response.status;
    error.code = data.code || data.detail?.code;
    error.body = data;
    throw error;
  }
  return data;
}

export const api = {
  health: () => request("/health"),
  listTrips: () => request("/api/trips"),
  createTrip: (body) => request("/api/trips", { method: "POST", body: JSON.stringify(body) }),
  getTrip: (id) => request(`/api/trips/${id}`),
  updateTrip: (id, body) =>
    request(`/api/trips/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteTrip: (id) => request(`/api/trips/${id}`, { method: "DELETE" }),
  createDay: (tripId, body) =>
    request(`/api/trips/${tripId}/days`, { method: "POST", body: JSON.stringify(body) }),
  updateDay: (dayId, body) =>
    request(`/api/days/${dayId}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteDay: (dayId) => request(`/api/days/${dayId}`, { method: "DELETE" }),
  createActivity: (dayId, body) =>
    request(`/api/days/${dayId}/activities`, { method: "POST", body: JSON.stringify(body) }),
  updateActivity: (activityId, body) =>
    request(`/api/activities/${activityId}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteActivity: (activityId) => request(`/api/activities/${activityId}`, { method: "DELETE" }),
  getShare: (token) => request(`/api/share/${token}`),
  getConditions: (dayId) => request(`/api/days/${dayId}/conditions`),
};
