"use client";

import type { CSSProperties } from 'react'
import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Link from "next/link";
import TransitionLink from "./TransitionLink";

const REPO = 'https://codeberg.org/nk2552003/umd/src/branch/main/documentations'

const docs = [
  ['Installation', 'Set up UMD on macOS, Windows, or Linux.', 'INSTALLATION.md'],
  ['Usage guide', 'Commands, quality choices, batch jobs, and playlists.', 'USAGE.md'],
  ['Configuration', 'Make downloads fit your workflow.', 'CONFIGURATION.md'],
  ['Architecture', 'How handlers, utilities, and the CLI work together.', 'ARCHITECTURE.md'],
  ['Handler reference', 'Extend UMD with platform-aware handlers.', 'HANDLERS.md'],
  ['Troubleshooting', 'Resolve common setup and download issues.', 'TROUBLESHOOTING.md'],
]

export default function Documentation() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    
    if (!cardsRef.current) return;
    const cards = cardsRef.current.querySelectorAll('.doc-card');
    
    gsap.fromTo(cards, 
      { y: 50, opacity: 0, scale: 0.95 },
      {
        y: 0,
        opacity: 1,
        scale: 1,
        duration: 0.6,
        stagger: 0.1,
        ease: "back.out(1.2)",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 70%",
        }
      }
    );
  }, []);

  return (
    <section ref={sectionRef} className="min-h-screen py-24 md:py-32 bg-[var(--offwhite)] text-[var(--offblack)] relative overflow-hidden" id="docs">
      {/* Background brutalist grid */}
      <div className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'linear-gradient(var(--offblack) 2px, transparent 2px), linear-gradient(90deg, var(--offblack) 2px, transparent 2px)', backgroundSize: '60px 60px' }}></div>
      
      <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] relative z-10">
        <div className="mb-16 md:mb-24 flex flex-col lg:flex-row justify-between items-start gap-12 border-b-2 border-[var(--offblack)] pb-16">
          <div className="text-left">
            <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)]">
              [ DOCUMENTATION ]
            </div>
            <h2 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter text-left uppercase leading-[0.9] mb-8">
              Everything explained.<br/>
              <span className="text-transparent bg-clip-text bg-[var(--offblack)] bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-contain bg-blend-screen relative inline-block">
                Nothing hidden.
              </span>
            </h2>
            <p className="text-base md:text-lg lg:text-xl font-mono opacity-80 max-w-3xl p-4 pl-0 mb-0">
              Read the source documentation in your browser, clone it locally, or open it directly in Codeberg. Diagrams use Mermaid, so the system stays understandable as it grows.
            </p>
          </div>
          <Link className="text-xl md:text-2xl font-bold border-b-2 border-[var(--offblack)] hover:bg-[var(--accent-color)] transition-colors py-1 whitespace-nowrap mt-4 lg:mt-0" href="/docs/INDEX">
            Open documentation index ↗
          </Link>
        </div>
        
        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 mb-24">
          {docs.map(([title, text, file], i) => (
            <TransitionLink className="doc-card block border-2 border-[var(--offblack)] p-6 md:p-8 hover:bg-[var(--accent-color)] shadow-[4px_4px_0px_var(--offblack)] hover:shadow-[8px_8px_0px_var(--offblack)] hover:-translate-y-1 hover:-translate-x-1 transition-all duration-300 relative group bg-[var(--offwhite)]" style={{ '--delay': `${i * 60}ms` } as CSSProperties} key={file} href={`/docs/${file.replace('.md', '')}`}>
              <span className="font-mono text-sm tracking-widest absolute top-6 right-6 opacity-50">0{i + 1}</span>
              <h3 className="text-2xl md:text-3xl lg:text-4xl font-bold uppercase tracking-tight mb-4">{title}</h3>
              <p className="text-base md:text-lg mb-8 leading-snug">{text}</p>
              <b className="font-mono text-xs md:text-sm tracking-wider uppercase flex items-center gap-2 group-hover:translate-x-2 transition-transform">Read .md ↗</b>
            </TransitionLink>
          ))}
        </div>
        
        <div className="border-2 border-[var(--offblack)] flex flex-col lg:flex-row bg-[var(--offwhite)] shadow-[12px_12px_0px_var(--offblack)] relative overflow-hidden">
          <div className="p-8 md:p-12 border-b-2 lg:border-b-0 lg:border-r-2 border-[var(--offblack)] lg:w-1/3 flex flex-col justify-center relative z-10 bg-[var(--offwhite)]">
            <span className="font-mono text-xs md:text-sm uppercase tracking-widest mb-4 inline-block opacity-80">System at a glance</span>
            <h3 className="text-3xl md:text-4xl lg:text-5xl font-black uppercase tracking-tighter leading-none mb-4">One command,<br/>clear flow.</h3>
            <p className="text-base md:text-lg lg:text-xl leading-relaxed opacity-80">URL validation routes requests to a dedicated handler when it can. A reliable generic pathway remains available for supported sites.</p>
          </div>
          
          <div className="lg:w-2/3 p-8 md:p-12 flex flex-wrap items-center gap-4 md:gap-8 justify-center lg:justify-start relative" aria-label="UMD architecture diagram">
            {/* Texture background for the diagram side */}
            <div className="absolute inset-0 bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-cover mix-blend-screen opacity-50 pointer-events-none z-0"></div>
            
            <b className="text-lg md:text-2xl lg:text-3xl font-black uppercase tracking-tighter border-2 border-[var(--offblack)] px-4 py-2 bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)] relative z-10">URL</b>
            <i className="text-xl md:text-2xl not-italic font-black relative z-10">→</i>
            <b className="text-lg md:text-2xl lg:text-3xl font-black uppercase tracking-tighter border-2 border-[var(--offblack)] px-4 py-2 bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)] relative z-10">CLI</b>
            <i className="text-xl md:text-2xl not-italic font-black relative z-10">→</i>
            <b className="text-lg md:text-2xl lg:text-3xl font-black uppercase tracking-tighter border-2 border-[var(--offblack)] px-4 py-2 bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)] relative z-10">Validator</b>
            <i className="text-xl md:text-2xl not-italic font-black relative z-10">→</i>
            <b className="text-lg md:text-2xl lg:text-3xl font-black uppercase tracking-tighter border-2 border-[var(--offblack)] px-4 py-2 bg-[var(--accent-color)] shadow-[4px_4px_0px_var(--offblack)] relative z-10">Handler</b>
            <i className="text-xl md:text-2xl not-italic font-black relative z-10">→</i>
            <b className="text-lg md:text-2xl lg:text-3xl font-black uppercase tracking-tighter border-2 border-[var(--offblack)] px-4 py-2 bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)] relative z-10">Media</b>
          </div>
        </div>
      </div>
    </section>
  )
}
