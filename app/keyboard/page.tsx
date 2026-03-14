"use client"

import { useEffect, useRef, useState } from "react"
import Keyboard from "@/components/keyboard"
import TextDisplay from "@/components/text-display"

export default function Home() {
  // --- basic state (unchanged) ---
  const [text, setText] = useState("")
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<any>(null)

  // --- gaze / UI state ---
  const [dotPos, setDotPos] = useState(() => {
    if (typeof window !== "undefined") return { x: window.innerWidth / 2, y: window.innerHeight / 2 }
    return { x: 0, y: 0 }
  })
  const dotPosRef = useRef<{ x: number; y: number }>(dotPos)

  const [hoverKey, setHoverKey] = useState<string | null>(null)
  const hoverKeyRef = useRef<string | null>(null)

  const [hoverStart, setHoverStart] = useState<number | null>(null)
  const hoverStartRef = useRef<number | null>(null)

  const [progress, setProgress] = useState(0)
  const progressRef = useRef<number>(0)

  // --- refs ---
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const faceMeshRef = useRef<any>(null)
  const rafRef = useRef<number | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const LAVENDER_STROKE = "#C8A2C8"
  const LAVENDER_FILL = "#E6E6FA"

  // keep refs in sync with state (so interval closure uses latest)
  useEffect(() => {
    dotPosRef.current = dotPos
  }, [dotPos])

  useEffect(() => {
    hoverKeyRef.current = hoverKey
  }, [hoverKey])

  useEffect(() => {
    hoverStartRef.current = hoverStart
  }, [hoverStart])

  useEffect(() => {
    progressRef.current = progress
  }, [progress])

  // ---------------- SPEECH SETUP (unchanged) ----------------
  useEffect(() => {
    if (typeof window === "undefined") return
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true
      recognitionRef.current.onstart = () => setIsListening(true)
      recognitionRef.current.onend = () => setIsListening(false)
      recognitionRef.current.onresult = (event: any) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) setText((prev) => prev + transcript + " ")
        }
      }
    }
  }, [])

  const handleKeyPress = (key: string) => {
    if (key === "Backspace") setText((prev) => prev.slice(0, -1))
    else if (key === "Enter") setText((prev) => prev + "\n")
    else if (key === "Space") setText((prev) => prev + " ")
    else if (key === "Clear") setText("")
    else setText((prev) => prev + key)
  }

  const handleSpeak = () => {
    if (!text.trim()) return
    setIsSpeaking(true)
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.onend = () => setIsSpeaking(false)
    window.speechSynthesis.speak(utterance)
  }

  const handleVoiceType = () => {
    if (!recognitionRef.current) return
    if (isListening) recognitionRef.current.stop()
    else recognitionRef.current.start()
  }

  // ---------------- Helper: load script from CDN ----------------
  const loadScript = (src: string, tries = 2, delay = 300) =>
    new Promise<void>((resolve, reject) => {
      const existing = Array.from(document.getElementsByTagName("script")).find((s) => s.src === src)
      if (existing) {
        if ((existing as any).loaded || (existing as any).readyState === "complete") return resolve()
        existing.addEventListener("load", () => resolve())
        existing.addEventListener("error", () => reject(new Error("script load error")))
        return
      }
      const s = document.createElement("script")
      s.src = src
      s.async = true
      s.onload = () => resolve()
      s.onerror = () => {
        if (tries > 0) setTimeout(() => loadScript(src, tries - 1, delay).then(resolve).catch(reject), delay)
        else reject(new Error("script load error"))
      }
      document.body.appendChild(s)
    })

  // ---------------- CAMERA + FaceMesh setup (robust) ----------------
  useEffect(() => {
    if (typeof window === "undefined") return
    let mounted = true

    const log = (...args: any[]) => console.log("[Gaze]", ...args)
    const warn = (...args: any[]) => console.warn("[Gaze]", ...args)
    const error = (...args: any[]) => console.error("[Gaze]", ...args)

    const start = async () => {
      try {
        log("Requesting webcam access...")
        const s = await navigator.mediaDevices.getUserMedia({ video: true })
        if (!mounted) {
          s.getTracks().forEach((t) => t.stop())
          return
        }
        streamRef.current = s

        if (videoRef.current) {
          videoRef.current.srcObject = s
          await videoRef.current.play().catch((e) => warn("video play rejected:", e))
          log("✅ Webcam stream attached")
        }

        // Load FaceMesh UMD from CDN to avoid bundler issues
        await loadScript("https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js")
        log("✅ FaceMesh script loaded")

        // Attempt to find FaceMesh constructor on window
        const WM = (window as any)
        let FaceMeshCtor: any = null

        if (WM.FaceMesh && typeof WM.FaceMesh === "function") FaceMeshCtor = WM.FaceMesh
        else if (WM.FaceMesh && WM.FaceMesh.FaceMesh && typeof WM.FaceMesh.FaceMesh === "function")
          FaceMeshCtor = WM.FaceMesh.FaceMesh
        else if (WM.faceMesh && typeof WM.faceMesh === "function") FaceMeshCtor = WM.faceMesh
        else {
          for (const k of Object.keys(WM)) {
            try {
              if (k.toLowerCase().includes("face") && WM[k] && typeof WM[k] === "function") {
                FaceMeshCtor = WM[k]
                break
              }
            } catch {}
          }
        }

        if (!FaceMeshCtor) throw new Error("FaceMesh constructor not found on window")
        log("FaceMesh constructor found:", FaceMeshCtor.name || "anonymous")

        // instantiate FaceMesh
        // @ts-ignore
        const faceMesh = new FaceMeshCtor({
          locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`,
        })

        faceMesh.setOptions?.({
          maxNumFaces: 1,
          refineLandmarks: true,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        })

        faceMesh.onResults((results: any) => {
          if (!mounted) return
          if (results?.multiFaceLandmarks && results.multiFaceLandmarks[0]) {
            const lm = results.multiFaceLandmarks[0]
            const leftEye = lm[33]
            const rightEye = lm[263]
            if (leftEye && rightEye) {
              // compute normalized center between eyes
              const centerX = (leftEye.x + rightEye.x) / 2
              const centerY = (leftEye.y + rightEye.y) / 2

              // map to screen pixels (keep same mapping as before; change if you need vertical flip)
              const xPx = Math.max(0, Math.min(window.innerWidth, (1 - centerX) * window.innerWidth))
              const yPx = Math.max(0, Math.min(window.innerHeight, centerY * window.innerHeight))

              // update state (and ref via separate effect)
              setDotPos({ x: Math.round(xPx), y: Math.round(yPx) })
            }
          }
        })

        faceMeshRef.current = faceMesh

        // wait until video is ready (stream attached)
        const waitForVideoReady = async () =>
          new Promise<void>((resolve) => {
            const check = () => {
              const v = videoRef.current
              if (!mounted) return resolve()
              if (v && (v.readyState >= 2 || v.srcObject)) return resolve()
              setTimeout(check, 100)
            }
            check()
          })

        await waitForVideoReady()

        // processing loop
        const process = async () => {
          if (!mounted) return
          const v = videoRef.current
          if (v && v.readyState >= 2 && faceMeshRef.current) {
            try {
              await faceMeshRef.current.send({ image: v })
            } catch (e) {
              // ignore transient send errors
            }
          }
          rafRef.current = requestAnimationFrame(process)
        }
        process()
        log("✅ FaceMesh processing started")
      } catch (err) {
        error("Initialization failed:", err)
        // keep camera running even if FaceMesh failed
      }
    }

    start()

    return () => {
      mounted = false
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      try {
        if (faceMeshRef.current && typeof faceMeshRef.current.close === "function") faceMeshRef.current.close()
      } catch {}
      try {
        if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop())
      } catch {}
      faceMeshRef.current = null
      streamRef.current = null
    }
  }, [])

  // ---------------- GAZE HOVER / TIMER (single interval using refs) ----------------
  useEffect(() => {
    // run interval once only; it will read latest dotPos via dotPosRef
    const interval = setInterval(() => {
      // read latest dotPos from ref
      const d = dotPosRef.current
      const x = Math.max(0, Math.min(window.innerWidth - 1, Math.round(d.x)))
      const y = Math.max(0, Math.min(window.innerHeight - 1, Math.round(d.y)))

      const element = document.elementFromPoint(x, y) as HTMLElement | null
      const keyElement = element?.closest("[data-key]") as HTMLElement | null
      const keyLabel = keyElement?.getAttribute("data-key")

      // clear previously set attributes first (so only current key has the attribute)
      document.querySelectorAll("[data-key]").forEach((el) => el.removeAttribute("data-hovered"))

      if (keyLabel && keyElement) {
        // set hovered attribute
        keyElement.setAttribute("data-hovered", "true")

        // if already hovering same key -> update progress
        if (hoverKeyRef.current === keyLabel) {
          const start = hoverStartRef.current ?? Date.now()
          if (!hoverStartRef.current) {
            // ensure state + ref are set
            setHoverStart(start)
            hoverStartRef.current = start
          }
          const elapsed = Date.now() - start
          const p = Math.min(elapsed / 2000, 1)
          setProgress(p)
          progressRef.current = p

          if (elapsed >= 2000) {
            // fire key press (and reset)
            handleKeyPress(keyLabel)
            setHoverStart(null)
            hoverStartRef.current = null
            setProgress(0)
            progressRef.current = 0
            setHoverKey(null)
            hoverKeyRef.current = null
          }
        } else {
          // new hover start
          setHoverKey(keyLabel)
          hoverKeyRef.current = keyLabel
          const now = Date.now()
          setHoverStart(now)
          hoverStartRef.current = now
          setProgress(0)
          progressRef.current = 0
        }
      } else {
        // not hovering any key -> reset
        setHoverKey(null)
        hoverKeyRef.current = null
        setHoverStart(null)
        hoverStartRef.current = null
        setProgress(0)
        progressRef.current = 0
      }
    }, 50)

    return () => clearInterval(interval)
  }, []) // run once

  // small effect so React updates when dotPos changes (not used by interval)
  useEffect(() => {
    // this blank effect ensures React updates things derived from dotPos state
  }, [dotPos])

  // ---------------- RENDER ----------------
  return (
    <main className="w-screen h-screen bg-background text-foreground overflow-hidden flex flex-col relative">
      {/* Webcam Feed */}
      <div className="fixed top-0.6 right-4 z-50">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-48 h-36 rounded-2xl border-4 border-[#C8A2C8] object-cover"
        />
      </div>

      {/* Control Buttons */}
      <div className="fixed top-0.6 left-4 z-40 flex gap-3">
        <button
          onClick={handleVoiceType}
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            isListening ? "bg-destructive text-white animate-pulse" : "bg-secondary text-secondary-foreground hover:bg-muted hover:opacity-90"
          }`}
        >
          {isListening ? "Listening..." : "Voice Type"}
        </button>

        <button
          onClick={handleSpeak}
          disabled={!text.trim() || isSpeaking}
          className="px-6 py-3 bg-accent text-accent-foreground rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
        >
          {isSpeaking ? "Speaking..." : "Read Text"}
        </button>
      </div>

      {/* Text Display */}
      <TextDisplay text={text} />

      {/* On-screen Keyboard */}
      <Keyboard onKeyPress={handleKeyPress} />

      {/* --- Lavender Gaze Circle with Timer Fill --- */}
      <div
        aria-hidden
        style={{
          position: "fixed",
          left: `${dotPos.x}px`,
          top: `${dotPos.y}px`,
          transform: "translate(-50%, -50%)",
          pointerEvents: "none", // important so elementFromPoint hits underlying keys
          zIndex: 9999,
          width: 60,
          height: 60,
        }}
      >
        <svg width="60" height="60" viewBox="0 0 36 36">
          {/* Outer static circle */}
          <circle cx="18" cy="18" r="14" stroke={LAVENDER_STROKE} strokeWidth="2" fill="none" />

          {/* Timer circle (visible progress) */}
          <circle
            cx="18"
            cy="18"
            r="10"
            stroke={LAVENDER_FILL}
            strokeWidth="4"
            fill="none"
            strokeLinecap="round"
            style={{
              strokeDasharray: 2 * Math.PI * 10,
              strokeDashoffset: 2 * Math.PI * 10 * (1 - progress),
              transition: "stroke-dashoffset 0.05s linear",
            }}
          />

          {/* Center dot */}
          <circle cx="18" cy="18" r="4" fill={LAVENDER_FILL} />
        </svg>
      </div>
    </main>
  )
}
