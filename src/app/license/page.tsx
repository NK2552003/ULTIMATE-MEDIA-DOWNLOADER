import { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Scale, FileText, Users, Globe, AlertCircle } from 'lucide-react';

export const metadata: Metadata = {
  title: 'License | UMD',
  description: 'UMD is licensed under the Apache License 2.0. Read the full terms and conditions here.',
};

const SECTIONS = [
  { num: '1', title: 'Definitions', content: '"License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.\n\n"Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.\n\n"Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity.\n\n"You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.\n\n"Source" form shall mean the preferred form for making modifications, including but not limited to software source code, documentation source, and configuration files.\n\n"Object" form shall mean any form resulting from mechanical transformation or translation of a Source form, including but not limited to compiled object code, generated documentation, and conversions to other media types.\n\n"Work" shall mean the work of authorship, whether in Source or Object form, made available under the License.\n\n"Derivative Works" shall mean any work, whether in Source or Object form, that is based on (or derived from) the Work.\n\n"Contributor" shall mean Licensor and any individual or Legal Entity on behalf of whom a Contribution has been received by Licensor and subsequently incorporated within the Work.' },
  { num: '2', title: 'Grant of Copyright License', content: 'Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works in Source or Object form.' },
  { num: '3', title: 'Grant of Patent License', content: 'Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work.' },
  { num: '4', title: 'Redistribution', content: 'You may reproduce and distribute copies of the Work or Derivative Works thereof in any medium, with or without modifications, and in Source or Object form, provided that You meet the following conditions:\n\n(a) You must give any other recipients of the Work or Derivative Works a copy of this License; and\n\n(b) You must cause any modified files to carry prominent notices stating that You changed the files; and\n\n(c) You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work; and\n\n(d) If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file.' },
  { num: '5', title: 'Submission of Contributions', content: 'Unless You explicitly state otherwise, any Contribution intentionally submitted for inclusion in the Work by You to the Licensor shall be under the terms and conditions of this License, without any additional terms or conditions. Notwithstanding the above, nothing herein shall supersede or modify the terms of any separate license agreement you may have executed with Licensor regarding such Contributions.' },
  { num: '6', title: 'Trademarks', content: 'This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file.' },
  { num: '7', title: 'Disclaimer of Warranty', content: 'Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.' },
  { num: '8', title: 'Limitation of Liability', content: 'In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by applicable law (such as deliberate and grossly negligent acts) or agreed to in writing, shall any Contributor be liable to You for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising as a result of this License or out of the use or inability to use the Work.' },
  { num: '9', title: 'Accepting Warranty or Additional Liability', content: 'While redistributing the Work or Derivative Works thereof, You may choose to offer, and charge a fee for, acceptance of support, warranty, indemnity, or other liability obligations and/or rights consistent with this License. However, in accepting such obligations, You may act only on your own behalf and on your sole responsibility, not on behalf of any other Contributor.' },
];

const KEY_PERMISSIONS = [
  { icon: '✓', label: 'Commercial use', color: 'bg-[#a3e635]' },
  { icon: '✓', label: 'Modification', color: 'bg-[#a3e635]' },
  { icon: '✓', label: 'Distribution', color: 'bg-[#a3e635]' },
  { icon: '✓', label: 'Patent use', color: 'bg-[#a3e635]' },
  { icon: '✓', label: 'Private use', color: 'bg-[#a3e635]' },
  { icon: '!', label: 'License notice required', color: 'bg-[#facc15]' },
  { icon: '!', label: 'State changes', color: 'bg-[#facc15]' },
  { icon: '✗', label: 'No warranty', color: 'bg-[#f87171]' },
  { icon: '✗', label: 'No trademark use', color: 'bg-[#f87171]' },
];

export default function LicensePage() {
  return (
    <main className="min-h-screen bg-[var(--offwhite)] text-[var(--offblack)] font-sans flex flex-col relative overflow-hidden">
      <Header />

      {/* Background Grid */}
      <div className="fixed inset-0 z-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'linear-gradient(var(--offblack) 2px, transparent 2px), linear-gradient(90deg, var(--offblack) 2px, transparent 2px)', backgroundSize: '60px 60px' }}></div>

      <div className="flex-grow relative z-10" style={{ paddingTop: '10rem' }}>

        {/* Hero Header */}
        <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] pb-16 md:pb-24 border-b-[3px] border-[var(--offblack)]">
          <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold">
            [ OPEN SOURCE ]
          </div>
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
            <div>
              <h1 className="text-5xl md:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-[0.9] mb-6">
                Apache<br />
                <span className="text-transparent bg-clip-text bg-[url('https://cdn.cosmos.so/00c1aedd-73e6-4e74-a278-2252a626bbff?format=jpeg')] bg-center bg-cover mix-blend-multiply inline-block">License 2.0</span>
              </h1>
              <p className="text-base md:text-lg lg:text-xl font-mono opacity-70 max-w-2xl leading-relaxed">
                UMD is free and open-source software, licensed under the Apache License, Version 2.0. You are free to use, modify, and distribute it under the terms below.
              </p>
            </div>
            <div className="shrink-0 flex flex-col gap-3">
              <div className="border-[2px] border-[var(--offblack)] px-5 py-3 font-mono text-xs bg-[var(--offwhite)] shadow-[3px_3px_0px_var(--offblack)] uppercase tracking-widest flex items-center gap-3">
                <Scale className="w-4 h-4 shrink-0" />
                Apache 2.0
              </div>
              <div className="border-[2px] border-[var(--offblack)] px-5 py-3 font-mono text-xs bg-[var(--offwhite)] shadow-[3px_3px_0px_var(--offblack)] uppercase tracking-widest flex items-center gap-3">
                <Globe className="w-4 h-4 shrink-0" />
                Copyright 2026 nk2552003
              </div>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] py-16 md:py-24 flex flex-col gap-16 md:gap-20">

          {/* Quick Reference */}
          <div>
            <div className="mb-8 flex flex-col gap-4">
              <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold self-start">
                [ QUICK REFERENCE ]
              </div>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-black uppercase tracking-tighter">At a glance</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4">
              {KEY_PERMISSIONS.map((p, i) => (
                <div key={i} className={`border-[2px] md:border-[3px] border-[var(--offblack)] ${p.color} p-4 md:p-5 shadow-[3px_3px_0px_var(--offblack)] flex flex-col gap-2`}>
                  <span className="font-mono text-xl font-black">{p.icon}</span>
                  <span className="font-mono text-xs md:text-sm font-bold uppercase tracking-wide">{p.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Copyright Notice Box */}
          <div className="border-[3px] border-[var(--offblack)] bg-[var(--offblack)] text-[var(--offwhite)] shadow-[8px_8px_0px_var(--accent-color)]">
            <div className="border-b-[3px] border-[var(--offwhite)]/30 px-6 md:px-10 py-4 flex items-center gap-3 bg-[#1a1a1a]">
              <div className="w-3 h-3 rounded-full bg-[#f87171]"></div>
              <div className="w-3 h-3 rounded-full bg-[#facc15]"></div>
              <div className="w-3 h-3 rounded-full bg-[#a3e635]"></div>
              <span className="font-mono text-xs opacity-50 ml-2 uppercase tracking-widest">LICENSE NOTICE</span>
            </div>
            <pre className="p-6 md:p-10 font-mono text-sm md:text-base leading-relaxed whitespace-pre-wrap text-[var(--offwhite)] opacity-90">{`Copyright 2026 nk2552003

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.`}</pre>
          </div>

          {/* Full License Text */}
          <div>
            <div className="mb-12 flex flex-col gap-4">
              <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)] font-bold self-start">
                [ FULL TEXT ]
              </div>
              <h2 className="text-3xl md:text-5xl font-black uppercase tracking-tighter">Terms and Conditions</h2>
              <p className="font-mono text-sm md:text-base opacity-80">Apache License, Version 2.0, January 2004 · http://www.apache.org/licenses/</p>
            </div>

            <div className="flex flex-col gap-6">
              {SECTIONS.map((s) => (
                <div key={s.num} className="border-[2px] md:border-[3px] border-[var(--offblack)] bg-[var(--offwhite)] shadow-[4px_4px_0px_var(--offblack)] hover:shadow-[8px_8px_0px_var(--offblack)] hover:-translate-y-0.5 transition-all duration-300 group overflow-hidden">
                  <div className="border-b-[2px] md:border-b-[3px] border-[var(--offblack)] px-6 md:px-8 py-4 flex items-center gap-4 bg-[var(--accent-color)] group-hover:bg-[var(--offblack)] group-hover:text-[var(--offwhite)] transition-colors">
                    <span className="font-mono text-2xl md:text-3xl font-black opacity-40 group-hover:opacity-80">{s.num}.</span>
                    <h3 className="text-lg md:text-2xl font-black uppercase tracking-tight">{s.title}</h3>
                  </div>
                  <div className="p-6 md:p-8">
                    {s.content.split('\n\n').map((para, j) => (
                      <p key={j} className="font-mono text-sm md:text-base opacity-80 leading-relaxed mb-4 last:mb-0">{para}</p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Appendix */}
          <div className="border-[3px] border-[var(--offblack)] p-8 md:p-12 bg-[var(--offwhite)] shadow-[8px_8px_0px_var(--offblack)]">
            <div className="font-mono text-xs tracking-[0.2em] uppercase opacity-80 mb-4">[ APPENDIX ]</div>
            <h3 className="text-2xl md:text-3xl font-black uppercase tracking-tighter mb-6">How to Apply This License to Your Work</h3>
            <p className="font-mono text-sm md:text-base opacity-80 leading-relaxed mb-6">
              To apply the Apache License to your work, attach the following boilerplate notice, with the fields enclosed by brackets replaced with your own identifying information.
            </p>
            <div className="border-[2px] border-[var(--offblack)] bg-[var(--offblack)] text-[var(--offwhite)] p-6 md:p-8">
              <pre className="font-mono text-xs md:text-sm leading-relaxed whitespace-pre-wrap opacity-90">{`Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.`}</pre>
            </div>
          </div>

          {/* CTA */}
          <div className="flex flex-col md:flex-row gap-4">
            <a
              href="http://www.apache.org/licenses/LICENSE-2.0"
              target="_blank"
              rel="noopener noreferrer"
              className="border-[3px] border-[var(--offblack)] px-6 md:px-8 py-3 md:py-4 font-mono font-black text-sm md:text-base uppercase tracking-widest bg-[var(--offblack)] text-[var(--offwhite)] hover:bg-[var(--accent-color)] hover:text-[var(--offblack)] shadow-[4px_4px_0px_var(--offblack)] hover:shadow-[6px_6px_0px_var(--offblack)] transition-all hover:-translate-y-0.5 text-center"
            >
              Read at apache.org ↗
            </a>
            <a
              href="https://codeberg.org/nk2552003/umd"
              target="_blank"
              rel="noopener noreferrer"
              className="border-[3px] border-[var(--offblack)] px-6 md:px-8 py-3 md:py-4 font-mono font-black text-sm md:text-base uppercase tracking-widest bg-[var(--offwhite)] text-[var(--offblack)] hover:bg-[var(--accent-color)] shadow-[4px_4px_0px_var(--offblack)] hover:shadow-[6px_6px_0px_var(--offblack)] transition-all hover:-translate-y-0.5 text-center"
            >
              View Source on Codeberg ↗
            </a>
          </div>

        </div>
      </div>

      <Footer />
    </main>
  );
}
