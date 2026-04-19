import { useState, useEffect } from "react";
import { api } from "../api/client.js";
import NavBar from "../components/NavBar.jsx";
import SectionCard from "../components/SectionCard.jsx";
import MiniCard from "../components/MiniCard.jsx";
import UploadModal from "../components/UploadModal.jsx";
import WorkedExamplesPage from "../components/WorkedExamplesPage.jsx";
import WaterCube from "../components/WaterCube.jsx";

const SECTIONS = [
  { key:"concept",      label:"Key Concepts",  color:"#FFC2A3", emoji:"🧠" },
  { key:"definition",   label:"Definitions",    color:"#99E5FF", emoji:"📖" },
  { key:"relationship", label:"Relationships",  color:"#FFC2FA", emoji:"🔗" },
  { key:"edge_case",    label:"Edge Cases",     color:"#89F5BF", emoji:"⚡" },
];

export default function Home({ onStudy, refreshKey = 0 }) {
  const [decks, setDecks]               = useState([]);
  const [activeDeck, setActiveDeck]     = useState(null);
  const [deckCards, setDeckCards]       = useState([]);
  const [activeSection, setActiveSection] = useState(null);
  const [showUpload, setShowUpload]     = useState(false);
  const [showWorked, setShowWorked]     = useState(false);
  const [uploading, setUploading]       = useState(false);
  const [uploadMsg, setUploadMsg]       = useState("");
  const [deckName, setDeckName]         = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => { fetchDecks(); }, [refreshKey]);

const fetchDecks = async (forceReset = false, newDeckId = null) => {
    try {
      const data = await api.getDecks();
      setDecks(data.decks);
      if (data.decks.length > 0) {
        if (forceReset && newDeckId) {
          const d = data.decks.find(d => d.id === newDeckId);
          if (d) await loadDeck(d);
        } else {
          const d = activeDeck
            ? data.decks.find(d => d.id === activeDeck.id) || data.decks[0]
            : data.decks[0];
          if (d) await loadDeck(d);
        }
      }
    } catch (e) { console.error(e); }
};

  const loadDeck = async (deck) => {
    setActiveDeck(deck);
    setActiveSection(null);
    try {
      const data = await api.getDeck(deck.id);
      setDeckCards(data.cards);
    } catch (e) { console.error(e); }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setUploadMsg("Reading your PDF... 📚");
    try {
      setTimeout(() => setUploadMsg("AI is writing your cards... ✨"), 3000);
      const data = await api.uploadPDF(selectedFile, deckName || undefined);
      setUploadMsg(`Done! ${data.cards.length} cards created! 🎉`);
      setTimeout(() => {
        setShowUpload(false);
        setSelectedFile(null);
        setDeckName("");
        setUploadMsg("");
        fetchDecks(true, data.deck.id);
      }, 2000);
    } catch (e) {
      setUploadMsg("Oops! " + e.message);
      setUploading(false);
    }
  };

  const handleDelete = async () => {
      if (!confirm(`Delete "${activeDeck.name}"?`)) return;
      try {
        await api.deleteDeck(activeDeck.id);
        setActiveDeck(null);
        setDeckCards([]);
        // ✅ force reset so it loads first available deck
        const data = await api.getDecks();
        setDecks(data.decks);
        if (data.decks.length > 0) {
          loadDeck(data.decks[0]);
        }
      } catch (e) { alert("Delete failed: " + e.message); }
  };

  const sectionCards = (key) => deckCards.filter(c => {
    if (key === "edge_case") return ["edge_case","application","example"].includes(c.category);
    return c.category === key;
  });

  const workedCards = deckCards.filter(c => ["example","application"].includes(c.category));
  const total    = activeDeck?.total_cards || 0;
  const counts   = activeDeck?.mastery_counts || {};
  const mastered = (counts[1]||0) + (counts[2]||0) + (counts[3]||0);
  const fillPct  = total ? Math.round((mastered / total) * 100) : 0;
  const allDone  = fillPct === 100 && total > 0;

  return (
    <div className="min-h-screen grid-bg relative overflow-hidden">
      <NavBar
        decks={decks}
        activeDeck={activeDeck}
        onDeckChange={id => { const d = decks.find(x => x.id === id); if (d) loadDeck(d); }}
        onDelete={handleDelete}
        onNewDeck={() => setShowUpload(true)}
      />

      <div style={{position:"relative", width:"100%", height:"calc(100vh - 64px)"}}>
        <SectionCard section={SECTIONS[0]} cards={sectionCards("concept")}
          style={{position:"absolute", top:"5%", left:"3%", width:"27%", height:"40%"}}
          onClick={() => setActiveSection("concept")} />
        <SectionCard section={SECTIONS[1]} cards={sectionCards("definition")}
          style={{position:"absolute", top:"5%", right:"3%", width:"27%", height:"40%"}}
          onClick={() => setActiveSection("definition")} />
        <SectionCard section={SECTIONS[2]} cards={sectionCards("relationship")}
          style={{position:"absolute", bottom:"5%", left:"3%", width:"27%", height:"40%"}}
          onClick={() => setActiveSection("relationship")} />
        <SectionCard section={SECTIONS[3]} cards={sectionCards("edge_case")}
          style={{position:"absolute", bottom:"5%", right:"3%", width:"27%", height:"40%"}}
          onClick={() => setActiveSection("edge_case")} />

                {/* Center */}
        <div style={{
          position:"absolute", top:"50%", left:"50%",
          transform:"translate(-50%,-50%)",
          display:"flex", flexDirection:"column",
          alignItems:"center", gap:12
        }}>
          {/* Cloud goes above cube — handled inside WaterCube */}
          <WaterCube fillPercent={fillPct} showCloud={allDone} onClick={() => setShowUpload(true)} />
          {activeDeck && (
            <button onClick={() => onStudy(activeDeck.id)} style={{
              width:200, padding:"10px 16px", borderRadius:16,
              background: activeDeck.due_count > 0 ? "#1a1a2e" : "#89F5BF",
              color: activeDeck.due_count > 0 ? "white" : "#1a1a2e",
              fontFamily:"Fredoka One", fontSize:"1.1rem",
              border:"none", cursor:"pointer", boxShadow:"0 5px 0 rgba(0,0,0,0.15)"
            }}>
              {activeDeck.due_count > 0 ? `🚀 Study Now (${activeDeck.due_count} due!)` : "✅ All caught up!"}
            </button>
          )}
        </div>

                {/* Pills LEFT side — 2 pills */}
        {activeDeck && (
          <div style={{
            position:"absolute", left:"32%", top:"50%",
            transform:"translateY(-50%)",
            display:"flex", flexDirection:"column", gap:8
          }}>
            {[
              {label:`🆕 ${counts[0]||0}`, bg:"#f0f0f5"},
              {label:`📚 ${counts[1]||0}`, bg:"#DBEEFF"},
            ].map((p,i) => (
              <span key={i} style={{padding:"6px 14px", borderRadius:999,
                background:p.bg, fontSize:13, fontWeight:800, color:"#333",
                boxShadow:"0 2px 8px rgba(0,0,0,0.08)"}}>{p.label}</span>
            ))}
          </div>
        )}

        {/* Pills RIGHT side — 2 pills */}
        {activeDeck && (
          <div style={{
            position:"absolute", right:"32%", top:"50%",
            transform:"translateY(-50%)",
            display:"flex", flexDirection:"column", gap:8
          }}>
            {[
              {label:`🔄 ${counts[2]||0}`, bg:"#FFF3CD"},
              {label:`⭐ ${mastered}`,      bg:"#D4FCEB"},
            ].map((p,i) => (
              <span key={i} style={{padding:"6px 14px", borderRadius:999,
                background:p.bg, fontSize:13, fontWeight:800, color:"#333",
                boxShadow:"0 2px 8px rgba(0,0,0,0.08)"}}>{p.label}</span>
            ))}
          </div>
        )}
        {/* Worked Examples button */}
        <div style={{position:"absolute", right:"3%", top:"50%", transform:"translateY(-50%)",
          display:"flex", flexDirection:"column", alignItems:"center", gap:8}}>
          <button className="circle-btn" onClick={() => setShowWorked(true)}>
            <span style={{fontSize:"1.3rem"}}>▶▶</span>
          </button>
          <span style={{fontSize:11, fontWeight:800, color:"#888", textAlign:"center", lineHeight:1.3}}>
            Worked<br/>Examples
          </span>
        </div>
      </div>

      {/* Section popup */}
      {activeSection && (
        <div className="blur-overlay" onClick={() => setActiveSection(null)}>
          <div className="card-panel bounce-in" onClick={e => e.stopPropagation()}>
            <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:16}}>
              <div>
                <h2 style={{fontFamily:"Fredoka One", fontSize:"1.4rem"}}>
                  {SECTIONS.find(s=>s.key===activeSection)?.emoji}{" "}
                  {SECTIONS.find(s=>s.key===activeSection)?.label}
                </h2>
                <p style={{fontSize:12, color:"#aaa", fontWeight:700}}>
                  {sectionCards(activeSection).length} cards
                </p>
              </div>
              <button onClick={() => setActiveSection(null)}
                style={{background:"none", border:"none", fontSize:"1.4rem", cursor:"pointer"}}>✕</button>
            </div>
            {sectionCards(activeSection).length === 0 ? (
              <div style={{textAlign:"center", padding:"2rem", color:"#aaa"}}>
                <div style={{fontSize:"3rem"}}>🌱</div>
                <p style={{fontWeight:700}}>No cards yet — upload a PDF!</p>
              </div>
            ) : (
              <div style={{display:"flex", flexDirection:"column", gap:10}}>
                {sectionCards(activeSection).map(card => (
                  <MiniCard key={card.id} card={card}
                    color={SECTIONS.find(s=>s.key===activeSection)?.color} />
                ))}
              </div>
            )}
            {activeDeck && sectionCards(activeSection).length > 0 && (
              <button onClick={() => { setActiveSection(null); onStudy(activeDeck.id); }}
                style={{width:"100%", marginTop:16, padding:"12px", borderRadius:14,
                  background:"#1a1a2e", color:"white", fontFamily:"Fredoka One",
                  fontSize:"1.1rem", border:"none", cursor:"pointer"}}>
                🚀 Study These Cards
              </button>
            )}
          </div>
        </div>
      )}

      <WorkedExamplesPage
        show={showWorked}
        cards={workedCards}
        onClose={() => setShowWorked(false)}
        onStudy={() => { setShowWorked(false); activeDeck && onStudy(activeDeck.id); }}
      />

      <UploadModal
        show={showUpload}
        uploading={uploading}
        uploadMsg={uploadMsg}
        selectedFile={selectedFile}
        deckName={deckName}
        onDeckNameChange={setDeckName}
        onFileSelect={setSelectedFile}
        onUpload={handleUpload}
        onClose={() => setShowUpload(false)}
      />
    </div>
  );
}