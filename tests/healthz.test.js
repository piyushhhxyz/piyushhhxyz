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

  it("does not accept POST requests on /healthz", async () => {
    const res = await request(app).post("/healthz");
    expect(res.status).toBe(404);
  });

  it("response body contains only the status field", async () => {
    const res = await request(app).get("/healthz");
    expect(Object.keys(res.body)).toEqual(["status"]);
  });
});
