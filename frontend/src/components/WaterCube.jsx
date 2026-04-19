import { useEffect, useRef } from "react";

export default function WaterCube({ fillPercent = 0, showCloud = false, onClick }) {
  const canvasRef = useRef(null);
  const animRef   = useRef(null);
  const waveOff   = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    // Fixed pixel size — do NOT let CSS scale it
    canvas.width  = 200;
    canvas.height = 150;

    const fx = 10, fy = 28, fw = 140, fh = 90;
    const dx = 40, dy = -25;

    function draw() {
      ctx.clearRect(0, 0, 200, 150);

      // Back face
      ctx.beginPath();
      ctx.moveTo(fx+dx,fy+dy); ctx.lineTo(fx+fw+dx,fy+dy);
      ctx.lineTo(fx+fw+dx,fy+fh+dy); ctx.lineTo(fx+dx,fy+fh+dy);
      ctx.closePath();
      ctx.fillStyle="rgba(255,240,130,0.18)"; ctx.fill();
      ctx.strokeStyle="rgba(180,130,0,0.2)"; ctx.lineWidth=0.8; ctx.stroke();

      // Right face
      ctx.beginPath();
      ctx.moveTo(fx+fw,fy); ctx.lineTo(fx+fw+dx,fy+dy);
      ctx.lineTo(fx+fw+dx,fy+fh+dy); ctx.lineTo(fx+fw,fy+fh);
      ctx.closePath();
      ctx.fillStyle="#EDB830"; ctx.fill();
      ctx.strokeStyle="rgba(150,90,0,0.35)"; ctx.lineWidth=0.8; ctx.stroke();

      // Top face
      ctx.beginPath();
      ctx.moveTo(fx,fy); ctx.lineTo(fx+dx,fy+dy);
      ctx.lineTo(fx+fw+dx,fy+dy); ctx.lineTo(fx+fw,fy);
      ctx.closePath();
      ctx.fillStyle="#FFF3A0"; ctx.fill();
      ctx.strokeStyle="rgba(150,100,0,0.3)"; ctx.lineWidth=0.8; ctx.stroke();

      // Water
      const clamp = Math.max(0, Math.min(100, fillPercent));
      const waterH = (fh * clamp) / 100;
      const waterY = fy + fh - waterH;

      if (waterH > 1) {
        ctx.save();
        ctx.beginPath(); ctx.rect(fx,fy,fw,fh); ctx.clip();
        ctx.beginPath(); ctx.moveTo(fx, waterY+2);
        for (let x=0; x<=fw; x++) {
          const w = Math.sin((x/30)*Math.PI*2+waveOff.current)*3
                  + Math.sin((x/18)*Math.PI*2+waveOff.current*1.6)*1.5;
          ctx.lineTo(fx+x, waterY+w);
        }
        ctx.lineTo(fx+fw,fy+fh); ctx.lineTo(fx,fy+fh); ctx.closePath();
        const g = ctx.createLinearGradient(0,waterY,0,fy+fh);
        g.addColorStop(0,"rgba(120,220,255,0.88)");
        g.addColorStop(1,"rgba(20,120,210,0.95)");
        ctx.fillStyle=g; ctx.fill();
        // shimmer
        ctx.beginPath();
        ctx.moveTo(fx+8,waterY+1);
        ctx.bezierCurveTo(fx+32,waterY-2,fx+68,waterY+3,fx+fw-8,waterY+1);
        ctx.strokeStyle="rgba(255,255,255,0.55)"; ctx.lineWidth=1.2; ctx.stroke();
        ctx.restore();
      }

      // Front face
      ctx.beginPath(); ctx.rect(fx,fy,fw,fh);
      ctx.fillStyle="rgba(255,238,120,0.28)"; ctx.fill();
      ctx.strokeStyle="#C89A00"; ctx.lineWidth=1.6; ctx.stroke();

      waveOff.current+=0.05;
      animRef.current=requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(animRef.current);
  }, [fillPercent]);

  return (
    <div style={{position:"relative", userSelect:"none"}}>
      {showCloud && (
        <div style={{
          position:"absolute", top:-72, left:"50%",
          transform:"translateX(-50%)",
          animation:"cloudPop 0.5s cubic-bezier(0.34,1.56,0.64,1) both",
          zIndex:10, pointerEvents:"none"
        }}>
          <svg width="180" height="60" viewBox="0 0 180 60">
            <ellipse cx="90" cy="30" rx="74" ry="22" fill="white" stroke="#e8e8e8" strokeWidth="1.5"/>
            <ellipse cx="44" cy="36" rx="26" ry="16" fill="white" stroke="#e8e8e8" strokeWidth="1.5"/>
            <ellipse cx="136" cy="36" rx="26" ry="16" fill="white" stroke="#e8e8e8" strokeWidth="1.5"/>
            <ellipse cx="90" cy="18" rx="28" ry="18" fill="white" stroke="#e8e8e8" strokeWidth="1.5"/>
            <polygon points="84,50 96,50 90,60" fill="white" stroke="#e8e8e8" strokeWidth="1"/>
            <text x="90" y="28" textAnchor="middle" fontSize="10" fontFamily="Nunito,sans-serif" fontWeight="800" fill="#1a1a2e">🎉 Amazing! Drink water!</text>
            <text x="90" y="43" textAnchor="middle" fontSize="9" fontFamily="Nunito,sans-serif" fontWeight="700" fill="#aaa">All topics mastered!</text>
          </svg>
        </div>
      )}

      {/* Fixed size wrapper — 200px wide, no stretching */}
      <div
        onClick={onClick}
        style={{
          width:200, cursor:"pointer",
          filter:"drop-shadow(0 6px 16px rgba(200,160,0,0.22))",
          transition:"filter 0.2s, transform 0.2s",
          animation:"cubeFloat 3.5s ease-in-out infinite"
        }}
        onMouseOver={e=>e.currentTarget.style.filter="drop-shadow(0 10px 24px rgba(200,160,0,0.35))"}
        onMouseOut={e=>e.currentTarget.style.filter="drop-shadow(0 6px 16px rgba(200,160,0,0.22))"}
      >
        <div style={{position:"relative", width:200, height:150, display:"inline-block"}}>
          <canvas ref={canvasRef} style={{display:"block", width:200, height:150}} />
          
          {/* SVG Text Overlay */}
          <svg 
            width="200" 
            height="150" 
            viewBox="0 0 200 150" 
            style={{position:"absolute", top:0, left:0, pointerEvents:"none"}}
          >
            <defs>
              <filter id="textShadowUpload" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="1" dy="2" stdDeviation="1.5" floodOpacity="0.2" />
              </filter>
              <filter id="textShadowPercent" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="2" dy="3" stdDeviation="2" floodOpacity="0.15" />
              </filter>
            </defs>
            
            {fillPercent === 0 ? (
              <>
                {/* Emoji */}
                <text x="80" y="61" textAnchor="middle" fontSize="18" fill="#1a1a2e">
                  📄
                </text>
                {/* UPLOAD PDF */}
                <text 
                  x="80" 
                  y="77" 
                  textAnchor="middle" 
                  fontSize="14" 
                  fontFamily="Fredoka One, cursive"
                  fontWeight="bold"
                  fill="#1a1a2e"
                  filter="url(#textShadowUpload)"
                >
                  UPLOAD PDF
                </text>
                {/* Subtitle */}
                <text 
                  x="80" 
                  y="91" 
                  textAnchor="middle" 
                  fontSize="9" 
                  fontFamily="Nunito, sans-serif"
                  fontWeight="800"
                  fill="#C89A00"
                >
                  drop PDF → get flashcards
                </text>
              </>
            ) : (
              /* Percentage */
              <text 
                x="80" 
                y="78" 
                textAnchor="middle" 
                fontSize={Math.max(0, Math.min(100, fillPercent)) === 100 ? "22" : "20"}
                fontFamily="Fredoka One, cursive"
                fontWeight="900"
                fill={Math.max(0, Math.min(100, fillPercent)) > 55 ? "#ffffff" : "#1a1a2e"}
                filter="url(#textShadowPercent)"
              >
                {Math.round(Math.max(0, Math.min(100, fillPercent)))}%
              </text>
            )}
          </svg>
        </div>
      </div>

      {/* Tiny progress bar - HIDDEN */}
      <div style={{width:200, marginTop:5, display:"none", alignItems:"center", gap:5}}>
        <div style={{flex:1, height:4, background:"#eee", borderRadius:999, overflow:"hidden"}}>
          <div style={{
            height:"100%", borderRadius:999,
            width:`${Math.min(100,Math.max(0,fillPercent))}%`,
            background:"linear-gradient(90deg,#60CFFF,#2080FF)",
            transition:"width 0.9s cubic-bezier(0.34,1.2,0.64,1)"
          }}/>
        </div>
        <span style={{fontSize:9, fontWeight:800, color:"#ccc"}}>{Math.round(fillPercent)}%</span>
      </div>

      <style>{`
        @keyframes cubeFloat {
          0%,100%{transform:translateY(0px)}
          50%{transform:translateY(-5px)}
        }
      `}</style>
    </div>
  );
}