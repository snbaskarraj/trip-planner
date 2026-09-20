import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ItineraryEditor from "./pages/ItineraryEditor";
import ShareView from "./pages/ShareView";
import TripList from "./pages/TripList";

export default function App() {
  return (
    <BrowserRouter>
      <div className="shell">
        <Routes>
          <Route path="/" element={<TripList />} />
          <Route path="/trips/:tripId" element={<ItineraryEditor />} />
          <Route path="/share/:token" element={<ShareView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
