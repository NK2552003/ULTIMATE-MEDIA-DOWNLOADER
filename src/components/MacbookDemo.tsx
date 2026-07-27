'use client'
import { useEffect, useRef, useState } from 'react'
import { Folder, Terminal, Music, Play, SkipBack, SkipForward, FileAudio, FolderOpen, Heart, Apple, Wifi, Battery, Search, Settings2, Calendar, Map, MessageCircle } from 'lucide-react'
import { FaChrome } from 'react-icons/fa'
import styles from './MacbookDemo.module.css'

const SEQ: [number, string][] = [
  [0,     `<div class="ln c-gray">Last login: Thu May  7 10:46:55 on ttys001</div>`],
  [220,   `<div class="ln"><span class="c-green">▶</span> <span class="c-white">umd</span></div>`],
  [520,   `<div class="ascii-block"><div class="ln c-cyan" style="font-size:clamp(5px,.65vw,8px);letter-spacing:.3em;margin-bottom:2px">▶ ULTIMATE MEDIA DOWNLOADER ◀</div><div class="ascii-title">DOWNLOADER</div><div class="ln c-yellow" style="font-size:clamp(4px,.6vw,7px);letter-spacing:.1em;margin-top:2px">═══ v2.2.1 – Professional Edition ═══</div><div class="ln" style="font-size:clamp(4px,.65vw,7.5px);margin-top:1px"><span class="c-green">▶</span> Video Downloads &nbsp;<span class="c-cyan">♪</span> Audio Extraction &nbsp;<span class="c-yellow">⇌</span> Social Media &nbsp;<span class="c-orange">⚡</span> 50+ Platforms</div></div>`],
  [820,   `<div class="imode-box"><div class="ln c-purple" style="text-align:center;letter-spacing:.22em;font-size:clamp(4px,.62vw,8px);margin-bottom:3px">▶ I N T E R A C T I V E &nbsp; M O D E ◀</div><div class="ln c-white bold" style="text-align:center;font-size:clamp(4px,.62vw,7.5px)">Supported Platforms:</div><div style="display:flex;justify-content:center;gap:clamp(6px,2vw,22px);margin:2px 0;font-size:clamp(5px,.72vw,8px)"><span><span class="c-green">▶</span> <span class="c-white">YouTube</span></span><span><span class="c-cyan">♪</span> <span class="c-white">Spotify</span></span><span><span class="c-pink">◉</span> <span class="c-white">Instagram</span></span></div><div style="display:flex;justify-content:center;gap:clamp(6px,2vw,22px);margin:1px 0;font-size:clamp(5px,.72vw,8px)"><span><span class="c-cyan">♪</span> <span class="c-white">SoundCloud</span></span><span><span class="c-yellow">⇌</span> <span class="c-white">TikTok</span></span><span><span class="c-purple">◎</span> <span class="c-white">Twitter/X</span></span></div><div class="ln c-gray" style="text-align:center;font-size:clamp(4px,.58vw,7px)">... and 50+ more platforms!</div></div>`],
  [1220,  `<div class="ln"><span class="c-yellow">◎</span> Enter media URL or command: <span class="c-white">https://music.youtube.com/watch?v=usvVGXFIpTM</span></div>`],
  [1520,  `<div class="ln"><span class="c-cyan">ℹ</span> Starting download from: <span class="c-cyan" style="text-decoration:underline">https://music.youtube.com/watch?v=usvVGXFIpTM...</span></div>`],
  [1680,  `<div class="sep">══ ▶ Starting Download ══</div>`],
  [1850,  `<div class="dl-box"><div class="ln"><span class="c-white">Platform:</span> <span class="c-yellow bold">YOUTUBE</span></div><div class="ln"><span class="c-white">Quality:</span> <span class="c-green">best</span></div><div class="ln"><span class="c-white">Mode:</span> <span class="c-cyan">Audio</span></div><div class="ln"><span class="c-white">Format:</span> <span class="c-purple">FLAC</span></div></div>`],
  [2150,  `<div class="ln"><span class="c-red bold">?</span> <span class="c-white bold">What would you like to download?</span></div>`],
  [2300,  `<div class="ln"><span class="c-cyan">1.</span> 🎵 Audio Only <span class="c-gray">(MP3/FLAC)</span></div>`],
  [2400,  `<div class="ln"><span class="c-cyan">2.</span> 🎬 Video + Audio <span class="c-gray">(MP4)</span></div>`],
  [2500,  `<div class="ln"><span class="c-cyan">3.</span> ⚙️  Advanced <span class="c-gray">(Custom Settings)</span></div>`],
  [2700,  `<div class="ln"><span class="c-yellow">◎</span> Select download type <span class="c-cyan">(1):</span> <span class="c-white">1</span></div>`],
  [2860,  `<div class="ln"><span class="c-cyan">1.</span> MP3 <span class="c-gray">(Universal)</span></div>`],
  [2960,  `<div class="ln"><span class="c-cyan">2.</span> FLAC <span class="c-gray">(Lossless)</span></div>`],
  [3060,  `<div class="ln"><span class="c-cyan">3.</span> M4A <span class="c-gray">(Apple)</span></div>`],
  [3360,  `<div class="ln"><span class="c-yellow">◎</span> Select audio format <span class="c-cyan">(1):</span> <span class="c-white">2</span></div>`],
  [3560,  `<div class="ln"><span class="c-green">✓</span> <span class="c-white">Selected:</span> <span class="c-green">Audio only (FLAC)</span></div>`],
  [3760,  `<div class="ln"><span class="c-green">▶</span> Starting download...</div>`],
  [4000,  `<div class="ln c-white bold" style="margin-top:2px">▶ MEDIA INFO:</div>`],
  [4130,  `<div class="ln"><span class="c-green">▶</span> Title: <span class="c-white">Jo Tum Mere Ho</span></div>`],
  [4230,  `<div class="ln"><span class="c-yellow">◎</span> Duration: <span class="c-white">4:12</span></div>`],
  [4330,  `<div class="ln"><span class="c-purple">◎</span> Uploader: <span class="c-white">Anuv Jain</span></div>`],
  [4430,  `<div class="ln">👥 Views: <span class="c-white">105,135,631</span></div>`],
  [4530,  `<div class="ln">📅 Upload Date: <span class="c-white">2024-08-01</span></div>`],
  [4820,  `<div class="ln c-green" style="margin-top:2px">▶ Starting download...</div>`],
]

export default function MacbookDemo() {
  const innerRef = useRef<HTMLDivElement>(null)
  const outerRef = useRef<HTMLDivElement>(null)
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([])
  
  const [downloaded, setDownloaded] = useState(false)
  const [time, setTime] = useState('10:00 AM')

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  function nudge() {
    const outer = outerRef.current
    const inner = innerRef.current
    if (!outer || !inner) return
    const outerH = outer.offsetHeight
    const innerH = inner.offsetHeight
    const maxVisible = outerH * 0.9
    if (innerH > maxVisible) {
      inner.style.transform = `translateY(${maxVisible - innerH}px)`
    }
  }

  function addLine(html: string) {
    const inner = innerRef.current
    if (!inner) return
    const d = document.createElement('div')
    d.innerHTML = html
    inner.appendChild(d)
    nudge()
  }

  function addProgress() {
    const inner = innerRef.current
    if (!inner) return
    const wrap = document.createElement('div')
    wrap.className = styles.progWrap
    wrap.innerHTML = `<span class="c-cyan" id="pct" style="min-width:2.8em;font-size:clamp(6px,1vw,11px);font-family:var(--font-mono)">0%</span><div class="${styles.progBar}"><div class="${styles.progFill}" id="pf"></div></div><span class="c-gray" id="eta" style="font-size:clamp(5px,.85vw,10px);font-family:var(--font-mono)">ETA: calculating...</span>`
    inner.appendChild(wrap)
    nudge()
    let p = 0
    const etas = ['ETA: 4:02','ETA: 3:31','ETA: 2:58','ETA: 2:22','ETA: 1:48','ETA: 1:14','ETA: 0:48','ETA: 0:24','ETA: 0:08','Done!']
    const iv = setInterval(() => {
      p = Math.min(100, p + (Math.random() * 2.6 + 0.9))
      const pf = document.getElementById('pf') as HTMLElement
      const pctEl = document.getElementById('pct')
      const etaEl = document.getElementById('eta')
      if (pf) pf.style.width = p + '%'
      if (pctEl) pctEl.textContent = Math.round(p) + '%'
      if (etaEl) etaEl.textContent = etas[Math.min(Math.floor(p / 11), 9)]
      nudge()
      if (p >= 100) clearInterval(iv)
    }, 55)
  }

  function runSequence() {
    setDownloaded(false)
    if (innerRef.current) {
      innerRef.current.innerHTML = ''
      innerRef.current.style.transform = 'translateY(0)'
    }
    SEQ.forEach(([t, html]) => {
      const tid = setTimeout(() => addLine(html), t)
      timersRef.current.push(tid)
    })
    const pt = setTimeout(() => addProgress(), 5480)
    timersRef.current.push(pt)

    const endLines: [number, string][] = [
      [9700, `<div class="ln"><span class="c-green">✓</span> Download complete: <span class="c-cyan">Jo Tum Mere Ho.flac</span></div>`],
      [9900, `<div class="sep">🎊 ══ SUCCESS ══</div><div class="${styles.successBox}"><div class="ln c-green bold">✦ Download completed successfully! ✦</div><div class="ln c-orange">🎉 Your media is ready!</div></div>`],
      [10150,`<div class="ln">🗂  File saved: <span class="c-cyan">~/Downloads/UltimateDownloader/Jo Tum Mere Ho.flac</span></div>`],
      [10400,`<div class="ln c-gray" style="margin-top:2px">◉ Cleaning up intermediate files...</div>`],
      [10680,`<div class="ln"><span class="c-green">✓</span> No intermediate files to clean</div>`],
      [11150,`<div class="ln c-green bold" style="margin-top:2px">✓ All done!</div>`],
      [11400,`<div class="ln" style="margin-top:2px"><span class="c-yellow">↓</span> Download another file? <span class="c-gray">[y/n]</span> (y): <span class="cursor-blink"></span></div>`],
    ]
    endLines.forEach(([t, html]) => {
      const tid = setTimeout(() => addLine(html), t)
      timersRef.current.push(tid)
    })
    
    // Set downloaded state so file appears
    const dlTimeout = setTimeout(() => setDownloaded(true), 10150)
    timersRef.current.push(dlTimeout)

    const reload = setTimeout(() => runSequence(), 24000)
    timersRef.current.push(reload)
  }

  useEffect(() => {
    runSequence()
    window.addEventListener('resize', nudge)
    return () => {
      timersRef.current.forEach(clearTimeout)
      window.removeEventListener('resize', nudge)
    }
  }, [])

  return (
    <div className={styles.scene}>
      <div className={styles.macbook}>
        <div className={styles.lid}>
          <div className={styles.screenWrap}>
            
            {/* MacOS Desktop */}
            <div className={styles.desktop}>
              
              {/* Menu Bar (Top) */}
              <div className={styles.menubar}>
                <div className={styles.menuLeft}>
                  <div className={styles.menuItem}><Apple size={14} fill="currentColor" /></div>
                  <div className={styles.menuItem} style={{ fontWeight: 600 }}>Finder</div>
                  <div className={styles.menuItem}>File</div>
                  <div className={styles.menuItem}>Edit</div>
                  <div className={styles.menuItem}>View</div>
                  <div className={styles.menuItem}>Go</div>
                  <div className={styles.menuItem}>Window</div>
                  <div className={styles.menuItem}>Help</div>
                </div>
                <div className={styles.menuRight}>
                  <div className={styles.menuIcon}><Battery size={14} /></div>
                  <div className={styles.menuIcon}><Wifi size={14} /></div>
                  <div className={styles.menuIcon}><Search size={14} /></div>
                  <div className={styles.menuIcon}><Settings2 size={14} /></div>
                  <div className={styles.menuTime}>{time}</div>
                </div>
              </div>

              {/* Desktop Area where windows float */}
              <div className={styles.desktopArea}>
                
                {/* Terminal Window */}
                <div className={`${styles.window} ${styles.terminalWindow}`}>
                  <div className={styles.titlebar}>
                    <div className={styles.windowControls}>
                      <div className={`${styles.control} ${styles.close}`}></div>
                      <div className={`${styles.control} ${styles.minimize}`}></div>
                      <div className={`${styles.control} ${styles.maximize}`}></div>
                    </div>
                    <div className={styles.title}>
                      <FolderOpen size={10} style={{ marginRight: '4px', verticalAlign: 'middle', display: 'inline' }} /> 
                      nitishkumar — bash — 80x24
                    </div>
                  </div>
                  <div className={styles.termOuter} ref={outerRef}>
                    <div className={styles.termInner} ref={innerRef} />
                  </div>
                </div>

                {/* Finder Window (Ultimate Downloader Folder) */}
                <div className={`${styles.window} ${styles.finderWindow}`}>
                  <div className={styles.titlebar}>
                    <div className={styles.windowControls}>
                      <div className={`${styles.control} ${styles.close}`}></div>
                      <div className={`${styles.control} ${styles.minimize}`}></div>
                      <div className={`${styles.control} ${styles.maximize}`}></div>
                    </div>
                    <div className={styles.title}>Ultimate Downloader</div>
                  </div>
                  <div className={styles.finderBody}>
                    <div className={styles.finderSidebar}>
                      <div className={styles.sidebarItem}><Heart size={12} color="#ff3b30"/> Favorites</div>
                      <div className={styles.sidebarItem}><FolderOpen size={12} color="#4facfe"/> Downloads</div>
                      <div className={styles.sidebarItem}><FolderOpen size={12} color="#4facfe"/> Documents</div>
                      <div className={styles.sidebarItem}><FolderOpen size={12} color="#4facfe"/> Desktop</div>
                    </div>
                    <div className={styles.finderMain}>
                      <div className={styles.finderToolbar}>
                        <div className={styles.toolbarPath}>Downloads {'>'} UltimateDownloader</div>
                      </div>
                      <div className={styles.finderItems}>
                        {/* Always present file */}
                        <div className={styles.fileItem}>
                          <div className={styles.fileIconFolder}>
                            <Folder size={28} color="#4facfe" fill="#bbedff" />
                          </div>
                          <div className={styles.fileName}>Archive</div>
                        </div>
                        {/* File that appears after download */}
                        {downloaded && (
                          <div className={styles.fileItem} style={{ animation: 'popIn 0.3s ease-out' }}>
                            <div className={styles.fileIconAudio}>
                              <FileAudio size={28} color="#ff3b30" />
                            </div>
                            <div className={styles.fileName}>Jo Tum Mere Ho.flac</div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Music Player Window (Appears when playing) */}
                <div className={`${styles.window} ${styles.musicPlayerWindow} ${downloaded ? styles.musicVisible : ''}`}>
                  <div className={styles.titlebar}>
                    <div className={styles.windowControls}>
                      <div className={`${styles.control} ${styles.close}`}></div>
                      <div className={`${styles.control} ${styles.minimize}`}></div>
                      <div className={`${styles.control} ${styles.maximize}`}></div>
                    </div>
                    <div className={styles.title}>Music</div>
                  </div>
                  <div className={styles.musicContent}>
                    <div className={styles.albumArt}>
                      <Music size={24} color="#fff" style={{ opacity: 0.5 }} />
                    </div>
                    <div className={styles.musicInfo}>
                      <div className={styles.songTitle}>Jo Tum Mere Ho</div>
                      <div className={styles.songArtist}>Anuv Jain</div>
                      <div className={styles.controls}>
                        <SkipBack size={14} />
                        <Play size={14} fill="currentColor" />
                        <SkipForward size={14} />
                      </div>
                    </div>
                  </div>
                </div>

              </div>

              {/* Dock (Bottom Center) */}
              <div className={styles.dockWrapper}>
                <div className={styles.dock}>
                  <div className={`${styles.dockIcon} ${styles.active}`} style={{ background: '#f5f5f5' }}>
                    <Folder size={20} color="#007aff" fill="#99ccff" />
                  </div>
                  <div className={`${styles.dockIcon} ${styles.active}`} style={{ background: '#333' }}>
                    <Terminal size={20} color="#fff" />
                  </div>
                  <div className={styles.dockIcon} style={{ background: '#ff3b30' }}>
                    <Music size={20} color="#fff" />
                  </div>
                  <div className={styles.dockIcon} style={{ background: '#fff' }}>
                    <FaChrome size={20} color="#4285F4" />
                  </div>
                  <div className={styles.dockIcon} style={{ background: '#27c93f' }}>
                    <MessageCircle size={20} color="#fff" fill="#fff" />
                  </div>
                </div>
              </div>

            </div>
            
          </div>
        </div>
        <div className={styles.base}>
          <div className={styles.trackpad} />
        </div>
        <div className={styles.shadow} />
        <div className={styles.outerFade} />
      </div>
    </div>
  )
}
