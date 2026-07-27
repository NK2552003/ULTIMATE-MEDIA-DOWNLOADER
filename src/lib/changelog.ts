export type ChangelogCategory = {
  name: string;
  items: string[];
};

export type ChangelogRelease = {
  version: string;
  date: string;
  description: string;
  categories: ChangelogCategory[];
};

export function parseChangelog(markdown: string): ChangelogRelease[] {
  const releases: ChangelogRelease[] = [];
  
  // Split by ## Version to get release blocks
  const versionBlocks = markdown.split(/^## Version /m).slice(1);
  
  for (const block of versionBlocks) {
    const lines = block.split('\n');
    
    // First line is the version number
    const version = lines[0].trim();
    
    let date = '';
    let description = '';
    const categories: ChangelogCategory[] = [];
    
    let currentCategory: ChangelogCategory | null = null;
    let inDescription = true;
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Stop parsing if we hit a horizontal rule or another major section
      if (line === '---' || line.startsWith('## ')) {
        break;
      }
      
      if (line.startsWith('**Release Date**:')) {
        date = line.replace('**Release Date**:', '').trim();
        continue;
      }
      
      if (line.startsWith('### ')) {
        inDescription = false;
        currentCategory = {
          name: line.replace('### ', '').trim(),
          items: []
        };
        categories.push(currentCategory);
        continue;
      }
      
      if (inDescription && line) {
        description += (description ? '\n' : '') + line;
      } else if (currentCategory && line) {
        // Collect items for the current category
        // If it's a list item, append it. If it's a continuation of a list item, add it to the previous.
        if (line.startsWith('- ')) {
          currentCategory.items.push(line.substring(2));
        } else if (currentCategory.items.length > 0) {
          // Multiline list item (e.g., indented sub-items)
          currentCategory.items[currentCategory.items.length - 1] += '\n' + line;
        }
      }
    }
    
    releases.push({
      version,
      date,
      description: description.trim(),
      categories
    });
  }
  
  return releases;
}
