import { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Shield, AlertTriangle, Lock, Eye, Bug, MessageSquare, CheckCircle, Clock } from 'lucide-react';

export const metadata: Metadata = {
  title: "Security",
  description:
    "Security policy, responsible disclosure guidelines, and security best practices for Ultimate Media Downloader (UMD). Report vulnerabilities safely.",
  openGraph: {
    title: "Security Policy — Ultimate Media Downloader",
    description: "Responsible disclosure guidelines and security practices for UMD.",
    url: "https://ultimate-media-downloader.fun/security",
    images: [{ url: "https://ultimate-media-downloader.fun/og-image.jpg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "UMD Security Policy",
    description: "Security practices and responsible disclosure for Ultimate Media Downloader.",
    images: ["https://ultimate-media-downloader.fun/og-image.jpg"],
  },
  alternates: {
    canonical: "https://ultimate-media-downloader.fun/security",
  },
};

const SECURITY_SECTIONS = [
  {
    icon: Shield,
    tag: '[ POLICY ]',
    title: 'Our Security Commitment',
    color: 'bg-[var(--accent-color)]',
    content: [
      'UMD is an open-source CLI tool. We take security seriously and appreciate responsible disclosure from the community.',
      'This document outlines how to report vulnerabilities, what we consider in scope, and what you can expect from us when you report an issue.',
    ],
  },
  {
    icon: Bug,
    tag: '[ REPORTING ]',
    title: 'Reporting a Vulnerability',
    color: 'bg-[#a3e635]',
    content: [
      'If you discover a security vulnerability in UMD, please report it responsibly. Do not open a public GitHub or Codeberg issue for security vulnerabilities.',
      'Send your report to the maintainer privately via Codeberg\'s private issue tracker or direct message. Include as much detail as possible: steps to reproduce, potential impact, and any suggested fixes.',
    ],
    steps: [
      'Go to the UMD repository on Codeberg',
      'Use the private/confidential issue feature if available',
      'Or DM the maintainer @nk2552003 directly',
      'Include a clear description and reproduction steps',
      'Wait for acknowledgment (within 72 hours)',
    ],
  },
  {
    icon: Eye,
    tag: '[ SCOPE ]',
    title: 'What Is In Scope',
    color: 'bg-[#38bdf8]',
    content: [
      'We are interested in vulnerabilities that could affect users of UMD or the security of the project itself.',
    ],
    items: [
      'Remote code execution via malicious URLs or inputs',
      'Path traversal or arbitrary file write vulnerabilities',
      'Dependency vulnerabilities in direct dependencies (yt-dlp, ffmpeg wrappers)',
      'Authentication or credential exposure in configuration files',
      'Supply chain attacks or compromised dependencies',
      'Privilege escalation during installation scripts',
    ],
  },
  {
    icon: AlertTriangle,
    tag: '[ OUT OF SCOPE ]',
    title: 'What Is Out of Scope',
    color: 'bg-[#facc15]',
    content: [
      'The following are generally not considered security vulnerabilities in the context of UMD:',
    ],
    items: [
      'Downloading copyrighted content (this is a user responsibility)',
      'Rate limiting or throttling by third-party platforms',
      'Issues in yt-dlp itself (report those upstream)',
      'Social engineering or phishing attacks not related to UMD',
      'Vulnerabilities in user\'s own Python/OS environment',
      'Missing best practices without a demonstrated exploit',
    ],
  },
];

const GUIDELINES = [
  { icon: Lock, title: 'Never share credentials', desc: 'UMD does not collect, store, or transmit any of your credentials. Spotify and other platform tokens are stored locally only.' },
  { icon: Eye, title: 'Review install scripts', desc: 'Always review install.sh or install.bat before running. The scripts are open-source and available for inspection on Codeberg.' },
  { icon: CheckCircle, title: 'Keep dependencies updated', desc: 'Run pip install -e . periodically to pull the latest secure versions of all dependencies, especially yt-dlp.' },
  { icon: Clock, title: '72-hour response SLA', desc: 'We commit to acknowledging security reports within 72 hours and providing a fix timeline within 7 days for critical issues.' },
  { icon: MessageSquare, title: 'Coordinated disclosure', desc: 'We ask that reporters give us at least 90 days to patch a vulnerability before public disclosure.' },
  { icon: Shield, title: 'No bounty program', desc: 'UMD is a solo open-source project. While we cannot offer monetary bounties, we will credit all responsible disclosures in the changelog.' },
];

export default function SecurityPage() {
  return (
    <main className="min-h-screen bg-[var(--offwhite)] text-[var(--offblack)] font-sans flex flex-col relative overflow-hidden">
      <Header />

      {/* Background Grid */}
      <div className="fixed inset-0 z-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'linear-gradient(var(--offblack) 2px, transparent 2px), linear-gradient(90deg, var(--offblack) 2px, transparent 2px)', backgroundSize: '60px 60px' }}></div>

      <div className="flex-grow relative z-10" style={{ paddingTop: '10rem' }}>

        {/* Hero Header */}
        <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] pb-16 md:pb-24 border-b-[3px] border-[var(--offblack)]">
          <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold">
            [ SECURITY ]
          </div>
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
            <div>
              <h1 className="text-5xl md:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-[0.9] mb-6">
                Security<br />
                <span className="text-transparent bg-clip-text bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-cover mix-blend-multiply inline-block">Policy</span>
              </h1>
              <p className="text-base md:text-lg lg:text-xl font-mono opacity-70 max-w-2xl leading-relaxed">
                Responsible disclosure, security guidelines, and how we handle vulnerability reports for UMD.
              </p>
            </div>
            <div className="flex flex-col gap-3 shrink-0">
              <div className="border-[2px] border-[var(--offblack)] px-5 py-3 font-mono text-sm bg-[var(--offwhite)] shadow-[3px_3px_0px_var(--offblack)] flex items-center gap-3">
                <Shield className="w-4 h-4 shrink-0" />
                <span className="uppercase tracking-widest text-xs">Apache 2.0 Licensed</span>
              </div>
              <div className="border-[2px] border-[var(--offblack)] px-5 py-3 font-mono text-sm bg-[#a3e635] shadow-[3px_3px_0px_var(--offblack)] flex items-center gap-3">
                <CheckCircle className="w-4 h-4 shrink-0" />
                <span className="uppercase tracking-widest text-xs">Open Source · No Telemetry</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Sections */}
        <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] py-16 md:py-24 flex flex-col gap-16 md:gap-24">

          {SECURITY_SECTIONS.map((section, i) => (
            <div key={i} className="flex flex-col lg:flex-row gap-8 lg:gap-16 items-start border-b-[2px] border-[var(--offblack)] pb-16 md:pb-24 last:border-b-0 last:pb-0">
              {/* Left: Label + Icon */}
              <div className="lg:w-1/3 shrink-0 flex flex-col gap-4">
                <div className={`inline-flex items-center justify-center w-14 h-14 md:w-20 md:h-20 border-[3px] border-[var(--offblack)] ${section.color} shadow-[4px_4px_0px_var(--offblack)]`}>
                  <section.icon strokeWidth={2.5} className="w-6 h-6 md:w-9 md:h-9" />
                </div>
                <div className="font-mono text-xs tracking-[0.2em] uppercase opacity-60">{section.tag}</div>
                <h2 className="text-3xl md:text-4xl lg:text-5xl font-black uppercase tracking-tighter leading-[0.95]">{section.title}</h2>
              </div>

              {/* Right: Content */}
              <div className="lg:w-2/3 flex flex-col gap-6">
                {section.content.map((para, j) => (
                  <p key={j} className="text-base md:text-lg font-mono opacity-80 leading-relaxed">{para}</p>
                ))}

                {section.steps && (
                  <div className="border-[2px] border-[var(--offblack)] bg-[var(--offwhite)] shadow-[6px_6px_0px_var(--offblack)] overflow-hidden">
                    {section.steps.map((step, j) => (
                      <div key={j} className="flex items-start gap-4 p-4 md:p-5 border-b-[2px] border-[var(--offblack)] last:border-b-0 hover:bg-[var(--accent-color)] transition-colors group">
                        <span className="font-mono text-xs font-black opacity-40 group-hover:opacity-100 pt-0.5 shrink-0 w-6">0{j + 1}</span>
                        <span className="font-mono text-sm md:text-base">{step}</span>
                      </div>
                    ))}
                  </div>
                )}

                {section.items && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {section.items.map((item, j) => (
                      <div key={j} className="flex items-start gap-3 border-[2px] border-[var(--offblack)] p-4 shadow-[3px_3px_0px_var(--offblack)] hover:shadow-[5px_5px_0px_var(--offblack)] hover:-translate-y-0.5 transition-all bg-[var(--offwhite)]">
                        <span className="shrink-0 w-3 h-3 bg-[var(--offblack)] mt-1.5 block"></span>
                        <span className="font-mono text-sm md:text-base leading-snug">{item}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Security Guidelines Grid */}
          <div>
            <div className="mb-12 flex flex-col gap-4">
              <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold self-start">
                [ BEST PRACTICES ]
              </div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-black uppercase tracking-tighter leading-[0.95]">Security Guidelines</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
              {GUIDELINES.map((g, i) => (
                <div key={i} className="border-[2px] md:border-[3px] border-[var(--offblack)] p-6 md:p-8 bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)] hover:shadow-[8px_8px_0px_var(--offblack)] hover:-translate-y-1 hover:-translate-x-1 transition-all duration-300 group flex flex-col gap-4">
                  <div className="w-12 h-12 border-[2px] border-[var(--offblack)] flex items-center justify-center bg-[var(--accent-color)] shadow-[2px_2px_0px_var(--offblack)] group-hover:bg-[var(--offblack)] group-hover:text-[var(--offwhite)] transition-colors">
                    <g.icon strokeWidth={2.5} className="w-5 h-5" />
                  </div>
                  <h3 className="text-xl md:text-2xl font-black uppercase tracking-tight">{g.title}</h3>
                  <div className="w-full h-[2px] bg-[var(--offblack)] opacity-20 group-hover:opacity-100 transition-opacity"></div>
                  <p className="font-mono text-sm md:text-base opacity-70 leading-relaxed group-hover:opacity-100 transition-opacity">{g.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Contact CTA */}
          <div className="border-[3px] border-[var(--offblack)] bg-[var(--offblack)] text-[var(--offwhite)] p-8 md:p-12 lg:p-16 shadow-[8px_8px_0px_var(--accent-color)] flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
            <div>
              <div className="font-mono text-xs tracking-[0.2em] uppercase opacity-60 mb-3">[ CONTACT ]</div>
              <h3 className="text-3xl md:text-4xl lg:text-5xl font-black uppercase tracking-tighter leading-none">Found something?</h3>
              <p className="font-mono text-sm md:text-base opacity-70 mt-4 max-w-lg leading-relaxed">Report it responsibly. We read every report and respond to all legitimate security concerns.</p>
            </div>
            <a
              href="https://codeberg.org/nk2552003/umd"
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 border-[3px] border-[var(--offwhite)] px-6 md:px-8 py-3 md:py-4 font-mono font-black text-base md:text-lg uppercase tracking-widest bg-[var(--offwhite)] text-[var(--offblack)] hover:bg-[var(--accent-color)] hover:border-[var(--accent-color)] shadow-[4px_4px_0px_var(--offwhite)] hover:shadow-[6px_6px_0px_var(--offwhite)] hover:-translate-y-0.5 transition-all"
            >
              Report on Codeberg ↗
            </a>
          </div>

        </div>
      </div>

      <Footer />
    </main>
  );
}
