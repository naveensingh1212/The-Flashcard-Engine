import MiniCard from "./MiniCard.jsx";

const WORKED_SECTIONS = [
  { label:"Step-by-Step", emoji:"📝", filter: c => c.difficulty === "hard" },
  { label:"Examples",     emoji:"💡", filter: c => c.category === "example" || c.category === "application" },
  { label:"Quick Tips",   emoji:"⚡", filter: c => c.difficulty === "easy" },
  { label:"Common Mistakes", emoji:"🚫", filter: c => c.category === "edge_case" },
];
const colors = ["#FFC2A3","#99E5FF","#FFC2FA","#89F5BF"];

export default function WorkedExamplesPage({ show, cards, onClose, onStudy }) {
  return (
    <div style={{
      position:"fixed", inset:0, zIndex:50,
      transform: show ? "translateX(0)" : "translateX(100%)",
      transition:"transform 0.4s cubic-bezier(0.4,0,0.2,1)",
      background:"white", overflowY:"auto"
    }}>
      <div style={{
        padding:"16px 32px", borderBottom:"2px solid #eee",
        display:"flex", alignItems:"center", justifyContent:"space-between",
        background:"white", position:"sticky", top:0, zIndex:10
      }}>
        <div style={{display:"flex", alignItems:"center", gap:12}}>
          <button onClick={onClose} style={{
            background:"#f0f0f5", border:"none", borderRadius:10,
            padding:"8px 16px", cursor:"pointer",
            fontFamily:"Nunito", fontWeight:800, fontSize:14
          }}>← Back</button>
          <h1 style={{fontFamily:"Fredoka One", fontSize:"1.5rem", color:"#1a1a2e"}}>
            ▶▶ Worked Examples
          </h1>
        </div>
        <button onClick={onStudy} style={{
          padding:"10px 24px", borderRadius:14,
          background:"#1a1a2e", color:"white",
          fontFamily:"Fredoka One", fontSize:"1rem",
          border:"none", cursor:"pointer"
        }}>🚀 Study Now</button>
      </div>
      <div style={{
        display:"grid", gridTemplateColumns:"1fr 1fr",
        gap:24, padding:32, maxWidth:1100, margin:"0 auto"
      }}>
        {WORKED_SECTIONS.map((sec, i) => {
          const sCards = cards.filter(sec.filter);
          return (
            <div key={i} style={{background:colors[i], borderRadius:24, padding:24, minHeight:200}}>
              <div style={{fontFamily:"Fredoka One", fontSize:"1.2rem", marginBottom:14, color:"#1a1a2e"}}>
                {sec.emoji} {sec.label}
                <span style={{marginLeft:8, fontSize:12, fontWeight:800,
                  background:"rgba(0,0,0,0.1)", padding:"3px 10px",
                  borderRadius:999, color:"#555"}}>{sCards.length}</span>
              </div>
              {sCards.length === 0 ? (
                <p style={{color:"rgba(0,0,0,0.4)", fontWeight:700, fontSize:13}}>No cards here yet</p>
              ) : (
                <div style={{display:"flex", flexDirection:"column", gap:8}}>
                  {sCards.slice(0,3).map(card => (
                    <MiniCard key={card.id} card={card} color="white" />
                  ))}
                  {sCards.length > 3 && (
                    <p style={{fontSize:12, fontWeight:800,
                      color:"rgba(0,0,0,0.5)", textAlign:"center"}}>
                      +{sCards.length-3} more
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}