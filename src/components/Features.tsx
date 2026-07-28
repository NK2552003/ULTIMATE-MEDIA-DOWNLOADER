"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Globe, Music, TerminalSquare, Layers, Sliders, Image as ImageIcon } from "lucide-react";
import Compatibility from "./Compatibility";
import PixelStrip from "./PixelStrip";

const FEATURES = [
  {
    icon: <Globe strokeWidth={2.5} size={16} />,
    title: 'Download from anywhere',
    desc: 'YouTube, Spotify, Instagram, TikTok, SoundCloud, Twitter/X, Vimeo, Reddit, and 50+ more. Paste any URL and UMD figures out the rest.',
  },
  {
    icon: <Music strokeWidth={2.5} size={16} />,
    title: 'Audio extraction',
    desc: 'Extract lossless audio in MP3, FLAC, M4A, OPUS, WAV. Automatic format detection and conversion powered by ffmpeg.',
  },
  {
    icon: <TerminalSquare strokeWidth={2.5} size={16} />,
    title: 'Interactive & headless modes',
    desc: 'Run interactively with guided prompts, or fully headless for scripts and automation. Both modes support the same full feature set.',
  },
  {
    icon: <Layers strokeWidth={2.5} size={16} />,
    title: 'Batch & playlist downloads',
    desc: 'Download entire playlists, channels, or albums in one command. Smart duplicate detection skips files you already have.',
  },
  {
    icon: <Sliders strokeWidth={2.5} size={16} />,
    title: 'Quality control',
    desc: 'Choose your preferred quality or let UMD pick the best available. Supports 4K, 1080p, lossless audio, and everything in between.',
  },
  {
    icon: <ImageIcon strokeWidth={2.5} size={16} />,
    title: '4K wallpapers built in',
    desc: 'Browse and download curated 4K wallpapers directly from the CLI. A hidden feature that actually gets used.',
  },
];

export default function Features() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    
    if (!cardsRef.current) return;
    const cards = cardsRef.current.querySelectorAll('.feature-card');
    
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
    <section id="features" ref={sectionRef} className="min-h-screen pt-24 md:pt-32 pb-0 bg-[var(--offwhite)] text-[var(--offblack)] relative overflow-hidden flex flex-col items-center">
      {/* Background brutalist grid */}
      <div className="absolute inset-0 z-0 opacity-[0.03]" style={{ backgroundImage: 'linear-gradient(var(--offblack) 2px, transparent 2px), linear-gradient(90deg, var(--offblack) 2px, transparent 2px)', backgroundSize: '60px 60px' }}></div>
      
      {/* Abstract Background Shapes */}
      <div className="absolute top-20 left-[-5%] w-[30%] aspect-square border-[10px] border-[var(--offblack)] rounded-full opacity-5 pointer-events-none"></div>
      <div className="absolute bottom-10 right-[-5%] w-[40%] aspect-square bg-[var(--offblack)] opacity-5 pointer-events-none rotate-12"></div>

      <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] relative z-10">
        <div className="mb-16 md:mb-24 flex flex-col items-center text-center">
          <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)]">
            [ CORE FEATURES ]
          </div>
          <h2 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter text-center uppercase leading-[0.9] mb-8">
            Download <span className="text-transparent bg-clip-text bg-[var(--offblack)] bg-[url('/texture.webp')] bg-center bg-contain bg-blend-screen relative inline-block">Anything.</span><br/>Keep it useful.
          </h2>
          <p className="text-base md:text-xl font-mono opacity-80 max-w-3xl mx-auto p-4">
            Write it, speak it, paste it — UMD handles the rest, quietly and without fuss.
          </p>
        </div>

        <div ref={cardsRef} className="grid grid-cols-2 lg:grid-cols-3 gap-3 md:gap-8">
          {FEATURES.map((f, i) => (
            <div key={i} className="feature-card group border-[2px] md:border-[3px] border-[var(--offblack)] bg-[var(--offwhite)] p-4 md:p-8 shadow-[4px_4px_0px_var(--offblack)] md:shadow-[8px_8px_0px_var(--offblack)] hover:shadow-[6px_6px_0px_var(--offblack)] md:hover:shadow-[12px_12px_0px_var(--offblack)] hover:-translate-y-1 hover:-translate-x-1 transition-all duration-300 flex flex-col h-full cursor-default">
              <div className="w-10 h-10 md:w-14 md:h-14 border-[2px] md:border-[3px] border-[var(--offblack)] flex items-center justify-center text-lg md:text-2xl font-black bg-[var(--accent-color)] mb-4 md:mb-6 shadow-[2px_2px_0px_var(--offblack)] md:shadow-[4px_4px_0px_var(--offblack)] group-hover:bg-[var(--offblack)] group-hover:text-[var(--offwhite)] transition-colors duration-300">
                {f.icon}
              </div>
              <h3 className="text-lg md:text-2xl lg:text-3xl font-bold uppercase tracking-tight mb-2 md:mb-4 leading-[1.1] md:leading-[1.1]">
                {f.title}
              </h3>
              <div className="w-full h-[2px] md:h-[3px] bg-[var(--offblack)] mb-3 md:mb-5 opacity-20 group-hover:opacity-100 transition-opacity duration-300"></div>
              <p className="font-mono text-xs md:text-sm lg:text-base opacity-80 md:opacity-70 leading-[1.3] md:leading-relaxed mt-auto group-hover:opacity-100 transition-opacity">
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      <Compatibility />
    </section>
  );
}
