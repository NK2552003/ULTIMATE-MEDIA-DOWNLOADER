"use client";

import { useEffect, useRef, useState } from "react";
import { Terminal } from "lucide-react";
import Lenis from "lenis";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CustomEase } from "gsap/CustomEase";
import { usePathname } from "next/navigation";

gsap.registerPlugin(ScrollTrigger, CustomEase);

import { Toaster } from 'sonner';
import ResponsibleUseToast from './ResponsibleUseToast';

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const lenisRef = useRef<Lenis | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const splashRef = useRef<HTMLDivElement>(null);
  const [splashFinished, setSplashFinished] = useState(false);

  useEffect(() => {
    // Initialize Lenis
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: "vertical",
      gestureOrientation: "vertical",
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
    });

    lenisRef.current = lenis;

    // Synchronize Lenis with ScrollTrigger
    lenis.on("scroll", ScrollTrigger.update);

    gsap.ticker.add((time) => {
      lenis.raf(time * 1000);
    });

    gsap.ticker.lagSmoothing(0);

    // Register custom eases
    CustomEase.create("verticalEase", "0.4, 0, 0.2, 1");
    CustomEase.create("blurEase", "0.65, 0, 0.35, 1");
    CustomEase.create("svgEase", "0.25, 0.1, 0.25, 1");

    return () => {
      lenis.destroy();
      gsap.ticker.remove((time) => {
        lenis.raf(time * 1000);
      });
    };
  }, []);

  const pathname = usePathname();
  useEffect(() => {
    window.dispatchEvent(new Event('routeChangeComplete'));
  }, [pathname]);

  // Initial load splash animation
  useEffect(() => {
    const tl = gsap.timeline({
      onComplete: () => {
        setSplashFinished(true);
        window.dispatchEvent(new Event('splashComplete'));
      }
    });

    // Fade out logo
    tl.to(".shutter-logo", {
      opacity: 0,
      scale: 0.8,
      duration: 0.4,
      ease: "power2.inOut",
      delay: 0.2
    });

    // Animate the shutters (bars) sliding up
    tl.to(".shutter-bar", {
      yPercent: -100,
      duration: 0.8,
      stagger: 0.1,
      ease: "power3.inOut",
    }, "-=0.2");

    // Content animating from bottom to top
    if (containerRef.current) {
      tl.fromTo(containerRef.current,
        { y: "100vh", opacity: 0.5 },
        { y: 0, opacity: 1, duration: 1.2, ease: "power3.out", clearProps: "all" },
        "-=0.7" // overlap with shutter animation
      );
    }
  }, []);

  return (
    <>
      {!splashFinished && (
        <div ref={splashRef} className="fixed inset-0 z-[100] flex pointer-events-none">
           {/* Shutter logo centered over everything */}
           <div className="absolute inset-0 flex items-center justify-center z-10 shutter-logo">
              <div className="w-16 h-16 border-[3px] border-[var(--offblack)] bg-[var(--accent-color)] flex items-center justify-center shadow-[4px_4px_0px_var(--offblack)]">
                <Terminal strokeWidth={2.5} className="w-8 h-8 text-[var(--offblack)]" />
              </div>
           </div>

           {/* 5 vertical shutter bars */}
           {Array.from({ length: 5 }).map((_, i) => (
             <div 
               key={i} 
               className="shutter-bar flex-1 h-full bg-[var(--offblack)]"
               style={{ transformOrigin: 'top' }}
             />
           ))}
        </div>
      )}
      
      <div ref={containerRef}>
        {children}
      </div>
      
      <Toaster position="bottom-center" />
      <ResponsibleUseToast />
    </>
  );
}
