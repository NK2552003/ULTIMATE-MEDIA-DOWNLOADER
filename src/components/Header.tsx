"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import TransitionLink from "./TransitionLink";
import { usePathname } from "next/navigation";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const splitText = (text: string) => {
  return text.split("").map((char, index) => (
    <span key={index} className="header-anim opacity-0 inline-block -translate-y-4" style={{ whiteSpace: char === ' ' ? 'pre' : 'normal' }}>
      {char}
    </span>
  ));
};

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState("hero");
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

    // Track active section
    const sections = ["hero", "features", "install", "docs"];
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { 
        threshold: 0.1,
        rootMargin: "-20% 0px -50% 0px"
      }
    );

    sections.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    const handleSplashComplete = () => {
      gsap.to(".header-anim", {
        opacity: 1,
        y: 0,
        stagger: 0.02,
        duration: 0.8,
        ease: "power3.out"
      });
    };

    window.addEventListener("splashComplete", handleSplashComplete);

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("splashComplete", handleSplashComplete);
      observer.disconnect();
    };
  }, []);

  const isInitialMount = useRef(true);

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    // Reset and replay animation on route change
    gsap.set(".header-anim", { opacity: 0, y: -16 });
    gsap.to(".header-anim", {
      opacity: 1,
      y: 0,
      stagger: 0.02,
      duration: 0.8,
      ease: "power3.out",
      delay: 0.1
    });
  }, [pathname]);

  return (
    <>
      {/* Top Notification Banner */}
      <div className="fixed top-0 left-0 w-full z-[100] bg-[var(--accent-color)] text-[var(--offblack)] border-b-[2px] border-[var(--offblack)] py-1.5 px-4 text-center font-mono text-xs md:text-sm font-bold uppercase tracking-widest flex items-center justify-center gap-3">
        <span className="animate-pulse">🚧</span>
        This site is currently under development
        <span className="animate-pulse">🚧</span>
      </div>

      <div 
        className={`fixed top-8 md:top-9 left-0 w-full h-32 z-40 transition-opacity duration-500 pointer-events-none ${isScrolled ? 'opacity-100' : 'opacity-0'}`}
        style={{
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          backgroundColor: 'transparent',
          maskImage: 'linear-gradient(to bottom, black 50%, transparent 100%)',
          WebkitMaskImage: 'linear-gradient(to bottom, black 50%, transparent 100%)'
        }}
      ></div>
      <header className="fixed top-8 md:top-9 left-0 w-full py-4 md:py-8 z-50 mix-blend-difference text-[#f5f5f0]">
        <div className="flex flex-wrap items-center justify-between max-w-full mx-auto px-4 md:px-8 gap-y-6">
        <div className="text-2xl md:text-3xl font-bold tracking-tight">
          {splitText("UMD")}
        </div>
        
        <div className="flex items-center ml-auto relative order-2 lg:order-none">
          <Link
            href="https://codeberg.org/nk2552003/umd/releases"
            className="header-anim opacity-0 -translate-y-4 inline-block bg-[#f5f5f0] text-[#3a3a38] mix-blend-normal px-4 py-2 md:px-6 md:py-3 text-sm md:text-lg uppercase font-bold"
            target="_blank"
          >
            + GET UMD
          </Link>
          <div className="header-anim opacity-0 -translate-y-4 w-[30vw] md:w-[40vw] h-[2px] ml-4 bg-white/20 hidden sm:block">
            <div
              ref={progressBarRef}
              className="h-full bg-[var(--accent-color)] origin-left"
              style={{ transform: "scaleX(0)" }}
            ></div>
          </div>
        </div>

        <nav className="flex gap-4 md:gap-8 w-full lg:w-auto lg:ml-12 text-center lg:text-right justify-center group order-3 lg:order-none mt-2 lg:mt-0">
          <TransitionLink onClick={() => setActiveSection('hero')} href="/#hero" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname === '/' && activeSection === 'hero' ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            {splitText("home")}
          </TransitionLink>
          <TransitionLink onClick={() => setActiveSection('features')} href="/#features" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname === '/' && activeSection === 'features' ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            {splitText("features")}
          </TransitionLink>
          <TransitionLink onClick={() => setActiveSection('install')} href="/#install" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname === '/' && activeSection === 'install' ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            {splitText("install")}
          </TransitionLink>
          <TransitionLink onClick={() => setActiveSection('docs')} href="/#docs" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname === '/' && activeSection === 'docs' ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            {splitText("docs")}
          </TransitionLink>
          <TransitionLink href="/changelog" className={`text-base md:text-xl lowercase transition-all duration-300 group-hover:blur-[2px] hover:!blur-none ${pathname === '/changelog' ? 'opacity-100 font-bold border-b-2' : 'opacity-70'}`}>
            {splitText("changelog")}
          </TransitionLink>
        </nav>
      </div>
    </header>
    </>
  );
}
