import { useState } from "react";

export default function MiniCard({ card, color }) {
  const [flipped, setFlipped] = useState(false);
  
  const masteryLabel = ["🌱 New", "📚 Learning", "🔄 Reviewing", "⭐ Mastered"][card.mastery] || "🌱 New";
  const masteryColor = ["#f0f0f5", "#DBEEFF", "#FFF3CD", "#D4FCEB"][card.mastery] || "#f0f0f5";

  return (
    <div className="flip-card" style={{height:90, cursor:"pointer"}}
      onClick={() => setFlipped(f => !f)}>
      <div className={`flip-inner ${flipped ? "flipped" : ""}`} style={{height:90}}>
        <div className="flip-front" style={{
          position:"absolute", inset:0, background:color||"white",
          borderRadius:14, padding:"10px 14px", display:"flex", 
          flexDirection:"column", justifyContent:"space-between",
          border:color==="white"?"2px solid #eee":"none"
        }}>
          <p style={{fontWeight:700, fontSize:15, color:"#1a1a2e"}}>{card.front}</p>
          <span style={{
            fontSize:11, fontWeight:800, padding:"2px 8px",
            borderRadius:999, background:masteryColor,
            alignSelf:"flex-start"
          }}>{masteryLabel}</span>
        </div>
        <div className="flip-back" style={{
          position:"absolute", inset:0, background:"white",
          borderRadius:14, padding:"10px 14px", display:"flex", 
          flexDirection:"column", justifyContent:"space-between",
          border:"2px solid #eee"
        }}>
          <p style={{fontSize:14, color:"#555"}}>{card.back}</p>
          <span style={{
            fontSize:11, fontWeight:800, padding:"2px 8px",
            borderRadius:999, background:masteryColor,
            alignSelf:"flex-start"
          }}>{masteryLabel}</span>
        </div>
      </div>
    </div>
  );
}