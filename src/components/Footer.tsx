"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import gsap from "gsap";
import { MoveUpRight, ArrowUpRight, Terminal } from "lucide-react";
import TransitionLink from "./TransitionLink";
import PixelStrip from "./PixelStrip";

const NAV_SECTIONS = [
  { label: "Home",          href: "/#hero" },
  { label: "Features",      href: "/#features" },
  { label: "Install",       href: "/#install" },
  { label: "Docs",          href: "/#docs" },
  { label: "FAQ",           href: "/#faq" },
  { label: "Changelog",     href: "/changelog" },
];

const RESOURCE_LINKS = [
  { label: "Documentation",   href: "/docs/INSTALLATION" },
  { label: "Usage Guide",     href: "/docs/USAGE" },
  { label: "Configuration",   href: "/docs/CONFIGURATION" },
  { label: "Architecture",    href: "/docs/ARCHITECTURE" },
  { label: "Troubleshooting", href: "/docs/TROUBLESHOOTING" },
  { label: "Handler Ref",     href: "/docs/HANDLERS" },
];

const LEGAL_LINKS = [
  { label: "Security Policy", href: "/security" },
  { label: "Apache 2.0 License", href: "/license" },
  { label: "Contributing",    href: "/contributing" },
];

const SOCIALS = [
  { name: "Codeberg",  url: "https://codeberg.org/nk2552003/umd",      desc: "Source & Releases" },
  { name: "GitHub",    url: "https://github.com/nk2552003",             desc: "Profile" },
  { name: "LinkedIn",  url: "https://www.linkedin.com/in/nk2552003/",  desc: "nk2552003" },
  { name: "Instagram", url: "https://www.instagram.com/natur_hacks/",  desc: "@natur_hacks" },
];

const MARQUEE_ITEMS = [
  "115+ Platforms",
  "MP3 · FLAC · M4A · WAV",
  "Open Source · Apache 2.0",
  "No Ads · No Telemetry",
  "Python 3.9+",
  "Batch Downloads",
  "Interactive CLI",
  "4K Wallpapers",
];

export default function Footer() {
  const pathname = usePathname() || "/";
  const isHome = pathname === "/";
  const footerRef = useRef<HTMLDivElement>(null);
  const marqueeRef = useRef<HTMLDivElement>(null);

  /* ── GSAP entrance ── */
  useEffect(() => {
    if (!footerRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".f-reveal",
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, ease: "power3.out", stagger: 0.07,
          scrollTrigger: { trigger: footerRef.current, start: "top 90%" } }
      );

    }, footerRef);
    return () => ctx.revert();
  }, []);

  /* ── Marquee animation ── */
  useEffect(() => {
    if (!marqueeRef.current) return;
    const track = marqueeRef.current.querySelector<HTMLDivElement>(".marquee-track");
    if (!track) return;
    const ctx = gsap.context(() => {
      gsap.to(track, { xPercent: -50, duration: 30, ease: "none", repeat: -1 });
    }, marqueeRef);
    return () => ctx.revert();
  }, []);

  return (
    <footer
      ref={footerRef}
      className="relative overflow-hidden bg-[var(--offblack)] text-[var(--offwhite)]"
    >
      {/* ── Light to Dark pixel transition ── */}
      <PixelStrip direction="down" primaryColor="var(--offwhite)" secondaryColor="var(--accent-color)" />

      {/* ── Marquee ── */}
      <div
        ref={marqueeRef}
        className="f-reveal border-b-[2px] border-[var(--offwhite)]/20 overflow-hidden py-4 relative z-10"
      >
        <div className="marquee-track flex gap-0 whitespace-nowrap w-max select-none">
          {Array.from({ length: 4 }).flatMap(() => MARQUEE_ITEMS).map((item, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-5 px-8 text-[11px] font-mono uppercase tracking-[0.25em] opacity-50"
            >
              {item}
              <span className="inline-block w-1.5 h-1.5 bg-[var(--accent-color)]" />
            </span>
          ))}
        </div>
      </div>

      {/* ── Main Body ── */}
      <div className="relative z-10 container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] pt-16 md:pt-20" style={{ paddingBottom: '2.5rem' }}>

        {/* Top row: Brand + Socials */}
        <div className="flex flex-col lg:flex-row justify-between gap-12 lg:gap-24 border-b-[2px] border-[var(--offwhite)]/20 pb-16 md:pb-20">

          {/* Brand identity */}
          <div className="f-reveal flex flex-col gap-8 lg:max-w-xs xl:max-w-sm">
            <div>
              <div className="flex items-center gap-4 mb-3">
                <div className="w-10 h-10 border-[2px] border-[var(--offwhite)] flex items-center justify-center bg-[var(--accent-color)] shrink-0">
                  <Terminal strokeWidth={2.5} className="w-5 h-5 text-[var(--offblack)]" />
                </div>
                <span className="font-black text-3xl md:text-4xl uppercase tracking-tighter leading-none">UMD</span>
              </div>
              <p className="font-mono text-[11px] uppercase tracking-[0.25em] opacity-40">
                Ultimate Media Downloader v3
              </p>
            </div>

            <p className="font-mono text-sm md:text-base opacity-80 leading-relaxed">
              Professional-grade, open-source media downloading for 115+ platforms.
              Built with Python. No ads. No telemetry. No nonsense.
            </p>

            <div className="flex flex-wrap gap-2">
              {["Apache 2.0", "Python 3.9+", "Open Source", "Free Forever"].map((tag) => (
                <span
                  key={tag}
                  className="border-[2px] border-[var(--offwhite)]/30 px-3 py-1.5 font-mono text-[10px] uppercase tracking-widest opacity-80"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* CTA */}
            <a
              href="https://codeberg.org/nk2552003/umd/releases"
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center gap-3 border-[3px] border-[var(--offwhite)] px-6 py-3 font-mono font-black text-sm uppercase tracking-widest bg-[var(--offwhite)] text-[var(--offblack)] hover:bg-[var(--accent-color)] hover:border-[var(--accent-color)] shadow-[4px_4px_0px_rgba(244,241,238,0.3)] hover:shadow-[6px_6px_0px_rgba(244,241,238,0.4)] hover:-translate-y-0.5 transition-all self-start"
            >
              + Get UMD
              <ArrowUpRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </a>
          </div>

          {/* Socials */}
          <div className="f-reveal flex-1">
            <p className="font-mono text-[11px] uppercase tracking-[0.25em] opacity-40 mb-6">
              [ CONNECT ]
            </p>
            <div className="flex flex-col gap-0">
              {SOCIALS.map((s, i) => (
                <a
                  key={s.name}
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center justify-between py-4 md:py-5 border-b-[2px] border-[var(--offwhite)]/20 hover:border-[var(--accent-color)] transition-all duration-300 hover:pl-4"
                >
                  <div className="flex items-center gap-5">
                    <span className="font-mono text-[11px] opacity-30 group-hover:opacity-70 transition-opacity w-6 tabular-nums">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <div>
                      <div className="text-2xl md:text-3xl font-black uppercase tracking-tighter group-hover:text-[var(--accent-color)] transition-colors duration-200">
                        {s.name}
                      </div>
                      <div className="font-mono text-xs opacity-40 group-hover:opacity-70 transition-opacity">
                        {s.desc}
                      </div>
                    </div>
                  </div>
                  <span className="w-10 h-10 border-[2px] border-[var(--offwhite)]/30 flex items-center justify-center group-hover:bg-[var(--accent-color)] group-hover:border-[var(--accent-color)] transition-all duration-300 shrink-0">
                    <MoveUpRight className="w-4 h-4 text-[var(--offwhite)] group-hover:text-[var(--offblack)] transition-colors duration-200" />
                  </span>
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom 3-col nav */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-10 md:gap-16 pt-16 md:pt-20 border-b-[2px] border-[var(--offwhite)]/20 pb-16">

          {/* Navigation */}
          <div className="f-reveal flex flex-col gap-5">
            <p className="font-mono text-[11px] uppercase tracking-[0.25em] opacity-40">[ Navigation ]</p>
            <ul className="flex flex-col gap-3">
              {NAV_SECTIONS.map((link) => (
                <li key={link.href} className="overflow-hidden">
                  <TransitionLink
                    href={link.href}
                    className="group relative inline-flex items-center gap-3 font-mono text-sm opacity-80 hover:opacity-100 transition-all duration-200 hover:translate-x-1"
                  >
                    <span className="w-3 h-[2px] bg-[var(--offwhite)]/40 group-hover:w-5 group-hover:bg-[var(--accent-color)] transition-all duration-300" />
                    {link.label}
                  </TransitionLink>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div className="f-reveal flex flex-col gap-5">
            <p className="font-mono text-[11px] uppercase tracking-[0.25em] opacity-40">[ Resources ]</p>
            <ul className="flex flex-col gap-3">
              {RESOURCE_LINKS.map((link) => (
                <li key={link.href}>
                  <TransitionLink
                    href={link.href}
                    className="group inline-flex items-center gap-3 font-mono text-sm opacity-80 hover:opacity-100 transition-all duration-200 hover:translate-x-1"
                  >
                    <span className="w-3 h-[2px] bg-[var(--offwhite)]/40 group-hover:w-5 group-hover:bg-[var(--accent-color)] transition-all duration-300" />
                    {link.label}
                  </TransitionLink>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div className="f-reveal flex flex-col gap-5 col-span-2 md:col-span-1">
            <p className="font-mono text-[11px] uppercase tracking-[0.25em] opacity-40">[ Legal ]</p>
            <ul className="flex flex-col gap-3">
              {LEGAL_LINKS.map((link) => (
                <li key={link.href}>
                  <TransitionLink
                    href={link.href}
                    className="group inline-flex items-center gap-3 font-mono text-sm opacity-80 hover:opacity-100 transition-all duration-200 hover:translate-x-1"
                  >
                    <span className="w-3 h-[2px] bg-[var(--offwhite)]/40 group-hover:w-5 group-hover:bg-[var(--accent-color)] transition-all duration-300" />
                    {link.label}
                  </TransitionLink>
                </li>
              ))}
            </ul>

            <div className="mt-4 border-[2px] border-[var(--offwhite)]/20 p-4 flex flex-col gap-1">
              <p className="font-mono text-[10px] uppercase tracking-widest opacity-40 mb-1">Contact</p>
              <a
                href="https://codeberg.org/nk2552003/umd/issues"
                target="_blank"
                rel="noopener noreferrer"
                className="group inline-flex items-center gap-2 font-mono text-sm opacity-80 hover:opacity-100 hover:text-[var(--accent-color)] transition-all"
              >
                Report an Issue
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-all" />
              </a>
              <a
                href="https://codeberg.org/nk2552003"
                target="_blank"
                rel="noopener noreferrer"
                className="group inline-flex items-center gap-2 font-mono text-sm opacity-80 hover:opacity-100 hover:text-[var(--accent-color)] transition-all"
              >
                @nk2552003
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-all" />
              </a>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="f-reveal pt-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 font-mono text-[11px] uppercase tracking-[0.2em] opacity-40">
          <span>© {new Date().getFullYear()} nk2552003 · UMD · All rights reserved</span>
          <div className="flex items-center gap-3">
            <span className="inline-block w-1.5 h-1.5 bg-[var(--accent-color)] animate-pulse" />
            <span>Built with Next.js · Python · GSAP</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
