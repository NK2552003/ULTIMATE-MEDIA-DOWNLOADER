import { getDocBySlug } from '@/lib/docs';
import { parseChangelog } from '@/lib/changelog';
import ChangelogTimeline from '@/components/ChangelogTimeline';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Changelog | UMD',
};

export default function ChangelogPage() {
  const doc = getDocBySlug('CHANGELOG');

  if (!doc) {
    notFound();
  }

  const releases = parseChangelog(doc.content);

  return (
    <main className="min-h-screen bg-[var(--offwhite)] bg-grid-pattern text-[var(--offblack)] font-sans flex flex-col relative overflow-hidden">
      <Header />
      
      <div 
        className="flex-grow container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] pb-32"
        style={{ paddingTop: '12rem' }}
      >
        <div className="mb-16 text-center">
          <div className="inline-block border-[3px] border-[var(--offblack)] px-4 py-1 font-mono text-sm tracking-[0.2em] uppercase mb-8 shadow-[4px_4px_0px_var(--offblack)] bg-[var(--accent-color)]">
            [ UPDATES & FIXES ]
          </div>
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none">
            Changelog
          </h1>
        </div>
        
        <ChangelogTimeline releases={releases} />
      </div>

      <Footer />
    </main>
  );
}
