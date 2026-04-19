import { useState, useEffect } from "react";
import { api } from "../api/client.js";

const QUALITY_BTNS = [
  { q: 1, label: "Again 😬",  bg: "#FFD6D6", shadow: "#ffaaaa" },
  { q: 3, label: "Hard 😅",   bg: "#FFE8B0", shadow: "#ffd07a" },
  { q: 4, label: "Good 😊",   bg: "#C8F7DC", shadow: "#89F5BF" },
  { q: 5, label: "Easy 🌟",   bg: "#B8E8FF", shadow: "#99E5FF" },
];

const MASTERY = ["🆕 New", "📚 Learning", "🔄 Reviewing", "⭐ Mastered"];
const MASTERY_COLOR = ["#aaa","#99E5FF","#FFC2A3","#89F5BF"];

export default function Study({ deckId, onBack }) {
  const [cards, setCards]     = useState([]);
  const [index, setIndex]     = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [done, setDone]       = useState(false);
  const [deckName, setDeckName] = useState("");
  const [reviewed, setReviewed] = useState(0);
  const [loading, setLoading] = useState(true);
  const [stats, setStats]     = useState({});
  const [checkedCards, setCheckedCards] = useState(new Set());

  useEffect(() => {
    (async () => {
      const [session, deckData] = await Promise.all([
        api.getStudySession(deckId, 30),
        api.getDeck(deckId),
      ]);
      setCards(session.cards);
      setStats({ due: session.total_due, newC: session.total_new, total: session.total_cards });
      setDeckName(deckData.deck.name);
      if (session.cards.length === 0) setDone(true);
      setLoading(false);
    })();
  }, [deckId]);

  const card    = cards[index];
  const checkedCount = checkedCards.size;
  const progress = cards.length > 0 ? Math.round((checkedCount / cards.length) * 100) : 0;

  const handleCheckCard = async () => {
    const newChecked = new Set(checkedCards);
    if (newChecked.has(card.id)) {
      newChecked.delete(card.id);
    } else {
      // When checked, auto-submit as "Easy" (quality 5)
      newChecked.add(card.id);
      await api.reviewCard(card.id, 5);
      setReviewed(r => r + 1);
    }
    setCheckedCards(newChecked);
  };

  const handleQuality = async (q) => {
    await api.reviewCard(card.id, q);
    setReviewed(r => r + 1);
    setFlipped(false);
    setShowHint(false);
    if (index + 1 >= cards.length) setDone(true);
    else setIndex(i => i + 1);
  };

  if (loading) return (
    <div className="min-h-screen grid-bg flex items-center justify-center">
      <div style={{fontFamily:'Fredoka One', fontSize:'1.5rem', color:'#888'}}>
        Loading your cards... 📚
      </div>
    </div>
  );

  if (done) return (
    <div className="min-h-screen grid-bg flex items-center justify-center">
      <div className="card-panel bounce-in text-center" style={{maxWidth:400}}>
        <div style={{fontSize:'4rem', marginBottom:'1rem'}}>🎉</div>
        <h2 style={{fontFamily:'Fredoka One', fontSize:'2rem', marginBottom:'0.5rem'}}>
          Session Complete!
        </h2>
        <p style={{fontWeight:700, color:'#888', marginBottom:'0.5rem'}}>
          You reviewed <strong style={{color:'#1a1a2e'}}>{reviewed} cards</strong> today!
        </p>
        <p style={{fontSize:'13px', color:'#aaa', marginBottom:'2rem'}}>
          SM-2 has scheduled your next reviews. Come back tomorrow! 🌙
        </p>
        <div style={{
          display:'grid', gridTemplateColumns:'1fr 1fr 1fr',
          gap:'8px', marginBottom:'1.5rem'
        }}>
          {[
            {label:'Reviewed', val: reviewed, color:'#FFC2A3'},
            {label:'Due Left', val: Math.max(0,stats.due-reviewed), color:'#99E5FF'},
            {label:'Total', val: stats.total, color:'#89F5BF'},
          ].map(s => (
            <div key={s.label} style={{background:s.color, borderRadius:16, padding:'12px 8px', textAlign:'center'}}>
              <div style={{fontFamily:'Fredoka One', fontSize:'1.5rem'}}>{s.val}</div>
              <div style={{fontSize:'11px', fontWeight:800, opacity:0.7}}>{s.label}</div>
            </div>
          ))}
        </div>
        <button
          onClick={onBack}
          style={{
            width:'100%', padding:'14px', borderRadius:16,
            background:'#1a1a2e', color:'white',
            fontFamily:'Fredoka One', fontSize:'1.2rem',
            border:'none', cursor:'pointer'
          }}
        >
          ← Back to Decks
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen grid-bg">
      {/* Top bar */}
      <div style={{
        background:'white', borderBottom:'1px solid #eee',
        padding:'12px 32px', display:'flex',
        alignItems:'center', justifyContent:'space-between'
      }}>
        <button
          onClick={onBack}
          style={{fontFamily:'Nunito', fontWeight:800, color:'#888',
            background:'none', border:'none', cursor:'pointer', fontSize:'14px'}}
        >
          ← Back
        </button>
        <div style={{textAlign:'center'}}>
          <div style={{fontFamily:'Fredoka One', fontSize:'1.1rem'}}>{deckName}</div>
          <div style={{fontSize:'12px', color:'#aaa', fontWeight:700}}>
            Learned: {checkedCount} / {cards.length} · {stats.due} due
          </div>
        </div>
        <div style={{fontFamily:'Fredoka One', fontSize:'1.1rem', color:'#89F5BF', fontWeight:800}}>
          {progress}%
        </div>
      </div>

      {/* Progress bar */}
      <div style={{padding:'0 32px'}}>
        <div className="prog-track" style={{borderRadius:0}}>
          <div className="prog-fill" style={{width:`${progress}%`}} />
        </div>
      </div>

      {/* Card area */}
      <div style={{
        maxWidth:600, margin:'0 auto', padding:'40px 24px',
        display:'flex', flexDirection:'column', alignItems:'center', gap:'24px'
      }}>
        {/* Mastery + difficulty badges */}
        <div style={{display:'flex', gap:'8px'}}>
          <span className="pill" style={{background: MASTERY_COLOR[card.mastery], color:'#1a1a2e'}}>
            {MASTERY[card.mastery]}
          </span>
          <span className="pill" style={{background:'#f0f0f5', color:'#888'}}>
            {card.difficulty}
          </span>
          <span className="pill" style={{background:'#f0f0f5', color:'#888'}}>
            {card.category}
          </span>
        </div>

        {/* Flip card */}
        <div
          className="flip-card"
          style={{width:'100%', height:260, cursor: flipped ? 'default' : 'pointer'}}
          onClick={() => !flipped && setFlipped(true)}
        >
          <div className={`flip-inner ${flipped?'flipped':''}`} style={{height:260}}>
            {/* Front */}
            <div className="flip-front" style={{
              position:'absolute', inset:0,
              background:'white',
              boxShadow:'0 12px 40px rgba(0,0,0,0.1)',
              display:'flex', flexDirection:'column',
              justifyContent:'space-between', padding:'28px'
            }}>
              {/* Checkbox at top */}
              <div style={{display:'flex', justifyContent:'flex-end', marginBottom:'12px'}}>
                <label style={{display:'flex', alignItems:'center', gap:'8px', cursor:'pointer', fontWeight:800, fontSize:'14px'}}>
                  <input
                    type="checkbox"
                    checked={checkedCards.has(card.id)}
                    onChange={handleCheckCard}
                    style={{width:'20px', height:'20px', cursor:'pointer'}}
                  />
                  <span style={{color:'#aaa'}}>Learned</span>
                </label>
              </div>
              
              <div style={{
                flex:1, display:'flex', alignItems:'center', justifyContent:'center'
              }}>
                <p style={{
                  fontFamily:'Nunito', fontWeight:800, fontSize:'1.2rem',
                  textAlign:'center', lineHeight:1.5, color:'#1a1a2e'
                }}>
                  {card.front}
                </p>
              </div>
              <div style={{textAlign:'center'}}>
                {showHint ? (
                  <p style={{fontSize:'13px', color:'#aaa', fontStyle:'italic', fontWeight:700}}>
                    💡 {card.hint}
                  </p>
                ) : card.hint && (
                  <button
                    onClick={e=>{e.stopPropagation();setShowHint(true)}}
                    style={{fontSize:'12px', color:'#aaa', fontWeight:800,
                      background:'none', border:'none', cursor:'pointer', textDecoration:'underline'}}
                  >
                    Show hint
                  </button>
                )}
                {!flipped && (
                  <p style={{fontSize:'12px', color:'#ccc', marginTop:4, fontWeight:700}}>
                    👆 Tap to reveal answer
                  </p>
                )}
              </div>
            </div>

            {/* Back */}
            <div className="flip-back" style={{
              position:'absolute', inset:0,
              background:'linear-gradient(135deg, #89F5BF22, #99E5FF22)',
              boxShadow:'0 12px 40px rgba(0,0,0,0.1)',
              display:'flex', flexDirection:'column',
              justifyContent:'center', alignItems:'center', padding:'28px'
            }}>
              <p style={{
                fontFamily:'Nunito', fontWeight:700, fontSize:'1.1rem',
                textAlign:'center', lineHeight:1.6, color:'#1a1a2e'
              }}>
                {card.back}
              </p>
            </div>
          </div>
        </div>

        {/* Quality buttons */}
        {flipped ? (
          <div style={{width:'100%'}}>
            <p style={{textAlign:'center', fontWeight:800, fontSize:'13px',
              color:'#aaa', marginBottom:'12px'}}>
              How well did you remember?
            </p>
            <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gap:'10px'}}>
              {QUALITY_BTNS.map(({q, label, bg, shadow}) => (
                <button
                  key={q}
                  className="q-btn"
                  style={{background:bg, boxShadow:`0 5px 0 ${shadow}`}}
                  onClick={() => handleQuality(q)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <button
            onClick={() => setFlipped(true)}
            style={{
              padding:'14px 48px', borderRadius:16,
              background:'#1a1a2e', color:'white',
              fontFamily:'Fredoka One', fontSize:'1.2rem',
              border:'none', cursor:'pointer',
              boxShadow:'0 6px 0 rgba(0,0,0,0.3)',
              transition:'transform 0.15s'
            }}
            onMouseOver={e=>e.target.style.transform='translateY(-3px)'}
            onMouseOut={e=>e.target.style.transform='translateY(0)'}
          >
            Reveal Answer ✨
          </button>
        )}
      </div>
    </div>
  );
}