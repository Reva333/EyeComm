"use client";

import type React from "react";
import { useState } from "react";

export default function Header() {
  const [starting, setStarting] = useState(false);

  const startFromNav = (e: React.MouseEvent) => {
    e.preventDefault();
    setStarting(true);

    // Open keyboard app in a new tab
    window.location.href = "/keyboard"

    // Optional: scroll to the "start" section if it exists
    const el = document.getElementById("start");
    if (el) el.scrollIntoView({ behavior: "smooth" });

    setTimeout(() => setStarting(false), 1000);
  };

  return (
    <header className="relative z-20 flex items-center justify-between p-6">
      {/* Logo */}
      <div className="flex items-center">
        {/* Logo content here */}
      </div>

      {/* Navigation */}
      <nav className="flex items-center space-x-2">
        <a
          href="#features"
          className="text-white/80 hover:text-white text-xs font-light px-3 py-2 rounded-full hover:bg-white/10 transition-all duration-200"
        >
          Features
        </a>
        <a
          href="#start"
          onClick={startFromNav}
          className="text-white/80 hover:text-white text-xs font-light px-3 py-2 rounded-full hover:bg-white/10 transition-all duration-200"
        >
          {starting ? "Starting..." : "Start"}
        </a>
      </nav>

      {/* Login Button Group with Arrow */}
      <div
        id="gooey-btn"
        className="relative flex items-center group"
        style={{ filter: "url(#gooey-filter)" }}
      >
        {/* Login button group content here */}
      </div>
    </header>
  );
}
