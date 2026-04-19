import { useRef } from "react";
import { useState } from "react";
export default function UploadModal({
  show, uploading, uploadMsg, selectedFile,
  deckName, onDeckNameChange, onFileSelect,
  onUpload, onClose
}) {
  const fileRef = useRef();
  const [dragging, setDragging] = useState(false); // needs import

  if (!show) return null;

  return (
    <div className="blur-overlay" onClick={() => !uploading && onClose()}>
      <div className="card-panel bounce-in" onClick={e => e.stopPropagation()}>
        <h2 style={{fontFamily:"Fredoka One", fontSize:"1.5rem", marginBottom:"1rem"}}>
          📄 Upload a PDF
        </h2>
        <div
          onDragOver={e=>{e.preventDefault();setDragging(true)}}
          onDragLeave={()=>setDragging(false)}
          onDrop={e=>{e.preventDefault();setDragging(false);onFileSelect(e.dataTransfer.files[0])}}
          onClick={() => fileRef.current.click()}
          style={{
            border:`3px dashed ${dragging?"#FFE94A":"#ddd"}`,
            borderRadius:20, padding:"2rem", textAlign:"center",
            cursor:"pointer", marginBottom:"1rem",
            background:dragging?"#FFFBE6":"#fafafa", transition:"all 0.2s"
          }}
        >
          <input ref={fileRef} type="file" accept=".pdf" style={{display:"none"}}
            onChange={e => onFileSelect(e.target.files[0])} />
          <div style={{fontSize:"3rem"}}>📚</div>
          {selectedFile
            ? <p style={{fontWeight:800}}>{selectedFile.name}</p>
            : <p style={{fontWeight:700, color:"#aaa"}}>Drop PDF here or click to browse</p>}
        </div>
        <input type="text" placeholder="Deck name (optional)" value={deckName}
          onChange={e => onDeckNameChange(e.target.value)}
          style={{
            width:"100%", padding:"12px 16px", borderRadius:14,
            border:"2px solid #eee", fontFamily:"Nunito", fontSize:14,
            fontWeight:700, outline:"none", marginBottom:"1rem"
          }} />
        {uploadMsg && (
          <div style={{
            padding:"12px", borderRadius:14, marginBottom:"1rem",
            background:"#FFFBE6", fontWeight:700, fontSize:14, textAlign:"center"
          }}>{uploadMsg}</div>
        )}
        <button onClick={onUpload} disabled={!selectedFile || uploading}
          style={{
            width:"100%", padding:"14px", borderRadius:16,
            background:uploading?"#ddd":"#FFE94A",
            color:"#1a1a2e", fontFamily:"Fredoka One", fontSize:"1.2rem",
            border:"none", cursor:uploading?"not-allowed":"pointer",
            boxShadow:uploading?"none":"0 6px 0 #c8b800"
          }}
        >{uploading ? "Generating Cards... ⚙️" : "Generate Flashcards! ✨"}</button>
      </div>
    </div>
  );
}