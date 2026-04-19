import { useState } from "react";
import Home from "./pages/Home.jsx";
import Study from "./pages/Study.jsx";

export default function App() {
  const [view, setView] = useState("home");
  const [activeDeckId, setActiveDeckId] = useState(null);
  const [refresh, setRefresh] = useState(0);

  return (
    <div className="min-h-screen">
      {view === "home" && (
        <Home onStudy={(id) => { setActiveDeckId(id); setView("study"); }} refreshKey={refresh} />
      )}
      {view === "study" && (
        <Study deckId={activeDeckId} onBack={() => { setView("home"); setRefresh(r => r + 1); }} />
      )}
    </div>
  );
}