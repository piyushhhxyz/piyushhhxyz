const skills = require('../data/skills.json');

const search = (keyword, { platform = null, sort = 'relevance' } = {}) => {
  const keywordLower = keyword.toLowerCase();

  // Filter by keyword (case-insensitive substring on name + description)
  let results = skills.filter((skill) => {
    return (
      skill.name.toLowerCase().includes(keywordLower) ||
      skill.description.toLowerCase().includes(keywordLower)
    );
  });

  // Filter by platform if provided
  if (platform) {
    results = results.filter((skill) => skill.platform === platform);
  }

  // Score relevance for each result
  results = results.map((skill) => {
    let score = 0;
    const nameLower = skill.name.toLowerCase();

    // Name tier (mutually exclusive — highest match wins)
    if (nameLower === keywordLower) {
      score += 100;
    } else if (nameLower.startsWith(keywordLower)) {
      score += 75;
    } else if (nameLower.includes(keywordLower)) {
      score += 50;
    }

    // Description bonus (independent)
    if (skill.description.toLowerCase().includes(keywordLower)) {
      score += 25;
    }

    return { ...skill, relevanceScore: score };
  });

  // Sort
  if (sort === 'relevance') {
    results.sort((a, b) => {
      if (b.relevanceScore !== a.relevanceScore) {
        return b.relevanceScore - a.relevanceScore;
      }
      return a.name.localeCompare(b.name);
    });
  } else if (sort === 'name') {
    results.sort((a, b) => a.name.localeCompare(b.name));
  }

  return results;
};

module.exports = { search };
