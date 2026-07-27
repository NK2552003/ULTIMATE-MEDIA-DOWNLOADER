import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

const docsDirectory = path.join(process.cwd(), 'public/documentations');

export function getDocSlugs() {
  if (!fs.existsSync(docsDirectory)) {
    return [];
  }
  return fs.readdirSync(docsDirectory).filter(file => file.endsWith('.md'));
}

export function getDocBySlug(slug: string) {
  const realSlug = slug.replace(/\.md$/, '');
  const fullPath = path.join(docsDirectory, `${realSlug}.md`);
  
  try {
    const fileContents = fs.readFileSync(fullPath, 'utf8');
    const { data, content } = matter(fileContents);

    return {
      slug: realSlug,
      frontmatter: data,
      content,
    };
  } catch (error) {
    return null;
  }
}

export function getAllDocs() {
  const slugs = getDocSlugs();
  const docs = slugs
    .map((slug) => getDocBySlug(slug))
    .filter(Boolean) as { slug: string; frontmatter: { [key: string]: any }; content: string }[];
  return docs;
}
