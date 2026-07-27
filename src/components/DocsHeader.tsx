"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import TransitionLink from "./TransitionLink";
import { usePathname } from "next/navigation";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export default function DocsHeader() {
  const [isScrolled, setIsScrolled] = useState(false);
  const progressBarRef = useRef(null);
  const pathname = usePathname() || "";

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);

    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);

    // Smooth GSAP scroll progress
    gsap.to(progressBarRef.current, {
      scaleX: 1,
      ease: "none",
      scrollTrigger: {
        trigger: document.documentElement,
        start: "top top",
        end: "bottom bottom",
        scrub: 0.1, // Slight smooth catch-up
      }
    });

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <div 
        className={`fixed top-0 left-0 w-full h-32 z-40 transition-opacity duration-500 pointer-events-none ${isScrolled ? 'opacity-100' : 'opacity-0'}`}
        style={{
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          backgroundColor: 'transparent',
          maskImage: 'linear-gradient(to bottom, black 50%, transparent 100%)',
          WebkitMaskImage: 'linear-gradient(to bottom, black 50%, transparent 100%)'
        }}
      ></div>
      <header className="fixed top-0 left-0 w-full py-4 md:py-8 z-50 mix-blend-difference text-[#f5f5f0]">
        <div className="flex flex-wrap items-center justify-between max-w-full mx-auto px-4 md:px-8 gap-y-6">
        <TransitionLink href="/" className="text-2xl md:text-3xl font-bold tracking-tight block">UMD</TransitionLink>
        
        <div className="flex items-center ml-auto relative order-2 lg:order-none">
          <Link
            href="https://codeberg.org/nk2552003/umd/releases"
            className="inline-block bg-[#f5f5f0] text-[#3a3a38] mix-blend-normal px-4 py-2 md:px-6 md:py-3 text-sm md:text-lg uppercase font-bold"
            target="_blank"
          >
            + GET UMD
          </Link>
          <div className="w-[30vw] md:w-[40vw] h-[2px] ml-4 bg-white/20 hidden sm:block">
            <div
              ref={progressBarRef}
              className="h-full bg-[var(--accent-color)] origin-left"
              style={{ transform: "scaleX(0)" }}
            ></div>
          </div>
        </div>

        <nav className="flex gap-4 md:gap-8 w-full lg:w-auto lg:ml-12 text-center lg:text-right justify-center group order-3 lg:order-none mt-2 lg:mt-0">
          <TransitionLink href="/" className="text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none opacity-70">
            home
          </TransitionLink>
          <TransitionLink href="/docs/INSTALLATION" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname.includes('INSTALLATION') ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            install
          </TransitionLink>
          <TransitionLink href="/docs/USAGE" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname.includes('USAGE') ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            usage
          </TransitionLink>
          <TransitionLink href="/docs/CONFIGURATION" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname.includes('CONFIGURATION') ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            config
          </TransitionLink>
        </nav>
      </div>
    </header>
    </>
  );
}
