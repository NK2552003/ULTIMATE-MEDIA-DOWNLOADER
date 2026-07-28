"use client";

import { ChangelogRelease } from "@/lib/changelog";
import ReactMarkdown from "react-markdown";

const categoryColors: Record<string, string> = {
  "Added": "bg-[#a3e635] text-black", // Lime
  "Changed": "bg-[#facc15] text-black", // Yellow
  "Fixed": "bg-[#fb923c] text-black", // Orange
  "Removed": "bg-[#f87171] text-black", // Red
  "Technical Changes": "bg-[#c084fc] text-black", // Purple
};

function getCategoryColor(name: string) {
  if (categoryColors[name]) return categoryColors[name];
  if (name.startsWith("Issue")) return "bg-[#38bdf8] text-black"; // Sky blue for issues
  return "bg-[var(--offwhite)] text-black";
}

const Doodles = [
  // Git Branch
  (props: React.SVGProps<SVGSVGElement>) => (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="square" strokeLinejoin="miter" {...props}>
      <line x1="6" y1="3" x2="6" y2="21"></line>
      <circle cx="6" cy="6" r="3" fill="currentColor"></circle>
      <circle cx="6" cy="18" r="3" fill="currentColor"></circle>
      <path d="M18 9a9 9 0 0 1-9 9"></path>
      <circle cx="18" cy="9" r="3" fill="currentColor"></circle>
    </svg>
  ),
  // Code Brackets
  (props: React.SVGProps<SVGSVGElement>) => (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="square" strokeLinejoin="miter" {...props}>
      <polyline points="16 18 22 12 16 6"></polyline>
      <polyline points="8 6 2 12 8 18"></polyline>
    </svg>
  ),
  // Sticky Note
  (props: React.SVGProps<SVGSVGElement>) => (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="square" strokeLinejoin="miter" {...props}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
      <polyline points="10 9 9 9 8 9"></polyline>
    </svg>
  ),
  // Terminal / Command Prompt
  (props: React.SVGProps<SVGSVGElement>) => (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="square" strokeLinejoin="miter" {...props}>
      <polyline points="4 17 10 11 4 5"></polyline>
      <line x1="12" y1="19" x2="20" y2="19"></line>
    </svg>
  )
];

export default function ChangelogTimeline({ releases }: { releases: ChangelogRelease[] }) {
  return (
    <div className="relative w-full max-w-[120rem] px-4 md:px-8 mx-auto py-12">
      {/* Center Line on Desktop, Left on Mobile */}
      <div className="absolute left-[24px] md:left-1/2 top-0 bottom-0 w-[4px] bg-[var(--offblack)] md:-translate-x-1/2 z-0"></div>

      <div className="space-y-32 md:space-y-48 relative z-10">
        {releases.map((release, index) => {
          const isEven = index % 2 === 0;
          const DoodleSVG = Doodles[index % Doodles.length];

          return (
            <div key={release.version} className={`relative flex flex-col items-start w-full group pl-[48px] md:pl-0 ${isEven ? 'md:flex-row' : 'md:flex-row-reverse'}`}>
              
              {/* Timeline Dot */}
              <div className="absolute left-[16px] md:left-1/2 top-2 md:top-0 w-6 h-6 bg-[var(--accent-color)] border-[3px] border-[var(--offblack)] md:-translate-x-1/2 z-10 rounded-none group-hover:scale-150 transition-transform duration-300"></div>

              {/* Desktop Version, Date, and Floating Doodle */}
              <div className={`hidden md:block w-1/2 ${isEven ? 'pr-12 lg:pr-16 text-right' : 'pl-12 lg:pl-16 text-left'} pt-1 relative`}>
                
                {/* Floating Doodle */}
                <div className={`absolute top-12 ${isEven ? 'left-12 2xl:left-32' : 'right-12 2xl:right-32'} w-32 h-32 opacity-10 hover:opacity-100 transition-opacity duration-500 z-0 rotate-[-5deg] pointer-events-none text-[var(--offblack)]`}>
                  <DoodleSVG className="w-full h-full drop-shadow-[4px_4px_0px_rgba(58,58,56,0.3)]" />
                </div>

                <div className="sticky inline-block relative z-10" style={{ top: '12rem' }}>
                  <h2 className="text-4xl md:text-6xl lg:text-7xl font-black uppercase tracking-tighter leading-none mb-2">
                    v{release.version}
                  </h2>
                  <div className="text-lg md:text-xl lg:text-2xl font-mono tracking-widest font-bold opacity-80 uppercase">
                    {release.date}
                  </div>
                </div>
              </div>

              {/* Mobile Version & Date */}
              <div className="md:hidden mb-6 w-full pl-8">
                <h2 className="text-4xl font-black uppercase tracking-tighter leading-none mb-2">
                  v{release.version}
                </h2>
                <div className="text-base font-mono tracking-widest font-bold opacity-80 uppercase">
                  {release.date}
                </div>
              </div>

              {/* Content Card */}
              <div className={`w-full md:w-1/2 ${isEven ? 'md:pl-12 lg:pl-16' : 'md:pr-12 lg:pr-16'}`}>
                <div className="border-[3px] border-[var(--offblack)] shadow-[8px_8px_0px_var(--offblack)] bg-white p-6 md:p-12 lg:p-16 transition-transform duration-300 hover:-translate-y-1 hover:shadow-[12px_12px_0px_var(--offblack)] w-full">
                  
                  {release.description && (
                    <div className="mb-10 prose prose-base md:prose-lg prose-p:font-medium prose-p:leading-relaxed max-w-none text-[var(--offblack)] break-words [&_a]:break-all [&_code]:break-all">
                      <ReactMarkdown>{release.description}</ReactMarkdown>
                    </div>
                  )}

                  <div className="space-y-10">
                    {release.categories.map((category) => (
                      <div key={category.name}>
                        <h3 className={`inline-block border-[2px] border-[var(--offblack)] px-4 py-1.5 font-mono text-sm md:text-base tracking-wider uppercase font-bold mb-6 shadow-[3px_3px_0px_var(--offblack)] ${getCategoryColor(category.name)}`}>
                          {category.name}
                        </h3>
                        <ul className="space-y-4">
                          {category.items.map((item, i) => (
                            <li key={i} className="flex items-start">
                              <span className="shrink-0 w-3 h-3 bg-[var(--offblack)] mt-2 mr-4 block"></span>
                              <div className="prose prose-base md:prose-lg max-w-none font-medium text-[var(--offblack)] [&_strong]:font-black [&_strong]:text-[var(--offblack)] break-words [&_a]:break-all [&_code]:break-all">
                                <ReactMarkdown>{item}</ReactMarkdown>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>

                </div>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}
