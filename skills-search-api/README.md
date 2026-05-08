# Skills Search API

A REST API for searching skills by keyword with platform filtering and relevance sorting.

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)

### Installation

```bash
npm install
```

### Start the server

```bash
npm start
```

The server will start on port 3000 by default. Set the `PORT` environment variable to use a different port.

### Development mode

```bash
npm run dev
```

## API Reference

### `GET /api/skills`

Search for skills by keyword.

#### Query Parameters

| Parameter  | Required | Description                                                      |
|------------|----------|------------------------------------------------------------------|
| `q`        | Yes      | Search keyword (case-insensitive substring match on name and description) |
| `platform` | No       | Filter by platform. Allowed values: `web`, `mobile`, `data`, `devops` |
| `sort`     | No       | Sort order. Allowed values: `relevance` (default), `name`        |

#### Response

Returns a JSON envelope with `data` (array of matching skills) and `meta` (query metadata).

Each skill object includes:
- `id` — Unique identifier
- `name` — Skill name
- `description` — Skill description
- `platform` — Platform category
- `relevanceScore` — Relevance score based on keyword match

#### Example Request

```bash
curl "http://localhost:3000/api/skills?q=react"
```

#### Example Response

```json
{
  "data": [
    {
      "id": 1,
      "name": "React",
      "description": "A JavaScript library for building user interfaces with a component-based architecture using React patterns",
      "platform": "web",
      "relevanceScore": 125
    },
    {
      "id": 6,
      "name": "React Native",
      "description": "A framework for building native mobile apps using React components and JavaScript",
      "platform": "mobile",
      "relevanceScore": 100
    }
  ],
  "meta": {
    "total": 2,
    "query": "react",
    "platform": null,
    "sort": "relevance"
  }
}
```

#### Error Responses

- **400 Bad Request** — Missing or invalid query parameters
- **404 Not Found** — Unknown route

## Testing

```bash
npm test
```

Runs unit tests for the service layer and integration tests for the API endpoint using Jest and Supertest.
