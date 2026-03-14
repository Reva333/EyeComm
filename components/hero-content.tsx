"use client"
import { useState } from "react"

export default function HeroContent() {
  const [starting, setStarting] = useState(false)
  const [showKeyboard, setShowKeyboard] = useState(false)
  const start = async () => {
    try {
      setStarting(true)
      window.location.href = "/keyboard"
    } catch (e) {
      console.error("Failed to start:", e)
    } finally {
      setTimeout(() => setStarting(false), 1000)
    }
  }

  return (
    <main id="start" className="relative z-20 flex min-h-screen items-center justify-center px-6">
      <div className="text-center max-w-3xl">
        <div
          className="inline-flex items-center px-4 py-1.5 rounded-full bg-white/5 backdrop-blur-sm mb-6 relative"
          style={{
            filter: "url(#glass-effect)",
          }}
        >
          <div className="absolute top-0 left-1 right-1 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent rounded-full" />
          <span className="text-white/90 text-sm font-light relative z-10">Gaze.Feel.Express</span>
        </div>

        {/* Main Heading */}
        <h1 className="text-6xl md:text-7xl tracking-tight font-light text-white mb-6">
          <span className="font-medium italic instrument">EyeComm</span>
          <br />
          <span className="font-light tracking-tight text-white"></span>
        </h1>

        {/* Description */}
        <p className="text-sm md:text-base font-light text-white/70 mb-6 leading-relaxed">Speak with your eyes</p>

        {/* Buttons */}
        <div className="flex items-center gap-5 flex-wrap justify-center">
          <a
            href="#features"
            className="px-10 py-4 rounded-full bg-transparent border border-white/30 text-white font-normal text-sm transition-all duration-200 hover:bg-white/10 hover:border-white/50"
          >
            Features
          </a>
          <button
            onClick={start}
            className="px-10 py-4 rounded-full bg-white text-black font-normal text-sm transition-all duration-200 hover:bg-white/90"
          >
            {starting ? "Starting..." : "Start"}
          </button>
        </div>
      </div>
    </main>
  )
}
