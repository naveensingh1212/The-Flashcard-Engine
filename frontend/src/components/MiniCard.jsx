import { useState } from "react";

export default function MiniCard({ card, color }) {
  const [flipped, setFlipped] = useState(false);
  return (
    <div className="flip-card" style={{height:76, cursor:"pointer"}}
      onClick={() => setFlipped(f => !f)}>
      <div className={`flip-inner ${flipped ? "flipped" : ""}`} style={{height:76}}>
        <div className="flip-front" style={{
          position:"absolute", inset:0, background:color||"white",
          borderRadius:14, padding:"10px 14px", display:"flex", alignItems:"center",
          border:color==="white"?"2px solid #eee":"none"
        }}>
          <p style={{fontWeight:700, fontSize:13, color:"#1a1a2e"}}>{card.front}</p>
        </div>
        <div className="flip-back" style={{
          position:"absolute", inset:0, background:"white",
          borderRadius:14, padding:"10px 14px", display:"flex", alignItems:"center",
          border:"2px solid #eee"
        }}>
          <p style={{fontSize:12, color:"#555"}}>{card.back}</p>
        </div>
      </div>
    </div>
  );
}