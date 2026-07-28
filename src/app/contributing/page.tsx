import { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { GitBranch, GitPullRequest, Bug, Lightbulb, Code2, MessageSquare, Heart, Star } from 'lucide-react';

export const metadata: Metadata = {
  title: "Contributing",
  description:
    "Learn how to contribute to UMD — from bug reports and feature requests to adding new platform handlers. All contributions are welcome.",
  openGraph: {
    title: "Contributing to Ultimate Media Downloader",
    description: "Join the UMD community. Submit bug reports, feature requests, or new platform handlers.",
    url: "https://ultimate-media-downloader.fun/contributing",
    images: [{ url: "https://ultimate-media-downloader.fun/og-image.jpg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Contribute to UMD",
    description: "How to contribute to Ultimate Media Downloader.",
    images: ["https://ultimate-media-downloader.fun/og-image.jpg"],
  },
  alternates: {
    canonical: "https://ultimate-media-downloader.fun/contributing",
  },
};

const WAYS_TO_CONTRIBUTE = [
  {
    icon: Bug,
    tag: '01',
    title: 'Report Bugs',
    color: 'bg-[#f87171]',
    desc: 'Found something broken? Open an issue on Codeberg with clear reproduction steps, your OS, Python version, and the full error output.',
  },
  {
    icon: Lightbulb,
    tag: '02',
    title: 'Suggest Features',
    color: 'bg-[#facc15]',
    desc: 'Have an idea? Open a feature request on Codeberg. Describe the use case, not just the solution — context helps us understand the need.',
  },
  {
    icon: Code2,
    tag: '03',
    title: 'Write Code',
    color: 'bg-[#a3e635]',
    desc: 'Fork the repo, make your changes on a feature branch, and open a pull request. Keep commits small and focused. All code must pass existing tests.',
  },
  {
    icon: GitBranch,
    tag: '04',
    title: 'Add a Platform Handler',
    color: 'bg-[#38bdf8]',
    desc: 'UMD uses a modular handler system. Adding a new platform is as simple as creating a new handler class in the handlers/ directory and registering it.',
  },
  {
    icon: MessageSquare,
    tag: '05',
    title: 'Improve Docs',
    color: 'bg-[#c084fc]',
    desc: 'Documentation lives in the documentations/ folder as Markdown. Fix typos, add examples, or write new guides — docs PRs are always welcome.',
  },
  {
    icon: Star,
    tag: '06',
    title: 'Star & Share',
    color: 'bg-[var(--accent-color)]',
    desc: 'The simplest contribution: star the repo on Codeberg and share UMD with developers who need it. Visibility helps the project grow.',
  },
];

const WORKFLOW_STEPS = [
  { title: 'Fork the repository', desc: 'Go to codeberg.org/nk2552003/umd and fork it to your account.' },
  { title: 'Clone your fork', desc: 'git clone https://codeberg.org/YOUR_USERNAME/umd.git && cd umd' },
  { title: 'Create a feature branch', desc: 'git checkout -b feature/your-feature-name  or  fix/bug-description' },
  { title: 'Make your changes', desc: 'Write code, update tests, and add docs if relevant to your change.' },
  { title: 'Test your changes', desc: 'Run the test suite to make sure nothing is broken: python -m pytest' },
  { title: 'Commit & push', desc: 'git add . && git commit -m "feat: describe your change" && git push origin feature/...' },
  { title: 'Open a Pull Request', desc: 'Go to Codeberg, open a PR from your branch to main. Fill in the PR template.' },
  { title: 'Review & merge', desc: 'The maintainer will review your PR, request changes if needed, then merge it.' },
];

const CODE_STANDARDS = [
  'Python 3.9+ compatible code only',
  'Follow PEP 8 style guidelines',
  'Add type hints to new functions',
  'Write docstrings for public methods',
  'Keep handler classes in handlers/ directory',
  'Update CHANGELOG.md with your changes',
  'No new dependencies without maintainer approval',
  'Test on at least one platform before PR',
];

export default function ContributingPage() {
  return (
    <main className="min-h-screen bg-[var(--offwhite)] text-[var(--offblack)] font-sans flex flex-col relative overflow-hidden">
      <Header />

      {/* Background Grid */}
      <div className="fixed inset-0 z-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'linear-gradient(var(--offblack) 2px, transparent 2px), linear-gradient(90deg, var(--offblack) 2px, transparent 2px)', backgroundSize: '60px 60px' }}></div>

      <div className="flex-grow relative z-10" style={{ paddingTop: '10rem' }}>

        {/* Hero */}
        <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] pb-16 md:pb-24 border-b-[3px] border-[var(--offblack)]">
          <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold">
            [ OPEN SOURCE ]
          </div>
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-[0.9] mb-6">
            Contributing<br />
            <span className="text-transparent bg-clip-text bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-cover mix-blend-multiply inline-block">to UMD</span>
          </h1>
          <p className="text-base md:text-lg lg:text-xl font-mono opacity-70 max-w-2xl leading-relaxed">
            UMD is built in the open. Whether you fix a typo, add a platform handler, or report a bug — every contribution makes it better.
          </p>
        </div>

        <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] py-16 md:py-24 flex flex-col gap-16 md:gap-24">

          {/* Ways to Contribute */}
          <div>
            <div className="mb-12 flex flex-col gap-4">
              <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold self-start">
                [ HOW TO HELP ]
              </div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-black uppercase tracking-tighter leading-[0.95]">Ways to Contribute</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
              {WAYS_TO_CONTRIBUTE.map((w) => (
                <div key={w.tag} className="border-[2px] md:border-[3px] border-[var(--offblack)] bg-[var(--offwhite)] p-6 md:p-8 shadow-[4px_4px_0px_var(--offblack)] hover:shadow-[8px_8px_0px_var(--offblack)] hover:-translate-y-1 hover:-translate-x-1 transition-all duration-300 group flex flex-col gap-4">
                  <div className="flex items-start justify-between">
                    <div className={`w-12 h-12 border-[2px] border-[var(--offblack)] flex items-center justify-center ${w.color} shadow-[2px_2px_0px_var(--offblack)] group-hover:bg-[var(--offblack)] group-hover:text-[var(--offwhite)] transition-colors`}>
                      <w.icon strokeWidth={2.5} className="w-5 h-5" />
                    </div>
                    <span className="font-mono text-3xl font-black opacity-10 group-hover:opacity-30 transition-opacity">{w.tag}</span>
                  </div>
                  <h3 className="text-xl md:text-2xl font-black uppercase tracking-tight">{w.title}</h3>
                  <div className="w-full h-[2px] bg-[var(--offblack)] opacity-20 group-hover:opacity-100 transition-opacity"></div>
                  <p className="font-mono text-sm md:text-base opacity-70 leading-relaxed group-hover:opacity-100 transition-opacity">{w.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Workflow */}
          <div>
            <div className="mb-12 flex flex-col gap-4">
              <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold self-start">
                [ WORKFLOW ]
              </div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-black uppercase tracking-tighter leading-[0.95]">PR Workflow</h2>
            </div>

            <div className="flex flex-col gap-0 border-[3px] border-[var(--offblack)] shadow-[8px_8px_0px_var(--offblack)] overflow-hidden">
              {WORKFLOW_STEPS.map((step, i) => (
                <div key={i} className="flex items-start gap-6 p-5 md:p-7 border-b-[2px] border-[var(--offblack)] last:border-b-0 hover:bg-[var(--accent-color)] transition-colors group bg-[var(--offwhite)]">
                  <span className="font-mono text-2xl md:text-3xl font-black opacity-20 group-hover:opacity-80 transition-opacity shrink-0 pt-1 w-10">
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <div className="flex flex-col gap-1">
                    <h4 className="text-lg md:text-xl font-black uppercase tracking-tight">{step.title}</h4>
                    <p className="font-mono text-sm md:text-base opacity-70 group-hover:opacity-100 transition-opacity">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Code Standards */}
          <div className="flex flex-col lg:flex-row gap-8 lg:gap-16">
            <div className="lg:w-1/2">
              <div className="mb-8 flex flex-col gap-4">
                <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold self-start">
                  [ STANDARDS ]
                </div>
                <h2 className="text-3xl md:text-4xl lg:text-5xl font-black uppercase tracking-tighter leading-[0.95]">Code Standards</h2>
              </div>
              <div className="flex flex-col gap-3">
                {CODE_STANDARDS.map((s, i) => (
                  <div key={i} className="flex items-center gap-4 border-[2px] border-[var(--offblack)] p-4 bg-[var(--offwhite)] shadow-[3px_3px_0px_var(--offblack)] hover:shadow-[5px_5px_0px_var(--offblack)] hover:-translate-y-0.5 transition-all">
                    <span className="shrink-0 w-3 h-3 bg-[var(--offblack)] block"></span>
                    <span className="font-mono text-sm md:text-base">{s}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="lg:w-1/2 flex flex-col gap-6">
              <div className="border-[3px] border-[var(--offblack)] bg-[var(--offblack)] text-[var(--offwhite)] p-6 md:p-8 shadow-[6px_6px_0px_var(--accent-color)]">
                <div className="font-mono text-xs opacity-50 uppercase tracking-widest mb-4">[ COMMIT FORMAT ]</div>
                <pre className="font-mono text-sm md:text-base leading-relaxed whitespace-pre-wrap opacity-90">{`feat: add TikTok handler
fix: resolve playlist URL parsing
docs: update INSTALLATION.md
chore: bump yt-dlp to 2024.12.x
refactor: simplify download queue
test: add tests for audio extraction`}</pre>
              </div>

              <div className="border-[3px] border-[var(--offblack)] bg-[var(--offwhite)] p-6 md:p-8 shadow-[6px_6px_0px_var(--offblack)] flex flex-col gap-4">
                <div className="font-mono text-xs opacity-50 uppercase tracking-widest">[ FIRST TIME? ]</div>
                <h3 className="text-2xl md:text-3xl font-black uppercase tracking-tight">Look for Good First Issues</h3>
                <p className="font-mono text-sm md:text-base opacity-70 leading-relaxed">Issues tagged <code className="border border-current px-1.5 py-0.5 font-bold">good-first-issue</code> on Codeberg are intentionally scoped to be approachable for new contributors.</p>
                <a href="https://codeberg.org/nk2552003/umd/issues" target="_blank" rel="noopener noreferrer" className="border-[2px] border-[var(--offblack)] px-5 py-3 font-mono text-sm font-black uppercase tracking-widest bg-[var(--accent-color)] shadow-[3px_3px_0px_var(--offblack)] hover:shadow-[5px_5px_0px_var(--offblack)] hover:-translate-y-0.5 transition-all self-start">
                  Browse Issues ↗
                </a>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="border-[3px] border-[var(--offblack)] bg-[var(--offblack)] text-[var(--offwhite)] p-8 md:p-12 lg:p-16 shadow-[8px_8px_0px_var(--accent-color)] flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
            <div>
              <div className="font-mono text-xs tracking-[0.2em] uppercase opacity-80 mb-3">[ READY? ]</div>
              <h3 className="text-3xl md:text-4xl lg:text-5xl font-black uppercase tracking-tighter leading-none">Let&apos;s build it<br/>together.</h3>
              <p className="font-mono text-sm md:text-base opacity-70 mt-4 max-w-lg leading-relaxed">Every line of code, every bug report, every doc fix makes UMD better for everyone.</p>
            </div>
            <a
              href="https://codeberg.org/nk2552003/umd"
              target="_blank"
              rel="noopener noreferrer"
              className="shrink-0 border-[3px] border-[var(--offwhite)] px-6 md:px-8 py-3 md:py-4 font-mono font-black text-base md:text-lg uppercase tracking-widest bg-[var(--offwhite)] text-[var(--offblack)] hover:bg-[var(--accent-color)] hover:border-[var(--accent-color)] shadow-[4px_4px_0px_var(--offwhite)] transition-all"
            >
              Fork on Codeberg ↗
            </a>
          </div>

        </div>
      </div>

      <Footer />
    </main>
  );
}
