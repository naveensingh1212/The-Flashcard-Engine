export default function SectionCard({ section, cards, onClick, style }) {
  const count = cards.length;
  const masteredCount = cards.filter(c => c.mastery === 3).length;
  const pct = count ? Math.round((masteredCount / count) * 100) : 0;

  return (
    <div className="section-card fade-up"
      style={{...style, background:section.color}}
      onClick={onClick}
    >
      <div style={{padding:"1.2rem", height:"100%", display:"flex",
        flexDirection:"column", justifyContent:"space-between"}}>
        <div>
          <div style={{fontSize:"1.8rem", marginBottom:"0.4rem"}}>{section.emoji}</div>
          <h3 style={{fontFamily:"Fredoka One", fontSize:"1.2rem", color:"#1a1a2e"}}>
            {section.label}
          </h3>
        </div>
        <div>
          {count > 0 && (
            <div style={{marginBottom:6}}>
              <div style={{height:6, background:"rgba(0,0,0,0.1)",
                borderRadius:999, overflow:"hidden"}}>
                <div style={{height:"100%", width:`${pct}%`,
                  background:"rgba(0,0,0,0.25)", borderRadius:999,
                  transition:"width 0.5s ease"}} />
              </div>
              <div style={{fontSize:10, fontWeight:800, color:"rgba(0,0,0,0.5)",
                marginTop:3}}>{pct}% mastered</div>
            </div>
          )}
          <div style={{fontWeight:800, fontSize:"1.6rem", color:"#1a1a2e"}}>{count}</div>
          <div style={{fontSize:11, fontWeight:700, color:"rgba(0,0,0,0.45)"}}>
            cards · tap to explore
          </div>
        </div>
      </div>
    </div>
  );
}