"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import { Link as LucideLink } from 'lucide-react';
import Mermaid from './Mermaid';

interface MarkdownRendererProps {
  content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="max-w-none text-[var(--offblack)] bg-[var(--offwhite)] 
      [&_h1]:scroll-mt-48 [&_h1]:font-black [&_h1]:uppercase [&_h1]:tracking-tighter [&_h1]:text-5xl [&_h1]:mb-8 [&_h1]:mt-12 [&_h1]:border-b-4 [&_h1]:border-[var(--offblack)] [&_h1]:pb-4
      [&_h2]:scroll-mt-48 [&_h2]:font-bold [&_h2]:uppercase [&_h2]:tracking-tighter [&_h2]:text-4xl [&_h2]:mt-10 [&_h2]:mb-6 [&_h2]:border-b-2 [&_h2]:border-[var(--offblack)] [&_h2]:pb-2
      [&_h3]:scroll-mt-48 [&_h3]:font-bold [&_h3]:uppercase [&_h3]:tracking-tighter [&_h3]:text-3xl [&_h3]:mt-8 [&_h3]:mb-4
      [&_h4]:scroll-mt-48 [&_h4]:font-bold [&_h4]:uppercase [&_h4]:tracking-tighter [&_h4]:text-2xl [&_h4]:mt-6 [&_h4]:mb-4
      [&_p]:text-xl [&_p]:leading-relaxed [&_p]:mb-6
      [&_a]:text-[var(--offblack)] [&_a]:font-bold [&_a]:underline [&_a]:decoration-2 [&_a]:underline-offset-4 hover:[&_a]:bg-[var(--accent-color)] hover:[&_a]:no-underline
      [&_strong]:font-bold [&_strong]:text-[var(--offblack)]
      [&_ul]:list-disc [&_ul]:pl-8 [&_ul]:text-xl [&_ul]:mb-6
      [&_ol]:list-decimal [&_ol]:pl-8 [&_ol]:text-xl [&_ol]:mb-6
      [&_li]:my-2
      [&_blockquote]:border-l-8 [&_blockquote]:border-[var(--offblack)] [&_blockquote]:pl-6 [&_blockquote]:py-2 [&_blockquote]:bg-[var(--accent-color)] [&_blockquote]:italic [&_blockquote]:font-medium
      [&_code]:text-[var(--offwhite)] [&_code]:bg-[var(--offblack)] [&_code]:px-2 [&_code]:py-1 [&_code]:font-mono [&_code]:text-base [&_code]:font-normal [&_code]:shadow-[2px_2px_0px_var(--accent-color)]
      [&_pre]:bg-[var(--offblack)] [&_pre]:text-[var(--offwhite)] [&_pre]:p-6 [&_pre]:font-mono [&_pre]:text-sm [&_pre]:overflow-x-auto [&_pre]:border-2 [&_pre]:border-[var(--accent-color)] [&_pre]:shadow-[6px_6px_0px_var(--offblack)] [&_pre]:my-8 [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_pre_code]:shadow-none [&_pre_code]:text-[var(--offwhite)]
      [&_img]:border-[4px] [&_img]:border-[var(--offblack)] [&_img]:shadow-[8px_8px_0px_var(--offblack)] [&_img]:my-8
      [&_table]:w-full [&_table]:border-collapse [&_table]:border-2 [&_table]:border-[var(--offblack)] [&_table]:mb-8
      [&_th]:border-2 [&_th]:border-[var(--offblack)] [&_th]:bg-[var(--offblack)] [&_th]:text-[var(--offwhite)] [&_th]:p-3 [&_th]:text-left [&_th]:font-bold [&_th]:uppercase [&_th]:tracking-wider
      [&_td]:border-2 [&_td]:border-[var(--offblack)] [&_td]:p-3
      [&_hr]:border-2 [&_hr]:border-[var(--offblack)] [&_hr]:my-12">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[
          rehypeRaw,
          rehypeSlug,
          [rehypeAutolinkHeadings, { behavior: 'wrap' }],
        ]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            
            if (!inline && match && match[1] === 'mermaid') {
              return <Mermaid chart={String(children).replace(/\n$/, '')} />;
            }
            
            // For inline code, we don't apply pre styles.
            return !inline ? (
              <code className={className} {...props}>
                {children}
              </code>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
