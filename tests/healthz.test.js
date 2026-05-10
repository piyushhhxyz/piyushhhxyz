const request = require("supertest");
const app = require("../src/app");

describe("GET /healthz", () => {
  it("returns 200 with { status: 'ok' }", async () => {
    const res = await request(app).get("/healthz");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });

  it("returns JSON content-type", async () => {
    const res = await request(app).get("/healthz");
    expect(res.headers["content-type"]).toMatch(/application\/json/);
  });

  it("returns 404 for unknown routes", async () => {
    const res = await request(app).get("/unknown");
    expect(res.status).toBe(404);
  });

  it("responds to HEAD /healthz", async () => {
    const res = await request(app).head("/healthz");
    expect(res.status).toBe(200);
  });

  it("returns 404 for POST /healthz", async () => {
    const res = await request(app).post("/healthz");
    expect(res.status).toBe(404);
  });
});
