import { NextResponse } from "next/server"
import { spawn } from "child_process"
import path from "path"

export async function POST() {
  try {
    const scriptPath = path.join(process.cwd(), "scripts", "gazeType.py")
    const proc = spawn("python", [scriptPath])

    proc.stdout.on("data", (data) => {
      console.log("[v0] gazeType.py:", data.toString())
    })
    proc.stderr.on("data", (data) => {
      console.log("[v0] gazeType.py error:", data.toString())
    })

    // Do not await close; return immediately that we started
    return NextResponse.json({ ok: true, message: "gazeType.py started" })
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: String(e?.message || e) }, { status: 500 })
  }
}
