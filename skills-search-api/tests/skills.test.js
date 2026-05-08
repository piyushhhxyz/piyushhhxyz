const request = require('supertest');
const app = require('../src/app');

describe('GET /api/skills', () => {
  // 1. 200 with results for q=react
  test('200 with results for q=react', async () => {
    const res = await request(app).get('/api/skills?q=react');
    expect(res.status).toBe(200);
    expect(res.body.data.length).toBeGreaterThanOrEqual(2);
    expect(res.body.meta.query).toBe('react');
  });

  // 2. 200 with platform filter
  test('200 with platform filter', async () => {
    const res = await request(app).get('/api/skills?q=react&platform=web');
    expect(res.status).toBe(200);
    res.body.data.forEach((item) => {
      expect(item.platform).toBe('web');
    });
  });

  // 3. 200 with uppercase platform filter (normalized to lowercase)
  test('200 with uppercase platform filter (normalized)', async () => {
    const res = await request(app).get('/api/skills?q=react&platform=WEB');
    expect(res.status).toBe(200);
    expect(res.body.data.length).toBeGreaterThanOrEqual(1);
    res.body.data.forEach((item) => {
      expect(item.platform).toBe('web');
    });
  });

  // 4. 200 with sort=name
  test('200 with sort=name', async () => {
    const res = await request(app).get('/api/skills?q=react&sort=name');
    expect(res.status).toBe(200);
    const names = res.body.data.map((item) => item.name);
    const sorted = [...names].sort((a, b) => a.localeCompare(b));
    expect(names).toEqual(sorted);
  });

  // 5. 200 with uppercase sort (normalized)
  test('200 with uppercase sort (normalized)', async () => {
    const res = await request(app).get('/api/skills?q=react&sort=NAME');
    expect(res.status).toBe(200);
    const names = res.body.data.map((item) => item.name);
    const sorted = [...names].sort((a, b) => a.localeCompare(b));
    expect(names).toEqual(sorted);
  });

  // 6. 200 with empty results
  test('200 with empty results', async () => {
    const res = await request(app).get('/api/skills?q=zzzznotfound');
    expect(res.status).toBe(200);
    expect(res.body.data).toEqual([]);
    expect(res.body.meta.total).toBe(0);
  });

  // 7. 200 case-insensitive search
  test('200 case-insensitive search', async () => {
    const res = await request(app).get('/api/skills?q=PYTHON');
    expect(res.status).toBe(200);
    const names = res.body.data.map((item) => item.name);
    expect(names).toContain('Python');
  });

  // 8. 400 when q is missing
  test('400 when q is missing', async () => {
    const res = await request(app).get('/api/skills');
    expect(res.status).toBe(400);
    expect(res.body.error.message).toMatch(/q/i);
  });

  // 9. 400 when q is empty
  test('400 when q is empty', async () => {
    const res = await request(app).get('/api/skills?q=');
    expect(res.status).toBe(400);
    expect(res.body.error.message).toMatch(/q/i);
  });

  // 10. 400 when q is whitespace only
  test('400 when q is whitespace only', async () => {
    const res = await request(app).get('/api/skills?q=%20%20');
    expect(res.status).toBe(400);
    expect(res.body.error.message).toMatch(/q/i);
  });

  // 11. 400 for invalid platform
  test('400 for invalid platform', async () => {
    const res = await request(app).get('/api/skills?q=react&platform=invalid');
    expect(res.status).toBe(400);
    expect(res.body.error.message).toMatch(/platform/i);
  });

  // 12. 400 for invalid sort
  test('400 for invalid sort', async () => {
    const res = await request(app).get('/api/skills?q=react&sort=invalid');
    expect(res.status).toBe(400);
    expect(res.body.error.message).toMatch(/sort/i);
  });

  // 13. 404 for unknown route
  test('404 for unknown route', async () => {
    const res = await request(app).get('/api/unknown');
    expect(res.status).toBe(404);
  });

  // 14. Response envelope structure check
  test('response envelope structure', async () => {
    const res = await request(app).get('/api/skills?q=react');
    expect(res.body).toHaveProperty('data');
    expect(res.body).toHaveProperty('meta');
    expect(Array.isArray(res.body.data)).toBe(true);
    expect(res.body.meta).toHaveProperty('total');
    expect(res.body.meta).toHaveProperty('query');
    expect(res.body.meta).toHaveProperty('platform');
    expect(res.body.meta).toHaveProperty('sort');
  });

  // 15. Results include relevanceScore
  test('results include relevanceScore', async () => {
    const res = await request(app).get('/api/skills?q=react');
    expect(res.body.data.length).toBeGreaterThanOrEqual(1);
    res.body.data.forEach((item) => {
      expect(typeof item.relevanceScore).toBe('number');
    });
  });

  // 16. Default sort is relevance
  test('default sort is relevance', async () => {
    const res = await request(app).get('/api/skills?q=react');
    expect(res.body.meta.sort).toBe('relevance');
  });

  // 17. Platform filter + no results
  test('platform filter + no results', async () => {
    const res = await request(app).get('/api/skills?q=react&platform=data');
    expect(res.status).toBe(200);
    expect(res.body.data).toEqual([]);
  });
});
