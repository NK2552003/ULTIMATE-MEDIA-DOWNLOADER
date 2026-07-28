"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import Image from "next/image";
import { Terminal, Zap, Award, List, RefreshCw, Info, MonitorSmartphone, AppWindow, Command, Server, AudioLines, Music, Radio, MessageSquare, Plus } from "lucide-react";
import { FaYoutube } from "react-icons/fa";
import PixelStrip from "./PixelStrip";

const basePath = '';

export default function Hero() {
  const textRef = useRef(null);

  const dotPattern = [
    [1, 0.5, 1, 0.5, 1, 1, 0.5, 1, 0.5, 1],
    [0.5, 0, 0.5, 0, 0.5, 0.5, 1, 0.5, 1, 0.5],
    [1, 0.5, 1, 0.5, 1, 1, 0.5, 1, 0.5, 1],
    [0, 0, 0, 0, 0, 0, 1, 0.5, 1, 0.5],
    [0, 0, 0, 0, 0, 0, 0.5, 1, 0.5, 1],
    [0, 0, 0, 0, 0, 0, 1, 0.5, 1, 1],
  ];

  useEffect(() => {

    gsap.to(textRef.current, {
      scrollTrigger: {
        trigger: "#hero",
        start: "top bottom",
        end: "center center",
        scrub: true,
      },
      y: 0,
      opacity: 1,
      filter: "blur(0px)",
      duration: 1,
      ease: "verticalEase",
    });
  }, []);

  return (
    <section id="hero" className="min-h-screen relative flex items-center pt-24 md:pt-32">
      <div 
        className="absolute inset-0 z-0 pointer-events-none" 
        style={{ 
          backgroundImage: 'linear-gradient(var(--offblack) 2px, transparent 2px), linear-gradient(90deg, var(--offblack) 2px, transparent 2px)', 
          backgroundSize: '60px 60px',
          opacity: 0.04,
          maskImage: 'linear-gradient(to bottom, transparent 0%, black 15%, black 60%, transparent 100%)',
          WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, black 15%, black 60%, transparent 100%)'
        }}
      ></div>
      
      {/* Decorative Dot Matrix */}
      <div className="hidden lg:grid absolute top-[100px] right-20 gap-3 z-1000 opacity-50 pointer-events-none" style={{ gridTemplateColumns: 'repeat(10, minmax(0, 1fr))' }}>
        {dotPattern.flat().map((val, i) => (
          <div key={i} className="w-1.5 h-1.5 rounded-full bg-current text-[var(--offblack)]" style={{ opacity: val }} />
        ))}
      </div>

      <Image 
        src={`${basePath}/totoro_hero.svg`} 
        alt="Totoro Media Downloader" 
        width={1200}
        height={1200}
        priority
        className="hidden lg:block absolute right-0 bottom-0 h-[95vh] max-h-[1200px] w-auto object-contain object-right-bottom z-30 pointer-events-none mix-blend-multiply"
        style={{ 
          WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%)', 
          maskImage: 'linear-gradient(to bottom, transparent 0%, black 15%, black 85%, transparent 100%)' 
        }} 
      />

      {/* Vertical Side Element */}
      <div className="hidden md:flex fixed left-2 md:left-8 top-32 bottom-0 flex-col items-center gap-6 z-50 text-[#f5f5f0] mix-blend-difference opacity-80 font-mono text-xs tracking-[0.2em] pointer-events-none">
        <div className="w-1.5 h-1.5 rounded-full bg-current"></div>
        <div className="[writing-mode:vertical-rl] whitespace-nowrap">OPEN SOURCE</div>
        <div className="w-px h-16 bg-current"></div>
        <div className="[writing-mode:vertical-rl] whitespace-nowrap">MEDIA DOWNLOADER V3</div>
        <div className="w-px h-16 bg-current"></div>
        <div className="relative flex items-center justify-center w-4 h-4">
          <div className="absolute w-full h-px bg-current"></div>
          <div className="absolute w-px h-full bg-current"></div>
          <div className="w-2.5 h-2.5 border border-current rounded-full"></div>
        </div>
        <div className="w-px flex-1 border-l border-dashed border-current"></div>
        <div className="w-1.5 h-1.5 rounded-full bg-current shrink-0 mb-8"></div>
      </div>

      {/* Vertical Side Element (Right) */}
      <div className="hidden md:flex fixed right-2 md:right-8 top-32 bottom-0 flex-col items-center gap-6 z-50 text-[#f5f5f0] mix-blend-difference opacity-80 font-mono text-xs tracking-[0.2em] pointer-events-none">
        <div className="w-1.5 h-1.5 rounded-full bg-current shrink-0"></div>
        <div className="w-px flex-1 border-l border-dashed border-current"></div>
        <div className="relative flex items-center justify-center w-4 h-4">
          <div className="absolute w-full h-px bg-current"></div>
          <div className="absolute w-px h-full bg-current"></div>
          <div className="w-2.5 h-2.5 border border-current rounded-full"></div>
        </div>
        <div className="w-px h-16 bg-current"></div>
        <div className="[writing-mode:vertical-rl] whitespace-nowrap">HIGH PERFORMANCE</div>
        <div className="w-px h-16 bg-current"></div>
        <div className="[writing-mode:vertical-rl] whitespace-nowrap">CLI INTERFACE</div>
        <div className="w-1.5 h-1.5 rounded-full bg-current mb-8"></div>
      </div>

      <div className="container mx-auto pl-12 md:pl-24 pr-4 md:pr-8 w-full max-w-full">
        {/* SVG Row */}
        <div className="grid grid-cols-12 gap-4 mt-12 md:mt-20 mb-8 md:mb-4 relative">
          <div className="col-span-12 relative overflow-hidden">
            <div className="flex flex-wrap items-center gap-2 md:gap-4 mb-6 md:mb-8 font-mono text-xs md:text-sm uppercase tracking-wide relative z-30">
              <span className="flex items-center gap-2 border-[2px] border-[var(--offblack)] px-3 py-1 bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)]">
                <svg aria-label="Python Logo" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" className="w-4 h-4 fill-current">
                  <path d="M439.8 200.5c-7.7-30.9-22.3-54.2-53.4-54.2h-40.1v47.4c0 36.8-31.2 67.8-66.8 67.8H172.7c-29.2 0-53.4 25-53.4 54.3v101.8c0 29 25.2 46 53.4 54.3 33.8 9.9 66.3 11.7 106.8 0 26.9-7.8 53.4-23.5 53.4-54.3v-40.7H226.2v-13.6h160.2c31.1 0 42.6-21.7 53.4-54.2 11.2-33.5 10.7-65.7 0-108.6zM286.2 404c11.1 0 20.1 9.1 20.1 20.3 0 11.3-9 20.4-20.1 20.4-11 0-20.1-9.2-20.1-20.4 .1-11.3 9.1-20.3 20.1-20.3zM167.8 248.1h106.8c29.7 0 53.4-25 53.4-54.3V92.1c0-29-24.4-50.7-53.4-54.3-35.8-4.5-74.1-4.4-106.8 0-29.2 3.5-53.4 25.2-53.4 54.3v40.7h106.8v13.6H61.1c-30.9 0-42.6 21.7-53.4 54.2-11.2 33.5-10.7 65.7 0 108.6 7.6 30.9 22.3 54.2 53.4 54.2h40.1v-47.4c0-36.8 31.2-67.8 66.8-67.8h106.8c29.2 0 53.4-25 53.4-54.3V248.1h-106.8zM161.7 108.6c11.1 0 20.1-9.1 20.1-20.3 0-11.3-9-20.4-20.1-20.4-11 0-20.1 9.2-20.1 20.4 0 11.3 9.1 20.3 20.1 20.3z"/>
                </svg>
                Python 3.10+
              </span>
              <span className="border-[2px] border-[var(--offblack)] px-3 py-1 bg-[var(--accent-color)] shadow-[4px_4px_0px_var(--offblack)]">
                Apache 2.0
              </span>
              <span className="border-[2px] border-[var(--offblack)] px-3 py-1 bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)]">
                Free Forever
              </span>
            </div>
            <div className="relative inline-block">
              {/* Textured Text Layer */}
              <h1 className="text-[4rem] sm:text-[6rem] md:text-[8rem] lg:text-[10rem] leading-[0.85] font-black uppercase tracking-tighter text-transparent bg-clip-text bg-[var(--offblack)] bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-contain bg-blend-screen relative z-10 pointer-events-none">
                Ultimate<br/>
                <span className="inline-flex items-center gap-2 md:gap-6">
                  Media
                  <span className="inline-block border-[2px] md:border-[4px] border-transparent px-2 md:px-4 py-0 md:py-1 text-2xl md:text-4xl lg:text-6xl leading-none tracking-normal font-bold opacity-0 -translate-y-1 md:-translate-y-2">
                    v3.0.1
                  </span>
                </span><br/>
                Downloader
              </h1>
              
              {/* Solid Badge Overlay Layer */}
              <h1 className="absolute inset-0 text-[4rem] sm:text-[6rem] md:text-[8rem] lg:text-[10rem] leading-[0.85] font-black uppercase tracking-tighter text-transparent z-20 pointer-events-none" aria-hidden="true">
                <span className="opacity-0">Ultimate</span><br/>
                <span className="inline-flex items-center gap-2 md:gap-6">
                  <span className="opacity-0">Media</span>
                  <span className="relative inline-block overflow-hidden -translate-y-1 md:-translate-y-2 pointer-events-auto">
                    <span className="relative z-10 inline-block border-[2px] md:border-[4px] border-[var(--offblack)] px-2 md:px-4 py-0 md:py-1 text-2xl md:text-4xl lg:text-6xl leading-none tracking-normal font-bold bg-[var(--accent-color)] text-[var(--offblack)]">
                      v3.0.1
                    </span>
                    <span className="absolute inset-0 bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-contain mix-blend-screen opacity-90 z-20 pointer-events-none"></span>
                  </span>
                </span><br/>
                <span className="opacity-0">Downloader</span>
              </h1>
            </div>
          </div>
        </div>

        {/* Mobile Graphic */}
        <div className="flex lg:hidden w-full justify-center relative mt-12 mb-4">
           <div className="relative w-[90vw] max-w-[400px] rounded-lg overflow-hidden border border-[var(--offblack)] shadow-[4px_4px_0px_var(--offblack)]">
             <Image src={`${basePath}/totoro_mobile_hero.webp`} alt="Media Downloading" width={400} height={500} priority className="w-full h-auto object-contain z-10 relative" />
           </div>
        </div>

        {/* Content Row */}
        <div className="gap-8 items-start mb-8 md:mb-16 w-full max-w-[300px] md:max-w-[500px] lg:max-w-[600px]">
          <div className="md:pl-8 text-left overflow-hidden mt-8 md:mt-4">
            <p
              ref={textRef}
              className="text-lg md:text-xl lg:text-2xl leading-relaxed opacity-0 translate-y-20 blur-[5px]"
            >
              A professional-grade, open-source media downloading tool supporting 115+ platforms. Built with Python, it features a beautiful Rich CLI interface and enterprise-level capabilities with consumer-friendly simplicity. Download from YouTube, Spotify, Amazon Music, and more with just one command.
            </p>
            
            <div className="mt-8 md:mt-12 flex sm:flex-row gap-8 sm:gap-12 md:gap-16">
              <div className="border-l-[2px] border-[var(--offblack)] pl-6 md:pl-8 flex flex-col gap-4 text-[var(--offblack)]">
                <div className="flex items-center gap-4">
                  <Zap className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Parallel Downloads</span>
                </div>
                <div className="flex items-center gap-4">
                  <Award className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">High Quality</span>
                </div>
                <div className="flex items-center gap-4">
                  <List className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Playlist Support</span>
                </div>
                <div className="flex items-center gap-4">
                  <RefreshCw className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Resume Support</span>
                </div>
              </div>
              
              <div className="border-l-[2px] border-[var(--offblack)] pl-6 md:pl-8 flex flex-col gap-4 text-[var(--offblack)]">
                <div className="flex items-center gap-4">
                  <AppWindow className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Windows 10/11</span>
                </div>
                <div className="flex items-center gap-4">
                  <Command className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">macOS (M1/Intel)</span>
                </div>
                <div className="flex items-center gap-4">
                  <Terminal className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Linux & distros</span>
                </div>
                <div className="flex items-center gap-4">
                  <Server className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Docker / CLI</span>
                </div>
              </div>

              <div className="hidden md:flex border-l-[2px] border-[var(--offblack)] pl-6 md:pl-8 flex-col gap-4 text-[var(--offblack)]">
                <div className="flex items-center gap-4">
                  <FaYoutube className="w-5 h-5 md:w-6 md:h-6" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">YouTube</span>
                </div>
                <div className="flex items-center gap-4">
                  <AudioLines className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Spotify</span>
                </div>
                <div className="flex items-center gap-4">
                  <Music className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">Apple Music</span>
                </div>
                <div className="flex items-center gap-4">
                  <Plus className="w-5 h-5 md:w-6 md:h-6 stroke-[2.5]" />
                  <span className="text-sm md:text-lg font-bold tracking-tight">110+ More</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
