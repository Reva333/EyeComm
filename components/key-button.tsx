"use client"

import { useState, useEffect, useRef } from "react"

interface KeyButtonProps {
  label: string
  onPress: () => void
  isWide?: boolean
  dataKey?: string
}

export default function KeyButton({ label, onPress, isWide = false, dataKey }: KeyButtonProps) {
  const [progress, setProgress] = useState(0)
  const [isHovering, setIsHovering] = useState(false)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const animationRef = useRef<number | null>(null)
  const rootRef = useRef<HTMLDivElement | null>(null) // 👈 for observing DOM

  // 👇 NEW: observe when your page sets data-hovered="true"
  useEffect(() => {
    if (!rootRef.current) return
    const el = rootRef.current

    const observer = new MutationObserver(() => {
      const active = el.getAttribute("data-hovered") === "true"
      setIsHovering(active)
    })

    observer.observe(el, { attributes: true, attributeFilter: ["data-hovered"] })

    return () => observer.disconnect()
  }, [])

  // same hover logic as before
  useEffect(() => {
    if (!isHovering) {
      setProgress(0)
      if (timerRef.current) clearTimeout(timerRef.current)
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
      return
    }

    const startTime = Date.now()
    const duration = 2000 // ⏱️ make it 2 seconds for gaze

    const animate = () => {
      const elapsed = Date.now() - startTime
      const newProgress = Math.min((elapsed / duration) * 100, 100)
      setProgress(newProgress)

      if (newProgress < 100) {
        animationRef.current = requestAnimationFrame(animate)
      } else {
        onPress()
        setProgress(0)
      }
    }

    animationRef.current = requestAnimationFrame(animate)
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [isHovering, onPress])

  const getDisplayLabel = () => {
    if (label === "Backspace") return "⌫"
    if (label === "Enter") return "ENTER"
    if (label === "Space") return "SPACE"
    if (label === "Clear") return "CLEAR"
    return label
  }

  return (
    <div
      ref={rootRef}                 // 👈 attach ref so we can observe this element
      data-key={dataKey}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      className={`relative flex items-center justify-center rounded-lg font-bold transition-all duration-150 ${
        isWide ? "flex-1 min-w-32 h-20 text-lg" : "flex-1 h-20 text-2xl"
      } ${
        isHovering
          ? "bg-accent text-accent-foreground shadow-2xl scale-110 border-2 border-accent"
          : "bg-card text-foreground hover:bg-secondary border-2 border-primary shadow-lg"
      }`}
    >
      {isHovering && (
        <svg className="absolute inset-0 w-full h-full" style={{ transform: "rotate(-90deg)" }}>
          <circle
            cx="50%"
            cy="50%"
            r="45%"
            fill="none"
            stroke="currentColor"
            strokeWidth="4"
            strokeDasharray={`${2 * Math.PI * 45} ${2 * Math.PI * 45}`}
            strokeDashoffset={`${2 * Math.PI * 45 * (1 - progress / 100)}`}
            className="text-accent-foreground opacity-100 transition-all duration-100"
          />
        </svg>
      )}
      <span className="relative z-10 pointer-events-none">{getDisplayLabel()}</span>
    </div>
  )
}
