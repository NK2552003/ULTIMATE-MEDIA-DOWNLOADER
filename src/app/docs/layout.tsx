import type { Metadata } from 'next';
import DocsHeader from '@/components/DocsHeader';
import DocsSidebar from '@/components/DocsSidebar';
import { getDocSlugs } from '@/lib/docs';

export const metadata: Metadata = {
  title: {
    default: "Documentation",
    template: "%s | UMD Docs",
  },
  description:
    "Complete documentation for Ultimate Media Downloader. Installation guides, CLI references, configuration, platform support, and advanced usage.",
  openGraph: {
    title: "Documentation — Ultimate Media Downloader",
    description: "Complete installation, configuration, and usage documentation for UMD.",
    url: "https://ultimate-media-downloader.fun/docs",
    images: [{ url: "https://ultimate-media-downloader.fun/og-image.jpg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "UMD Documentation",
    description: "Complete documentation for Ultimate Media Downloader.",
    images: ["https://ultimate-media-downloader.fun/og-image.jpg"],
  },
  alternates: {
    canonical: "https://ultimate-media-downloader.fun/docs",
  },
};

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
