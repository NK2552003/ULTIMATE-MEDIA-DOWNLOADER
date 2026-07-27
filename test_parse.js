const fs = require('fs');

const content = fs.readFileSync('./public/documentations/CHANGELOG.md', 'utf8');

function parseChangelog(markdown) {
  const releases = [];
  const versionBlocks = markdown.split(/^## Version /m).slice(1);
  
  for (const block of versionBlocks) {
    const lines = block.split('\n');
    const version = lines[0].trim();
    
    let date = '';
    let description = '';
    const categories = [];
    
    let currentCategory = null;
    let inDescription = true;
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      
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
        if (line.startsWith('- ')) {
          currentCategory.items.push(line.substring(2));
        } else if (currentCategory.items.length > 0) {
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

const releases = parseChangelog(content);
console.log(JSON.stringify(releases[releases.length - 1], null, 2));
