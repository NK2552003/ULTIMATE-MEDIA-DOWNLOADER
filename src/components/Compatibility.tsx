import { Apple, Play, Music, Camera, MessageSquare, Zap, Tv, Film, MonitorPlay, Radio, Headphones, Smartphone, Image as ImageIcon, Flame, AudioLines, Monitor, Globe } from 'lucide-react'
import { SiSpotify, SiTiktok, SiTed, SiRumble, SiReddit, SiPinterest, SiPeertube, SiKick, SiInstagram, SiFlickr, SiDailymotion, SiTwitch, SiTumblr, SiVimeo, SiApplemusic, SiAudiomack } from 'react-icons/si'
import { FaApple, FaAmazon, FaLinkedin, FaYoutube } from 'react-icons/fa'
import Image from 'next/image'
import PixelStrip from './PixelStrip'

const basePath = '';

export default function Compatibility() {
  return (
    <div className="w-full relative flex flex-col items-center mt-24 md:mt-32">
      <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] flex flex-col gap-24 relative z-10 text-[var(--offblack)]">
        
        {/* Works on any Mac */}
        <div className="w-full border-[3px] border-[var(--offblack)] shadow-[12px_12px_0px_var(--offblack)] overflow-hidden relative group min-h-[300px] flex items-center bg-[var(--offwhite)]">
          <Image 
            src={`${basePath}/totoro_mac.jpg`}
            alt="Totoro using a Mac" 
            width={1200}
            height={400}
            className="absolute inset-0 w-full h-full object-cover object-[100%_center] scale-110 -translate-y-5 filter grayscale contrast-125 opacity-80 group-hover:scale-[1.15] group-hover:-translate-y-6 group-hover:opacity-100 transition-all duration-700"
          />
          <div className="absolute inset-0 bg-white/70 backdrop-blur-md md:hidden pointer-events-none z-0"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-[var(--offwhite)] via-[var(--offwhite)] via-50% to-transparent w-full md:w-[75%] lg:w-[55%] pointer-events-none z-0 hidden md:block"></div>
          
          <div className="p-8 md:p-12 lg:p-16 flex flex-col gap-8 items-start w-full md:w-[60%] lg:w-[45%] relative z-10">
            <div className="w-10 h-10 md:w-16 md:h-16 border-[2px] md:border-[3px] border-[var(--offblack)] bg-[var(--accent-color)] flex items-center justify-center shrink-0 shadow-[2px_2px_0px_var(--offblack)] md:shadow-[4px_4px_0px_var(--offblack)]">
              <Apple fill="currentColor" className="w-5 h-5 md:w-9 md:h-9" />
            </div>
            <div className="flex flex-col gap-6">
              <h3 className="text-3xl md:text-5xl font-bold uppercase tracking-tight leading-none text-[var(--offblack)]">Works on any Mac</h3>
              <p className="font-mono text-sm md:text-base opacity-90 max-w-xl leading-relaxed text-[var(--offblack)]">
                MacBook with a notch? Hover to open. Also works on older Mac models. Same app, same features, every Mac running macOS 10 Sequoia or later.
              </p>
              <div className="flex flex-wrap gap-3 mt-2">
                {['MacBook Pro', 'MacBook Air', 'Mac', 'Mac Mini', 'Mac Studio'].map(mac => (
                  <span key={mac} className="px-4 py-2 border-[2px] border-[var(--offblack)] bg-white shadow-[4px_4px_0px_var(--offblack)] text-xs md:text-sm font-bold uppercase tracking-wider text-[var(--offblack)]">
                    {mac}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Platforms */}
        <div className="w-full flex flex-col items-center gap-16">
          <div className="text-center flex flex-col items-center gap-6">
             <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase shadow-[4px_4px_0px_var(--offblack)] bg-white">
                [ SUPPORTED PLATFORMS ]
              </div>
            <h2 className="text-6xl md:text-8xl lg:text-9xl font-bold tracking-tighter text-center uppercase leading-[0.9] mb-8">
              Built for <span className="text-transparent bg-clip-text bg-[var(--offblack)] bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-contain bg-blend-screen relative inline-block">what</span><br/>you use
            </h2>
            <p className="text-base md:text-xl font-mono opacity-80 max-w-3xl mx-auto p-4 text-center">
              UMD uses yt-dlp under the hood — supporting virtually every major video and audio platform.
            </p>
          </div>

          <div className="flex flex-wrap justify-center items-center gap-4 md:gap-8 w-full max-w-6xl mx-auto opacity-80 text-[var(--offblack)]">
            <PlatformIcon icon={SiSpotify} name="Spotify" />
            <PlatformIcon icon={SiApplemusic} name="Apple Music" />
            <PlatformIcon icon={SiTiktok} name="TikTok" />
            <PlatformIcon icon={SiInstagram} name="Instagram" />
            <PlatformIcon icon={SiTumblr} name="Tumblr" />
            
            <PlatformIcon icon={FaLinkedin} name="LinkedIn" />
            <PlatformIcon icon={SiReddit} name="Reddit" />
            <PlatformIcon icon={SiPinterest} name="Pinterest" />
            <PlatformIcon icon={FaAmazon} name="Amazon Music" />
            
            <PlatformIcon icon={SiTwitch} name="Twitch" />
            <PlatformIcon icon={SiRumble} name="Rumble" />
            <PlatformIcon icon={SiVimeo} name="Vimeo" />
            <PlatformIcon icon={SiDailymotion} name="Dailymotion" />
            
            <PlatformIcon icon={SiKick} name="Kick" />
            <PlatformIcon icon={SiTed} name="TED" />
            <PlatformIcon icon={SiFlickr} name="Flickr" />
            <PlatformIcon icon={SiPeertube} name="PeerTube" />
            <PlatformIcon icon={SiAudiomack} name="Audiomack" />
            <PlatformIcon icon={FaApple} name="Apple Podcasts" />
            <PlatformIcon icon={FaYoutube} name="YouTube" />
            
            {/* Fallback generics */}
            <PlatformIcon icon={Flame} name="Adult Sites" />
            <PlatformIcon icon={Globe} name="JioSaavn & Gaana" />
            <PlatformIcon icon={Zap} name="TrillerTV & More" />
          </div>
        </div>

        {/* Target Audiences Grid */}
        <div className="w-full grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-8">
          <AudienceCard 
            title="Developers" 
            description="Save API keys, terminal output, code snippets, and reference docs without switching context." 
            image={`${basePath}/totoro_developer.jpg`}
          />
          <AudienceCard 
            title="Music lovers" 
            description="Collect tracks, albums, and playlists in lossless FLAC. Metadata preserved. Library stays organized." 
            image={`${basePath}/totoro_music.jpg`}
          />
          <AudienceCard 
            title="Content creators" 
            description="Download reference footage, pull stock video, grab audio stems — all without leaving your terminal." 
            image={`${basePath}/totoro_creator.jpg`}
          />
          <AudienceCard 
            title="Everyone" 
            description="If you've ever wanted to keep a video or song locally, UMD does it cleanly and without bloat." 
            image={`${basePath}/totoro_everyone.jpg`}
          />
        </div>
        
      </div>
      
      {/* Full-width Pixel Strip at the bottom */}
      <div className="w-full mt-12 md:mt-24">
        <PixelStrip direction="up" />
      </div>
    </div>
  )
}

function PlatformIcon({ icon: Icon, name }: { icon: any, name: string }) {
  return (
    <div className="relative group cursor-help flex justify-center p-1 md:p-2">
      <Icon className="w-6 h-6 md:w-9 md:h-9 group-hover:scale-110 transition-transform duration-300" />
      
      {/* Tooltip */}
      <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none bg-white text-[var(--offblack)] text-[10px] md:text-xs font-bold uppercase tracking-wider py-1.5 px-3 shadow-[4px_4px_0px_var(--offblack)] border-[2px] border-[var(--offblack)] z-50 whitespace-nowrap">
        {name}
      </div>
    </div>
  )
}

function AudienceCard({ title, description, image }: { title: string, description: string, image?: string }) {
  return (
    <div className="relative w-full aspect-[4/5] border-[3px] border-[var(--offblack)] shadow-[8px_8px_0px_var(--offblack)] hover:shadow-[12px_12px_0px_var(--offblack)] hover:-translate-y-1 transition-all group overflow-hidden bg-[var(--offblack)]">
      {image && (
        <Image 
          src={image} 
          alt={title} 
          width={400}
          height={500}
          loading="lazy"
          className="absolute inset-0 w-full h-full object-cover filter grayscale contrast-125 opacity-80 group-hover:scale-105 group-hover:opacity-100 transition-all duration-700" 
        />
      )}
      
      {/* Overlay gradient for text readability */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-80 group-hover:opacity-80 transition-opacity duration-500"></div>

      {/* Blurred text container at the bottom */}
      <div className="absolute bottom-0 left-0 right-0 p-3 md:p-6 backdrop-blur-md bg-black/30 border-t-[3px] border-[var(--offblack)] translate-y-4 group-hover:translate-y-0 transition-transform duration-500 flex flex-col gap-2 md:gap-3 text-white">
        <h3 className="text-sm md:text-2xl font-bold uppercase tracking-tight leading-none">
          {title}
        </h3>
        <div className="w-full h-[2px] bg-white opacity-30"></div>
        <p className="font-mono text-[10px] md:text-sm opacity-90 leading-tight md:leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  )
}
