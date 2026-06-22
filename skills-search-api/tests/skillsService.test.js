const skillsService = require('../src/services/skillsService');

describe('skillsService.search()', () => {
  // 1. Returns matching skills by name
  test('returns matching skills by name (search "react" returns React and React Native)', () => {
    const results = skillsService.search('react');
    const names = results.map((r) => r.name);
    expect(names).toContain('React');
    expect(names).toContain('React Native');
    expect(results.length).toBeGreaterThanOrEqual(2);
  });

  // 2. Returns matching skills by description
  test('returns matching skills by description (search "machine learning" returns TensorFlow and Python)', () => {
    const results = skillsService.search('machine learning');
    const names = results.map((r) => r.name);
    expect(names).toContain('TensorFlow');
    expect(names).toContain('Python');
  });

  // 3. Case-insensitive search
  test('case-insensitive search (search "PYTHON" returns Python)', () => {
    const results = skillsService.search('PYTHON');
    const names = results.map((r) => r.name);
    expect(names).toContain('Python');
  });

  // 4. Filters by platform
  test('filters by platform (search "react" platform "mobile" returns only React Native)', () => {
    const results = skillsService.search('react', { platform: 'mobile' });
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe('React Native');
  });

  // 5. Sorts by relevance (default) — React score 125 before React Native score 100
  test('sorts by relevance by default (React before React Native)', () => {
    const results = skillsService.search('react');
    const reactIdx = results.findIndex((r) => r.name === 'React');
    const reactNativeIdx = results.findIndex((r) => r.name === 'React Native');
    expect(reactIdx).toBeLessThan(reactNativeIdx);
  });

  // 6. Sorts by name (alphabetical)
  test('sorts by name when sort is "name"', () => {
    const results = skillsService.search('react', { sort: 'name' });
    const names = results.map((r) => r.name);
    const sorted = [...names].sort((a, b) => a.localeCompare(b));
    expect(names).toEqual(sorted);
  });

  // 7. Returns empty array for no matches
  test('returns empty array for no matches', () => {
    const results = skillsService.search('zzzznonexistent');
    expect(results).toEqual([]);
  });

  // 8. Exact match scores 125 (100 name + 25 description)
  test('exact match scores 125 (100 name + 25 description)', () => {
    const results = skillsService.search('react');
    const react = results.find((r) => r.name === 'React');
    expect(react.relevanceScore).toBe(125);
  });

  // 9. Starts-with match scores 100 (75 name + 25 description)
  test('starts-with match scores 100 (75 name + 25 description)', () => {
    const results = skillsService.search('react');
    const reactNative = results.find((r) => r.name === 'React Native');
    expect(reactNative.relevanceScore).toBe(100);
  });

  // 10. Description-only match scores 25
  test('description-only match scores 25', () => {
    const results = skillsService.search('machine learning');
    const tensorflow = results.find((r) => r.name === 'TensorFlow');
    expect(tensorflow.relevanceScore).toBe(25);
  });

  // 11. Name-contains match scores >= 50
  test('name-contains match scores >= 50', () => {
    const results = skillsService.search('script');
    const typescript = results.find((r) => r.name === 'TypeScript');
    expect(typescript).toBeDefined();
    expect(typescript.relevanceScore).toBeGreaterThanOrEqual(50);
  });

  // 12. Relevance tie-breaker sorts alphabetically
  test('relevance tie-breaker sorts alphabetically', () => {
    // search "machine learning": both Python and TensorFlow have score 25
    const results = skillsService.search('machine learning', { sort: 'relevance' });
    const names = results.map((r) => r.name);
    const pythonIdx = names.indexOf('Python');
    const tensorIdx = names.indexOf('TensorFlow');
    // Both score 25 → alphabetical: Python before TensorFlow
    expect(pythonIdx).toBeLessThan(tensorIdx);
  });

  // 13. Combined platform filter + sort by name
  test('combined platform filter + sort by name', () => {
    const results = skillsService.search('a', { platform: 'web', sort: 'name' });
    // All results should be platform "web"
    results.forEach((r) => {
      expect(r.platform).toBe('web');
    });
    // Sorted alphabetically
    const names = results.map((r) => r.name);
    const sorted = [...names].sort((a, b) => a.localeCompare(b));
    expect(names).toEqual(sorted);
  });

  // 14. Platform filter with no matching results returns []
  test('platform filter with no matching results returns []', () => {
    const results = skillsService.search('react', { platform: 'data' });
    expect(results).toEqual([]);
  });

  // 15. Whitespace handling
  test('whitespace in keyword — search("react") works correctly', () => {
    const results = skillsService.search('react');
    expect(results.length).toBeGreaterThanOrEqual(2);
    const names = results.map((r) => r.name);
    expect(names).toContain('React');
    expect(names).toContain('React Native');
  });
});
