"use client"

import Header from "@/components/header"
import HeroContent from "@/components/hero-content"
import PulsingCircle from "@/components/pulsing-circle"
import ShaderBackground from "@/components/shader-background"
import { motion } from "framer-motion"

export default function ShaderShowcase() {
  return (
    <ShaderBackground>
      <Header />
      <HeroContent />
      <PulsingCircle />

      <section id="features" className="relative z-20 mx-auto max-w-6xl px-6 py-28 text-white">
        <div className="mb-12 text-center">
          <motion.h2
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-3xl md:text-5xl font-light tracking-tight text-balance"
          >
            EyeComm Features
          </motion.h2>
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
            className="mx-auto mt-4 h-px w-40 origin-left bg-gradient-to-r from-white/0 via-white/60 to-white/0"
          />
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-4 text-white/70 text-sm md:text-base"
          >
            A fluid, expressive way to communicate—guided by gaze.
          </motion.p>
        </div>

        {/* Feature 1 - left */}
        <motion.div
          className="relative py-10 md:py-12 flex md:justify-end"
          initial={{ opacity: 0, x: -48, y: 12 }}
          whileInView={{ opacity: 1, x: 0, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ type: "spring", stiffness: 120, damping: 18, mass: 0.6 }}
        >
          {/* soft glow accent */}
          <motion.span
            aria-hidden
            className="pointer-events-none absolute -z-10 blur-3xl"
            style={{
              left: "30%",
              top: "20%",
              width: 200,
              height: 200,
              background: "radial-gradient(50% 50% at 50% 50%, rgba(139,92,246,0.25), transparent 70%)",
            }}
            animate={{ y: [-6, 6, -6], x: [-4, 4, -4] }}
            transition={{ duration: 8, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          {/* connector dot */}
          <span className="absolute left-1/2 top-1/2 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/70 shadow-[0_0_20px_rgba(255,255,255,0.4)]" />
          <div className="md:max-w-xl text-right pr-8">
            <h3 className="text-xl md:text-2xl font-medium tracking-tight">Gaze‑to‑Text</h3>
            <div className="ml-auto mt-2 h-px w-24 bg-gradient-to-l from-white/0 via-white/60 to-white/0" />
            <p className="mt-3 text-white/70 text-sm md:text-base leading-relaxed">
              Translate subtle eye movements into accurate text with latency‑aware smoothing for a flowy, natural feel.
            </p>
          </div>
        </motion.div>

        {/* Feature 2 - right */}
        <motion.div
          className="relative py-10 md:py-12 flex md:justify-start"
          initial={{ opacity: 0, x: 48, y: 12 }}
          whileInView={{ opacity: 1, x: 0, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ type: "spring", stiffness: 120, damping: 18, mass: 0.6, delay: 0.05 }}
        >
          <motion.span
            aria-hidden
            className="pointer-events-none absolute -z-10 blur-3xl"
            style={{
              right: "28%",
              top: "35%",
              width: 220,
              height: 220,
              background: "radial-gradient(50% 50% at 50% 50%, rgba(255,255,255,0.16), transparent 70%)",
            }}
            animate={{ y: [4, -4, 4], x: [6, -6, 6] }}
            transition={{ duration: 9, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <span className="absolute left-1/2 top-1/2 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/70 shadow-[0_0_20px_rgba(255,255,255,0.4)]" />
          <div className="md:max-w-xl text-left pl-8">
            <h3 className="text-xl md:text-2xl font-medium tracking-tight">Adaptive Calibration</h3>
            <div className="mt-2 h-px w-24 bg-gradient-to-r from-white/0 via-white/60 to-white/0" />
            <p className="mt-3 text-white/70 text-sm md:text-base leading-relaxed">
              Learns from your gaze patterns over time, adapting sensitivity for comfort and precision.
            </p>
          </div>
        </motion.div>

        {/* Feature 3 - left */}
        <motion.div
          className="relative py-10 md:py-12 flex md:justify-end"
          initial={{ opacity: 0, x: -48, y: 12 }}
          whileInView={{ opacity: 1, x: 0, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ type: "spring", stiffness: 120, damping: 18, mass: 0.6, delay: 0.1 }}
        >
          <motion.span
            aria-hidden
            className="pointer-events-none absolute -z-10 blur-3xl"
            style={{
              left: "25%",
              bottom: "20%",
              width: 220,
              height: 220,
              background: "radial-gradient(50% 50% at 50% 50%, rgba(139,92,246,0.18), transparent 70%)",
            }}
            animate={{ y: [-5, 5, -5], x: [3, -3, 3] }}
            transition={{ duration: 10, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <span className="absolute left-1/2 top-1/2 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/70 shadow-[0_0_20px_rgba(255,255,255,0.4)]" />
          <div className="md:max-w-xl text-right pr-8">
            <h3 className="text-xl md:text-2xl font-medium tracking-tight">Fluid UI</h3>
            <div className="ml-auto mt-2 h-px w-24 bg-gradient-to-l from-white/0 via-white/60 to-white/0" />
            <p className="mt-3 text-white/70 text-sm md:text-base leading-relaxed">
              Smooth highlights and soft transitions guide your eyes—no abrupt jumps, just gentle motion.
            </p>
          </div>
        </motion.div>

        {/* Feature 4 - right */}
        <motion.div
          className="relative py-10 md:py-12 flex md:justify-start"
          initial={{ opacity: 0, x: 48, y: 12 }}
          whileInView={{ opacity: 1, x: 0, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ type: "spring", stiffness: 120, damping: 18, mass: 0.6, delay: 0.15 }}
        >
          <motion.span
            aria-hidden
            className="pointer-events-none absolute -z-10 blur-3xl"
            style={{
              right: "26%",
              bottom: "18%",
              width: 200,
              height: 200,
              background: "radial-gradient(50% 50% at 50% 50%, rgba(255,255,255,0.12), transparent 70%)",
            }}
            animate={{ y: [3, -3, 3], x: [-4, 4, -4] }}
            transition={{ duration: 8.5, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          />
          <span className="absolute left-1/2 top-1/2 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/70 shadow-[0_0_20px_rgba(255,255,255,0.4)]" />
          <div className="md:max-w-xl text-left pl-8">
            <h3 className="text-xl md:text-2xl font-medium tracking-tight">Offline‑First</h3>
            <div className="mt-2 h-px w-24 bg-gradient-to-r from-white/0 via-white/60 to-white/0" />
            <p className="mt-3 text-white/70 text-sm md:text-base leading-relaxed">
              Core features work locally to reduce latency and keep you typing—even without a connection.
            </p>
          </div>
        </motion.div>
      </section>
    </ShaderBackground>
  )
}
