import { notFound } from 'next/navigation';
import { getDocBySlug, getDocSlugs } from '@/lib/docs';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import TableOfContents from '@/components/TableOfContents';
import { Metadata } from 'next';
import GithubSlugger from 'github-slugger';

export async function generateStaticParams() {
  const slugs = getDocSlugs();
  return slugs.map((slug) => ({
    slug: slug.replace(/\.md$/, ''),
  }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const doc = getDocBySlug(slug);
  if (!doc) {
    return { title: 'Not Found' };
  }
  return {
    title: `${doc.slug.toUpperCase()} | UMD Documentation`,
  };
}

export default async function DocPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const doc = getDocBySlug(slug);

  if (!doc) {
    notFound();
  }

  // Strip existing manual Table of Contents
  const contentWithoutTOC = doc.content.replace(/##\s+Table of Contents[\s\S]*?(?=(##\s|---|$))/i, '');

  const slugger = new GithubSlugger();
  
  // Extract headings (## and ###)
  const headings = Array.from(contentWithoutTOC.matchAll(/^(#{2,3})\s+(.*)$/gm)).map(match => ({
    level: match[1].length,
    text: match[2].replace(/\[(.*?)\]\(.*?\)/g, '$1'), // Remove markdown links in headings
    slug: slugger.slug(match[2].replace(/\[(.*?)\]\(.*?\)/g, '$1'))
  }));

  return (
    <>
      <div className="flex gap-12 items-start relative w-full">
        <article className="border-[3px] border-[var(--offblack)] shadow-[8px_8px_0px_var(--offblack)] bg-[var(--offwhite)] p-8 md:p-16 mb-24 relative flex-1 min-w-0 mt-16">
          <div className="absolute top-0 right-0 bg-[var(--offblack)] text-[var(--offwhite)] font-mono text-sm tracking-[0.2em] px-4 py-2 uppercase font-bold">
            {doc.slug}.md
          </div>
          <MarkdownRenderer content={contentWithoutTOC} />
        </article>
        
        <TableOfContents headings={headings} />
      </div>
    </>
  );
}
