"use client";

import { useState } from "react";
import { Terminal, Apple, Monitor, LayoutGrid } from "lucide-react";
import PixelStrip from "./PixelStrip";
import MacbookDemo from "./MacbookDemo";

export default function Install() {
  const [activeTab, setActiveTab] = useState("quick");

  const tabs = [
    { id: "quick", label: "Quick Install", icon: Terminal },
    { id: "mac", label: "macOS", icon: Apple },
    { id: "win", label: "Windows", icon: Monitor },
    { id: "linux", label: "Linux", icon: LayoutGrid },
  ];

  return (
    <section id="install" className="md:min-h-screen pt-32 flex flex-col items-center bg-[var(--offblack)] text-[var(--offwhite)] relative overflow-hidden">
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-10 mix-blend-overlay pointer-events-none z-0"></div>

      {/* Background Doodles Layer */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-[0.15] text-[var(--offwhite)]">
        {/* Hand-drawn circle */}
        <svg aria-hidden="true" className="absolute w-[150px] md:w-[200px] h-[150px] md:h-[200px] top-24 left-[2%] md:left-[10%] -rotate-12" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="1">
          <path d="M50,10 C20,15 10,40 15,70 C20,95 60,95 85,75 C105,50 85,15 50,10" strokeLinecap="round"/>
        </svg>

        {/* Squiggly line */}
        <svg aria-hidden="true" className="absolute w-24 md:w-32 h-24 md:h-32 top-[45%] md:top-[50%] left-[2%] md:left-[5%] rotate-[15deg]" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M0,50 Q25,10 50,50 T100,50" />
        </svg>

        {/* Plus signs cluster */}
        <div className="absolute top-24 right-[5%] md:right-[15%] flex flex-col gap-2">
           <div className="flex gap-4">
              <span className="text-3xl md:text-4xl font-mono leading-none">+</span>
              <span className="text-3xl md:text-4xl font-mono leading-none mt-4">+</span>
           </div>
           <div className="flex gap-4 ml-6">
              <span className="text-3xl md:text-4xl font-mono leading-none">+</span>
              <span className="text-3xl md:text-4xl font-mono leading-none mt-2">+</span>
           </div>
        </div>

        {/* Hand-drawn Arrow pointing to Macbook */}
        <svg aria-hidden="true" className="absolute w-16 md:w-24 h-16 md:h-24 bottom-[30%] md:bottom-[40%] right-[4%] md:right-[12%] rotate-[130deg]" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10,90 Q50,60 90,10" />
          <path d="M60,10 L90,10 L90,40" />
        </svg>
        
        {/* Abstract Asterisk/Star */}
        <svg aria-hidden="true" className="absolute w-20 md:w-24 h-20 md:h-24 top-[35%] right-[2%] md:right-[8%] -rotate-12" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
          <line x1="50" y1="10" x2="50" y2="90" />
          <line x1="10" y1="50" x2="90" y2="50" />
          <line x1="20" y1="20" x2="80" y2="80" />
          <line x1="20" y1="80" x2="80" y2="20" />
        </svg>

        {/* Code doodle tag */}
        <div className="absolute bottom-[20%] md:bottom-[25%] left-[2%] md:left-[12%] font-mono text-xs md:text-sm tracking-widest border border-current p-2 md:p-3 rotate-[-6deg] opacity-70">
          {"[ EXEC_MODE: ON ]"}
        </div>
      </div>
      
      <div className="container mx-auto px-4 md:px-8 z-10 w-full flex flex-col items-center justify-center mb-12 md:mb-16">
           <div className="inline-block border-[3px] border-[var(--offwhite)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offwhite)] bg-[var(--dark-color)]">
            [ INTERACTIVE CLI EXPERIENCE ]
          </div>
        <h2 className="text-6xl md:text-8xl lg:text-9xl font-bold tracking-tighter text-center uppercase leading-[0.9] mb-8 text-transparent bg-clip-text bg-[url('/texture.webp')] bg-center bg-cover invert opacity-90">
          Command Line
        </h2>
        <div className="flex flex-col items-center gap-2">
          <div className="flex gap-4 font-mono text-xs md:text-sm tracking-widest opacity-80">
            <span>[ VIDEO ]</span>
            <span>[ AUDIO ]</span>
            <span>[ SOCIAL ]</span>
          </div>
          <p className="text-sm md:text-base opacity-40 text-center max-w-xl font-mono mt-2">
            115+ PLATFORMS. LOSSLESS EXTRACTION. ZERO CONFIGURATION.
          </p>
        </div>
      </div>

      <div className="w-full z-10">
        <MacbookDemo/>
      </div>
    </section>
  );
}
