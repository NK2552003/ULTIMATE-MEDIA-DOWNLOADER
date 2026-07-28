"use client";

import { useState, useEffect } from "react";
import { Check, Copy, TerminalSquare } from "lucide-react";
import PixelStrip from "./PixelStrip";

const AppleIcon = () => (
  <svg aria-hidden="true" viewBox="0 0 384 512" fill="currentColor" className="w-4 h-4 md:w-5 md:h-5">
    <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.3 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.3zM34.4 46.1c25.4-31.5 61.1-46.1 82.6-46.1 4.5 0 9.1 .6 12.3 1.2-2.3 29.4-14.4 63.8-38.3 89.2-22.3 24.5-56.1 39.3-84.7 39.3-1.2-30.7 7.6-61.1 28.1-83.6z"/>
  </svg>
);

const WindowsIcon = () => (
  <svg aria-hidden="true" viewBox="0 0 448 512" fill="currentColor" className="w-4 h-4 md:w-5 md:h-5">
    <path d="M0 93.7l210.6-29.7v167.4H0V93.7zm0 216.9h210.6v167.4L0 448.3V310.6zm237.4 171.1L448 512V310.6H237.4v171.1zm0-394L448 0v216.9H237.4V87.7z"/>
  </svg>
);

const LinuxIcon = () => (
  <TerminalSquare className="w-4 h-4 md:w-5 md:h-5" />
);

const OS_TABS = [
  { id: 'macOS', label: 'macOS', icon: AppleIcon },
  { id: 'Windows', label: 'Windows', icon: WindowsIcon },
  { id: 'Linux', label: 'Linux', icon: LinuxIcon }
];

const METHOD_TABS = ['Quick Install', 'pipx', 'pip', 'venv'];

const INSTALL_DATA: Record<string, Record<string, string[]>> = {
  'macOS': {
    'Quick Install': [
      '# Easiest: Download .pkg from Releases',
      '# Or install via terminal:',
      '',
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      './scripts/install.sh',
      '',
      'umd --version',
    ],
    'pipx': [
      '# Install pipx if needed',
      'brew install pipx',
      '',
      '# Clone and install',
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'pipx install -e .',
    ],
    'pip': [
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'pip3 install -e .',
    ],
    'venv': [
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'python3 -m venv venv',
      'source venv/bin/activate',
      'pip install -r requirements.txt',
      'python ultimate_downloader.py',
    ]
  },
  'Windows': {
    'Quick Install': [
      '# Note: Ensure Python, Git, and FFmpeg are installed',
      '',
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'scripts\\install.bat',
      '',
      'umd --version',
    ],
    'pipx': [
      '# Install pipx if needed',
      'pip install --user pipx',
      '',
      '# Clone and install',
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'pipx install -e .',
    ],
    'pip': [
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'pip3 install -e .',
    ],
    'venv': [
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'python3 -m venv venv',
      'venv\\Scripts\\activate',
      'pip install -r requirements.txt',
      'python ultimate_downloader.py',
    ]
  },
  'Linux': {
    'Quick Install': [
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      './scripts/install.sh',
      '',
      'umd --version',
    ],
    'pipx': [
      '# Install pipx if needed',
      'pip install --user pipx',
      '',
      '# Clone and install',
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'pipx install -e .',
    ],
    'pip': [
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'pip3 install -e .',
    ],
    'venv': [
      'git clone https://codeberg.org/nk2552003/umd.git',
      'cd umd',
      'python3 -m venv venv',
      'source venv/bin/activate',
      'pip install -r requirements.txt',
      'python ultimate_downloader.py',
    ]
  },
};

const COMMANDS = [
  { cmd: 'umd', desc: 'Interactive mode (easiest for beginners)' },
  { cmd: 'umd "https://youtube.com/watch?v=VIDEO_ID"', desc: 'Download a video' },
  { cmd: 'umd "URL" --audio-only --format mp3', desc: 'Download audio only as MP3' },
  { cmd: 'umd "URL" --quality 1080p', desc: 'Download in specific quality' },
  { cmd: 'umd "https://youtube.com/playlist?list=PLAYLIST_ID"', desc: 'Download entire playlist' },
  { cmd: 'umd "URL" --audio-only --embed-metadata --embed-thumbnail', desc: 'Download with metadata and thumbnail' },
  { cmd: 'umd --batch-file urls.txt --audio-only', desc: 'Batch download from file' },
  { cmd: 'umd --batch-file urls.txt --optimized-batch --max-concurrent 5', desc: 'Parallel batch download' },
  { cmd: 'umd "URL" --output /path/to/folder', desc: 'Custom output directory' },
  { cmd: 'umd "URL" --show-formats', desc: 'Show available formats' },
  { cmd: 'umd --help', desc: 'Show all available commands' },
  { cmd: 'umd --version', desc: 'Check installed version' },
];

export default function InstallationGuide() {
  const [os, setOs] = useState(OS_TABS[0].id);
  const [method, setMethod] = useState(METHOD_TABS[0]);
  const [copied, setCopied] = useState<string | null>(null);
  const [typedLines, setTypedLines] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    let currentLineIndex = 0;
    let currentCharIndex = 0;
    const targetLines = INSTALL_DATA[os][method] || [];
    const currentLines: string[] = [];
    
    setIsTyping(true);
    setTypedLines([]);

    const typeNextChar = () => {
      if (currentLineIndex >= targetLines.length) {
        setIsTyping(false);
        return;
      }

      const line = targetLines[currentLineIndex];
      
      // If it's an empty line, skip instantly
      if (line === '') {
        currentLines[currentLineIndex] = '';
        currentLineIndex++;
        currentCharIndex = 0;
        setTypedLines([...currentLines]);
        timeoutId = setTimeout(typeNextChar, 10);
        return;
      }

      // If we finished this line
      if (currentCharIndex >= line.length) {
        currentLineIndex++;
        currentCharIndex = 0;
        // Pause briefly at end of line
        timeoutId = setTimeout(typeNextChar, 80);
        return;
      }

      // Type next char
      if (currentLines[currentLineIndex] === undefined) {
        currentLines[currentLineIndex] = '';
      }
      
      currentLines[currentLineIndex] = line.substring(0, currentCharIndex + 1);
      setTypedLines([...currentLines]);
      
      currentCharIndex++;
      
      // Randomize typing speed for realism (10ms - 25ms)
      const delay = Math.random() * 15 + 5;
      timeoutId = setTimeout(typeNextChar, delay);
    };

    // Small delay before starting to type when tab changes
    timeoutId = setTimeout(typeNextChar, 200);

    return () => clearTimeout(timeoutId);
  }, [os, method]);

  function copyText(text: string, key: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(key);
      setTimeout(() => setCopied(null), 1800);
    });
  }

  // Use typedLines during typing, else full code
  const codeLines = isTyping ? typedLines : (INSTALL_DATA[os][method] || []);

  return (
    <section id="install" className="w-full bg-[var(--offblack)] text-[var(--offwhite)] relative overflow-hidden pt-24 md:pt-32 pb-0">
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-10 mix-blend-overlay pointer-events-none z-0"></div>

      {/* Background Doodles Layer */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-[0.15] text-[var(--offwhite)]">
        <svg aria-hidden="true" className="absolute w-[150px] md:w-[200px] h-[150px] md:h-[200px] top-12 left-[2%] md:left-[10%] -rotate-12" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="1">
          <path d="M50,10 C20,15 10,40 15,70 C20,95 60,95 85,75 C105,50 85,15 50,10" strokeLinecap="round"/>
        </svg>
        <svg aria-hidden="true" className="absolute w-24 md:w-32 h-24 md:h-32 top-[45%] md:top-[50%] left-[2%] md:left-[5%] rotate-[15deg]" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M0,50 Q25,10 50,50 T100,50" />
        </svg>
        <div className="absolute top-12 right-[5%] md:right-[15%] flex flex-col gap-2">
           <div className="flex gap-4">
              <span className="text-3xl md:text-4xl font-mono leading-none">+</span>
              <span className="text-3xl md:text-4xl font-mono leading-none mt-4">+</span>
           </div>
           <div className="flex gap-4 ml-6">
              <span className="text-3xl md:text-4xl font-mono leading-none">+</span>
              <span className="text-3xl md:text-4xl font-mono leading-none mt-2">+</span>
           </div>
        </div>
        <svg aria-hidden="true" className="absolute w-20 md:w-24 h-20 md:h-24 bottom-[10%] right-[2%] md:right-[8%] -rotate-12" viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
          <line x1="50" y1="10" x2="50" y2="90" />
          <line x1="10" y1="50" x2="90" y2="50" />
          <line x1="20" y1="20" x2="80" y2="80" />
          <line x1="20" y1="80" x2="80" y2="20" />
        </svg>
      </div>

      <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] relative z-10 flex flex-col gap-12 lg:gap-16">
      
        {/* Header */}
        <div className="mb-16 md:mb-24 flex flex-col items-center text-center">
          <div className="inline-block border-[3px] border-[var(--offwhite)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offwhite)] bg-[var(--cyan)] text-white font-bold">
            [ INSTALLATION ]
          </div>
          <h2 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter text-center uppercase leading-[0.9] mb-8">
            Up and running in <span className="text-transparent bg-clip-text bg-[url('/texture.webp')] bg-center bg-cover invert opacity-90 inline-block">seconds.</span>
          </h2>
          <p className="text-base md:text-lg lg:text-xl font-mono opacity-80 max-w-3xl mx-auto p-4">
            UMD requires Python 3.9+ and ffmpeg for audio conversion.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8 lg:gap-12 w-full items-start">
          
          {/* Code block area with Animated Terminal */}
          <div className="w-full lg:w-[55%] xl:w-[60%] flex flex-col transition-transform duration-500 hover:scale-[1.01] group/terminal">
            <div className="h-[350px] md:h-[480px] lg:h-[480px] border-[2px] md:border-[3px] border-[var(--offwhite)] bg-[var(--offblack)] shadow-[4px_4px_0px_var(--offwhite)] md:shadow-[8px_8px_0px_var(--offwhite)] hover:shadow-[8px_8px_0px_var(--cyan)] overflow-hidden flex flex-col rounded-none transition-shadow duration-500 relative">
              
              {/* Blurred Wallpaper Background */}
              <div className="absolute inset-0 bg-[url('/totoro_wallpaper.webp')] bg-cover bg-center opacity-40 blur-[4px] z-0 pointer-events-none scale-105"></div>
              {/* Dark overlay to ensure text readability */}
              <div className="absolute inset-0 bg-black/50 z-0 pointer-events-none"></div>

              {/* Terminal Header */}
              <div className="flex items-center justify-center px-4 py-3 border-b-[2px] md:border-b-[3px] border-[var(--offwhite)] bg-[#111]/70 backdrop-blur-md shrink-0 relative z-10">
                <div className="text-xs font-mono opacity-80 flex items-center gap-2">
                  <TerminalSquare className="w-3.5 h-3.5" /> root@umd-installer:~
                </div>
              </div>

              {/* OS Tabs */}
              <div className="flex overflow-x-auto border-b-[2px] md:border-b-[3px] border-[var(--offwhite)] [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] bg-[#1a1a1a]/60 backdrop-blur-md shrink-0 relative z-10">
                {OS_TABS.map(t => (
                  <button
                    key={t.id}
                    className={`flex items-center gap-2 md:gap-3 px-4 md:px-8 py-3 md:py-4 font-mono text-sm md:text-base lg:text-lg tracking-wider whitespace-nowrap transition-colors border-r-[2px] md:border-r-[3px] border-[var(--offwhite)] last:border-r-0 ${
                      os === t.id 
                        ? 'bg-[var(--cyan)]/90 text-white font-bold shadow-[inset_0_-4px_0_0_#fff]' 
                        : 'text-[var(--offwhite)] opacity-70 hover:bg-white/20 hover:opacity-100'
                    }`}
                    onClick={() => {
                      if(os !== t.id) setOs(t.id);
                    }}
                  >
                    <t.icon />
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Method Tabs (Sub-navigation) */}
              <div className="flex overflow-x-auto bg-[#222]/50 backdrop-blur-md border-b-[2px] md:border-b-[3px] border-[var(--offwhite)]/30 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] shrink-0 relative z-10">
                {METHOD_TABS.map(m => (
                  <button
                    key={m}
                    className={`px-4 md:px-6 py-2 font-mono text-xs md:text-sm whitespace-nowrap transition-colors ${
                      method === m 
                        ? 'text-[var(--cyan)] font-bold bg-white/10 border-b-2 border-[var(--cyan)]' 
                        : 'text-[var(--offwhite)] opacity-50 hover:bg-white/10 hover:opacity-100'
                    }`}
                    onClick={() => {
                      if(method !== m) setMethod(m);
                    }}
                  >
                    {m}
                  </button>
                ))}
              </div>

              {/* Code Area */}
              <div className="p-4 md:p-8 relative flex-1 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] group z-10">
                <button
                  className="absolute top-4 right-4 md:top-6 md:right-6 px-4 py-2 border-[2px] border-[var(--offwhite)] rounded-lg font-mono text-sm md:text-base bg-[var(--offblack)] hover:bg-[var(--offwhite)] hover:text-[var(--offblack)] transition-all duration-300 shadow-[2px_2px_0px_var(--offwhite)] hover:shadow-[4px_4px_0px_#fff] flex gap-2 items-center z-20 opacity-0 group-hover:opacity-100 focus:opacity-100"
                  onClick={() => copyText((INSTALL_DATA[os][method] || []).filter(l => l && !l.startsWith('#')).join('\n'), 'install')}
                >
                  {copied === 'install' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied === 'install' ? 'Copied' : 'Copy'}
                </button>
                
                <pre className="h-full w-full font-mono text-sm md:text-base lg:text-lg leading-loose overflow-y-auto overflow-x-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] pt-2 pb-2 text-blue-200">
                  {codeLines.map((line, i) => (
                    <div key={i} className={line.startsWith('#') ? 'opacity-50 text-green-400 font-normal' : 'font-bold whitespace-pre'}>
                      <span className={line.startsWith('#') ? '' : 'text-[var(--cyan)] opacity-70 mr-3 select-none'}>$</span>
                      {line}
                      {/* Blinking cursor on the active typing line */}
                      {isTyping && i === codeLines.length - 1 && (
                        <span className="inline-block w-2.5 h-5 bg-[var(--cyan)] ml-1 animate-pulse align-middle"></span>
                      )}
                    </div>
                  ))}
                  {/* Blinking cursor when idle */}
                  {!isTyping && (
                    <div className="mt-1">
                      <span className="text-[var(--cyan)] opacity-70 mr-3 select-none">$</span>
                      <span className="inline-block w-2.5 h-5 bg-[var(--cyan)] ml-1 animate-pulse align-middle opacity-50"></span>
                    </div>
                  )}
                </pre>
              </div>
            </div>
          </div>

          {/* Quick Commands */}
          <div className="w-full lg:w-[45%] xl:w-[40%] flex flex-col gap-6 lg:mt-0">
            <div className="h-[420px] md:h-[480px] lg:h-[480px] border-[2px] md:border-[3px] border-[var(--offwhite)] p-6 md:p-8 bg-[#1a1a1a] shadow-[4px_4px_0px_var(--offwhite)] md:shadow-[8px_8px_0px_var(--offwhite)] flex flex-col gap-6 rounded-none relative overflow-hidden group hover:shadow-[8px_8px_0px_var(--cyan)] transition-shadow duration-500">
              
              <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--cyan)] rounded-full blur-[100px] opacity-10 group-hover:opacity-30 transition-opacity duration-500 pointer-events-none"></div>

              <h3 className="font-mono text-base lg:text-lg uppercase tracking-widest opacity-80 flex items-center gap-3 shrink-0">
                <TerminalSquare className="w-5 h-5 text-[var(--cyan)]" /> Quick Commands
              </h3>
              
              <div className="flex flex-col gap-4 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none] pr-2">
                {COMMANDS.map((c, i) => (
                  <div 
                    key={i} 
                    className="group/cmd flex flex-col md:flex-row md:items-center gap-2 md:gap-6 border-l-[3px] border-[var(--offwhite)] hover:border-[var(--cyan)] pl-4 py-2 hover:bg-cyan-900/20 transition-all duration-300 hover:translate-x-2 rounded-r-lg cursor-pointer shrink-0"
                    onClick={() => copyText(c.cmd, `cmd-${i}`)}
                  >
                    <div className="flex items-center gap-3 w-auto md:min-w-[300px]">
                      <button
                        className="opacity-50 group-hover/cmd:opacity-100 transition-opacity text-[var(--cyan)]"
                        title="Copy command"
                      >
                        {copied === `cmd-${i}` ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                      </button>
                      <code className="font-mono text-sm md:text-base font-bold text-white group-hover/cmd:text-[var(--cyan)] transition-colors break-all">{c.cmd}</code>
                    </div>
                    <span className="text-xs md:text-sm font-mono opacity-70 group-hover/cmd:opacity-100 transition-opacity">{c.desc}</span>
                  </div>
                ))}
              </div>
            </div>
            
          </div>
        </div>
      </div>
      <div className="w-full mt-16 md:mt-24 bg-[var(--offwhite)]">
        <PixelStrip direction="down" primaryColor="var(--offblack)" secondaryColor="var(--accent-color)" />
      </div>
    </section>
  );
}
