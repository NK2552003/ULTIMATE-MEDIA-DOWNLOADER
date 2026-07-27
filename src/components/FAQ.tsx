"use client";

import { useState } from 'react';
import { Plus, Minus } from "lucide-react";

const FAQS = [
  {
    q: 'Which platforms does UMD support?',
    a: 'UMD supports 110+ platforms via yt-dlp, including YouTube, Spotify, Instagram, TikTok, SoundCloud, Twitter/X, Vimeo, Reddit, Facebook, Twitch, Dailymotion, and many more. If yt-dlp supports it, UMD can download it.',
  },
  {
    q: 'Where is my downloaded media saved?',
    a: 'By default, media is saved to ~/Downloads/UltimateDownloader/. You can configure this by editing the settings in the interactive menu.',
  },
  {
    q: 'Does UMD support playlist and album downloads?',
    a: 'Yes. Paste a playlist or album URL and UMD will download all tracks automatically. It also detects duplicates so you won\'t re-download files you already have.',
  },
  {
    q: 'What audio formats are supported?',
    a: 'UMD supports MP3, FLAC (lossless), M4A, OPUS, and WAV. You choose the format in the interactive prompt, or specify it via command-line flags.',
  },
  {
    q: 'Do I need ffmpeg?',
    a: 'ffmpeg is required for audio extraction and format conversion. Install it via brew (macOS), apt (Linux), or download from ffmpeg.org (Windows). UMD will warn you if it\'s missing.',
  },
  {
    q: 'Is UMD free and open source?',
    a: 'Yes. UMD is fully free, with no ads, no telemetry, and no tracking. The source code is hosted publicly on Codeberg under an open-source license.',
  },
  {
    q: 'Can I use UMD in scripts or automation?',
    a: 'Absolutely. UMD supports a headless/non-interactive mode suitable for cron jobs, shell scripts, and CI pipelines. Run umd help to see all available flags.',
  },
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section className="bg-[var(--offwhite)] text-[var(--offblack)] relative overflow-hidden pb-24 md:pb-32" id="faq">
      {/* Background brutalist grid */}
      <div className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'linear-gradient(var(--offblack) 2px, transparent 2px), linear-gradient(90deg, var(--offblack) 2px, transparent 2px)', backgroundSize: '60px 60px' }}></div>
      
      {/* Abstract Shapes for Texture */}
      <div className="absolute top-[20%] left-[-5%] w-[40%] aspect-square border-[8px] border-[var(--offblack)] rounded-full opacity-5 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] aspect-square bg-[var(--offblack)] opacity-5 pointer-events-none rotate-45"></div>

      <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] relative z-10">
        
        <div className="mb-16 md:mb-24 flex flex-col items-center text-center">
          <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] text-[var(--offblack)] font-bold">
            [ FAQ ]
          </div>
          <h2 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter text-center uppercase leading-[0.9] mb-8">
            Frequently Asked <span className="text-transparent bg-clip-text bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-cover mix-blend-screen opacity-90 inline-block">Questions</span>
          </h2>
          <p className="text-base md:text-lg lg:text-xl font-mono opacity-80 max-w-2xl mx-auto px-4">
            Everything you need to know about UMD, answered directly.
          </p>
        </div>

        <div className="w-full flex flex-col gap-4 md:gap-6">
          {FAQS.map((item, i) => (
            <div
              key={i}
              className={`border-[2px] md:border-[3px] border-[var(--offblack)] bg-[var(--offwhite)] transition-all duration-300 ${
                open === i ? 'shadow-[8px_8px_0px_var(--offblack)] -translate-y-1' : 'shadow-[4px_4px_0px_var(--offblack)] hover:shadow-[6px_6px_0px_var(--offblack)] hover:-translate-y-0.5'
              }`}
            >
              <button
                className="w-full flex items-center justify-between p-4 md:p-6 text-left cursor-pointer group outline-none"
                onClick={() => setOpen(open === i ? null : i)}
              >
                <span className={`text-lg md:text-xl lg:text-2xl font-bold tracking-tight pr-4 ${open === i ? 'text-[var(--offblack)]' : 'group-hover:text-[var(--offblack)] transition-colors'}`}>
                  {item.q}
                </span>
                <span className={`shrink-0 border-[2px] md:border-[3px] border-[var(--offblack)] w-8 h-8 md:w-12 md:h-12 flex items-center justify-center text-[var(--offwhite)] font-bold transition-all duration-300 ${open === i ? 'rotate-180 bg-[var(--accent-color)] text-[var(--offblack)]' : 'bg-[var(--offblack)] group-hover:bg-[var(--accent-color)] group-hover:text-[var(--offblack)]'}`}>
                  {open === i ? <Minus size={24} strokeWidth={3} /> : <Plus size={24} strokeWidth={3} />}
                </span>
              </button>
              
              <div 
                className={`overflow-hidden transition-all duration-300 ease-in-out ${open === i ? 'max-h-[500px] border-t-[2px] md:border-t-[3px] border-[var(--offblack)]' : 'max-h-0 border-t-0'}`}
              >
                <div className="p-4 md:p-8 text-base md:text-lg font-mono opacity-80 leading-relaxed bg-[var(--offwhite)]">
                  {item.a}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
