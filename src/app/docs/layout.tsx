import DocsHeader from '@/components/DocsHeader';
import DocsSidebar from '@/components/DocsSidebar';
import { getDocSlugs } from '@/lib/docs';

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const slugs = getDocSlugs().map(slug => slug.replace(/\.md$/, ''));

  return (
    <div className="min-h-screen bg-[var(--offwhite)] text-[var(--offblack)] font-sans">
      <DocsHeader />
      <div className="container mx-auto px-4 md:px-12 lg:px-24 xl:px-32 max-w-[90rem] pt-32 pb-32">
        <div className="flex gap-12 items-start mt-12">
          <DocsSidebar docs={slugs} />
          <main className="flex-1 w-full min-w-0">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
