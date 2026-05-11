const request = require("supertest");
const app = require("../src/app");

describe("GET /healthz", () => {
  it("returns 200 with status ok", async () => {
    const res = await request(app).get("/healthz");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });

  it("returns JSON content-type", async () => {
    const res = await request(app).get("/healthz");
    expect(res.headers["content-type"]).toMatch(/application\/json/);
  });

  it("includes uptime as a number", async () => {
    const res = await request(app).get("/healthz");
    expect(typeof res.body.uptime).toBe("number");
    expect(res.body.uptime).toBeGreaterThanOrEqual(0);
  });

  it("includes a valid ISO timestamp", async () => {
    const res = await request(app).get("/healthz");
    expect(res.body.timestamp).toBeDefined();
    const parsed = new Date(res.body.timestamp);
    expect(parsed.toISOString()).toBe(res.body.timestamp);
  });

  it("returns 404 for unknown routes", async () => {
    const res = await request(app).get("/unknown");
    expect(res.status).toBe(404);
  });
});
