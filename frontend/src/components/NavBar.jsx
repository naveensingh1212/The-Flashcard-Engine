export default function NavBar({ decks, activeDeck, onDeckChange, onDelete, onNewDeck }) {
  return (
    <nav style={{
      display:"flex", alignItems:"center", justifyContent:"space-between",
      padding:"12px 32px", background:"white",
      borderBottom:"1px solid #eee", position:"relative", zIndex:10
    }}>
      <div style={{display:"flex", alignItems:"center", gap:10}}>
        <span style={{fontSize:"1.5rem"}}>🃏</span>
        <span style={{fontFamily:"Fredoka One", fontSize:"1.3rem", color:"#1a1a2e"}}>
          Flashcard Engine
        </span>
      </div>
      <div style={{display:"flex", alignItems:"center", gap:8}}>
        {decks.length > 0 && (
          <div style={{display:"flex", alignItems:"center", gap:4,
            border:"2px solid #eee", borderRadius:12, overflow:"hidden"}}>
            <select
              style={{padding:"8px 14px", border:"none",
                fontFamily:"Nunito", fontWeight:700, fontSize:14,
                outline:"none", background:"white"}}
              value={activeDeck?.id || ""}
              onChange={e => onDeckChange(e.target.value)}
            >
              {decks.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
            {activeDeck && (
              <button
                onClick={onDelete}
                title={`Delete "${activeDeck.name}"`}
                style={{
                  width:34, height:34, border:"none",
                  borderLeft:"2px solid #eee",
                  background:"#fff5f5", color:"#cc0000",
                  cursor:"pointer", fontSize:"0.9rem",
                  display:"flex", alignItems:"center", justifyContent:"center"
                }}
              >🗑</button>
            )}
          </div>
        )}
        <button
          onClick={onNewDeck}
          style={{
            padding:"8px 20px", borderRadius:12,
            background:"#FFE94A", color:"#1a1a2e",
            fontFamily:"Fredoka One", fontSize:"1rem",
            border:"none", cursor:"pointer",
            boxShadow:"0 4px 0 #c8b800"
          }}
        >+ New Deck</button>
      </div>
    </nav>
  );
}