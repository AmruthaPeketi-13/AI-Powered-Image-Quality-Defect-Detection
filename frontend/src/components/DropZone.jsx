import { useState, useRef } from 'react'

export default function DropZone({ onFile }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  const handleFile = (file) => {
    if (!file) return
    onFile(file)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  return (
    <div
      id="drop-zone"
      className={`drop-zone ${dragging ? 'dragging' : ''}`}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
    >
      <div className="drop-zone-icon">🖼️</div>
      <h2>Drop an image here</h2>
      <p>or click to browse — JPEG, PNG, WebP, BMP · max 10 MB</p>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/bmp"
        onChange={e => handleFile(e.target.files[0])}
        onClick={e => e.stopPropagation()}
      />
    </div>
  )
}
