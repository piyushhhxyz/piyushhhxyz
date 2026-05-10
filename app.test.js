const request = require("supertest");
const app = require("./app");

describe("GET /healthz", () => {
  it("should return 200 with { status: 'ok' }", async () => {
    const res = await request(app).get("/healthz");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });

  it("should return Content-Type application/json", async () => {
    const res = await request(app).get("/healthz");
    expect(res.headers["content-type"]).toMatch(/application\/json/);
  });
});

describe("Unknown routes", () => {
  it("should return 404 for GET /", async () => {
    const res = await request(app).get("/");
    expect(res.status).toBe(404);
  });

  it("should return 404 for GET /unknown", async () => {
    const res = await request(app).get("/unknown");
    expect(res.status).toBe(404);
  });
});
