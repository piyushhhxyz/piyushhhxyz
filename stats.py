"""Pull the GitHub numbers that appear on the profile card.

Everything here goes through the GraphQL API. Line-of-code counting is the
expensive part, so per-repository results are cached under cache/ keyed by the
commit SHA at the tip of the default branch - a repo that has not moved since
the last run costs zero API calls.
"""
import json
import os
import pathlib
import time
from datetime import datetime, timedelta, timezone

import requests

API = "https://api.github.com/graphql"
REST = "https://api.github.com"
CACHE = pathlib.Path("cache")

# Committing any of these means the repo's diff stats are dominated by code the
# user did not write. Such repos are dropped from the line count entirely -
# counting them would put the total off by an order of magnitude.
VENDORED = ("node_modules/", "vendor/", "dist/", "build/", ".vite/",
            "site-packages/", "venv/", ".next/", "Pods/", "target/")


class Cache:
    """One JSON file keyed by `<repo>@<head sha>`; a repo that has not been
    pushed to since the last run is answered without touching the network."""

    def __init__(self, path=CACHE / "repos.json"):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {}

    def get(self, key):
        return self.data.get(key)

    def put(self, key, value):
        self.data[key] = value

    def save(self):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True))


class Client:
    def __init__(self, token, login):
        self.login = login
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"bearer {token}"})
        self.calls = 0

    def rest(self, path, **params):
        self.calls += 1
        r = self.session.get(f"{REST}{path}", params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        return None

    def query(self, doc, **variables):
        """POST a GraphQL document, retrying through secondary rate limits."""
        for attempt in range(5):
            self.calls += 1
            r = self.session.post(API, json={"query": doc, "variables": variables},
                                  timeout=30)
            if r.status_code == 200:
                payload = r.json()
                if "errors" in payload:
                    raise RuntimeError(f"GraphQL error: {payload['errors']}")
                return payload["data"]
            if r.status_code in (403, 429):        # secondary rate limit
                wait = int(r.headers.get("Retry-After", 2 ** attempt * 5))
                print(f"  rate limited, sleeping {wait}s")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        raise RuntimeError("gave up after 5 attempts")


USER_Q = """
query($login:String!){
  user(login:$login){
    id name login createdAt
    followers{totalCount}
    following{totalCount}
    repositories(ownerAffiliations:OWNER, isFork:false){totalCount}
    repositoriesContributedTo(
      contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY],
      includeUserRepositories:false){totalCount}
  }
}
"""

CONTRIB_Q = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      totalCommitContributions
      restrictedContributionsCount
    }
  }
}
"""

REPOS_Q = """
query($login:String!,$cursor:String){
  user(login:$login){
    repositories(first:100, after:$cursor, orderBy:{field:PUSHED_AT,direction:DESC},
                 ownerAffiliations:OWNER, affiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER]){
      pageInfo{hasNextPage endCursor}
      nodes{
        nameWithOwner isFork stargazerCount
        defaultBranchRef{ target{ ... on Commit { oid } } }
      }
    }
  }
}
"""

HISTORY_Q = """
query($owner:String!,$name:String!,$id:ID!,$cursor:String){
  repository(owner:$owner,name:$name){
    defaultBranchRef{
      target{ ... on Commit {
        history(first:100, after:$cursor, author:{id:$id}){
          pageInfo{hasNextPage endCursor}
          nodes{ additions deletions }
        }
      }}
    }
  }
}
"""


def account_age(created_at):
    """Whole years/months/days since the account was opened."""
    start = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    years = now.year - start.year
    months = now.month - start.month
    days = now.day - start.day
    if days < 0:
        months -= 1
        prev = (now.replace(day=1) - timedelta(days=1)).day
        days += prev
    if months < 0:
        years -= 1
        months += 12
    return years, months, days


def total_commits(client, created_at):
    """contributionsCollection caps at one year, so walk year by year."""
    start = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    total = 0
    year = start.year
    while year <= now.year:
        frm = max(start, datetime(year, 1, 1, tzinfo=timezone.utc))
        to = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        if frm >= to:
            year += 1
            continue
        c = client.query(CONTRIB_Q, login=client.login,
                         **{"from": frm.isoformat(), "to": to.isoformat()})
        cc = c["user"]["contributionsCollection"]
        total += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
        year += 1
    return total


def all_repos(client):
    repos, cursor = [], None
    while True:
        d = client.query(REPOS_Q, login=client.login, cursor=cursor)
        page = d["user"]["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return repos
        cursor = page["pageInfo"]["endCursor"]


def find_vendored(client, repo, oid):
    """Return the vendored directory this repo checks in, or None."""
    tree = client.rest(f"/repos/{repo}/git/trees/{oid}", recursive="1") or {}
    paths = [n["path"] + "/" for n in tree.get("tree", [])]
    return next((v for v in VENDORED
                 if any(p.startswith(v) or f"/{v}" in p for p in paths)), None)


def repo_loc(client, cache, repo, user_id):
    """Additions/deletions this user authored in one repo, cached by head SHA."""
    head = (repo.get("defaultBranchRef") or {}).get("target") or {}
    oid = head.get("oid")
    if not oid:
        return 0, 0, None

    name_with_owner = repo["nameWithOwner"]
    key = f"{name_with_owner}@{oid}"
    hit = cache.get(key)
    if hit is not None:
        return hit["additions"], hit["deletions"], hit.get("vendored")

    marker = find_vendored(client, name_with_owner, oid)
    if marker:
        cache.put(key, {"additions": 0, "deletions": 0, "vendored": marker})
        return 0, 0, marker

    owner, name = name_with_owner.split("/", 1)
    adds = dels = 0
    cursor = None
    while True:
        d = client.query(HISTORY_Q, owner=owner, name=name, id=user_id, cursor=cursor)
        target = ((d.get("repository") or {}).get("defaultBranchRef") or {}).get("target")
        if not target:
            break
        h = target["history"]
        for n in h["nodes"]:
            adds += n["additions"]
            dels += n["deletions"]
        if not h["pageInfo"]["hasNextPage"]:
            break
        cursor = h["pageInfo"]["endCursor"]

    cache.put(key, {"additions": adds, "deletions": dels, "vendored": None})
    return adds, dels, None


def collect(token, login, exclude=()):
    client = Client(token, login)
    exclude = set(exclude)
    user = client.query(USER_Q, login=login)["user"]

    repos = all_repos(client)
    stars = sum(r["stargazerCount"] for r in repos if not r["isFork"])

    cache = Cache()
    adds = dels = 0
    skipped = []
    for i, r in enumerate(repos, 1):
        if r["nameWithOwner"] in exclude:
            skipped.append(f"{r['nameWithOwner']} (config)")
            continue
        a, d, marker = repo_loc(client, cache, r, user["id"])
        if marker:
            skipped.append(f"{r['nameWithOwner']} ({marker} checked in)")
        adds += a
        dels += d
        if i % 20 == 0:
            print(f"  loc: {i}/{len(repos)} repos")
    cache.save()

    for r in sorted(skipped):
        print(f"  excluded from line count: {r}")

    y, m, d = account_age(user["createdAt"])
    return {
        "name": user["name"] or user["login"],
        "login": user["login"],
        "age": f"{y} years, {m} months, {d} days",
        "repos": user["repositories"]["totalCount"],
        "contributed": user["repositoriesContributedTo"]["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": total_commits(client, user["createdAt"]),
        "loc_add": adds,
        "loc_del": dels,
        "loc_net": adds - dels,
        "api_calls": client.calls,
        "excluded": sorted(skipped),
    }


def sanity_check(new, previous):
    """Refuse to publish a card that just lost most of its data.

    The usual cause is a token that cannot see the whole account - Actions'
    built-in GITHUB_TOKEN is scoped to a single repository, so it reports a
    fraction of the repos and a tiny line count. Failing here keeps a bad run
    from overwriting a good card.
    """
    if not previous:
        return
    for field, floor in (("repos", 0.8), ("loc_add", 0.8), ("stars", 0.8)):
        was, now = previous.get(field, 0), new.get(field, 0)
        if was and now < was * floor:
            raise SystemExit(
                f"refusing to write: {field} fell from {was:,} to {now:,}.\n"
                "This almost always means ACCESS_TOKEN is missing or lacks "
                "`repo` scope, so the API only returned part of the account.")


if __name__ == "__main__":
    tok = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    cfg = json.loads(pathlib.Path("config.json").read_text())
    who = os.environ.get("PROFILE_LOGIN") or cfg.get("login") or "piyushhhxyz"
    stats_path = CACHE / "stats.json"
    previous = json.loads(stats_path.read_text()) if stats_path.exists() else None

    data = collect(tok, who, cfg.get("exclude_repos", []))
    sanity_check(data, previous)

    CACHE.mkdir(exist_ok=True)
    stats_path.write_text(json.dumps(data, indent=2))
    print(json.dumps({k: v for k, v in data.items() if k != "excluded"}, indent=2))
