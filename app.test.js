const request = require("supertest");
const app = require("./app");

describe("GET /healthz", () => {
  it("returns 200 with {status: 'ok'}", async () => {
    const res = await request(app).get("/healthz");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });

  it("returns application/json content type", async () => {
    const res = await request(app).get("/healthz");
    expect(res.headers["content-type"]).toMatch(/application\/json/);
  });
});

describe("unknown routes", () => {
  it("returns 404 for GET /unknown", async () => {
    const res = await request(app).get("/unknown");
    expect(res.status).toBe(404);
  });
});
