"use client"

import { useEffect, useRef, useState } from "react"

export default function WebcamFeed() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isActive, setIsActive] = useState(false)

  useEffect(() => {
    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 320 }, height: { ideal: 240 } },
        })
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          setIsActive(true)
        }
      } catch (err) {
        console.error("Webcam access denied:", err)
        setIsActive(false)
      }
    }

    startWebcam()

    return () => {
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks()
        tracks.forEach((track) => track.stop())
      }
    }
  }, [])

  return (
    <div className="relative w-64 h-48 rounded-xl overflow-hidden border-4 border-accent shadow-2xl bg-black pointer-events-auto">
      <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
      {!isActive && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80">
          <p className="text-white text-xs text-center px-2">Webcam not available</p>
        </div>
      )}
    </div>
  )
}
