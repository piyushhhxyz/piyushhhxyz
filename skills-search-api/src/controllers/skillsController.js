const skillsService = require('../services/skillsService');

const VALID_PLATFORMS = Object.freeze(['web', 'mobile', 'data', 'devops']);
const VALID_SORTS = Object.freeze(['relevance', 'name']);

/**
 * Extract a scalar string from a query parameter value.
 * Express may parse repeated keys (e.g. ?q=a&q=b) as an array.
 * When that happens, take only the first element.
 */
const toScalar = (value) => {
  if (Array.isArray(value)) return value[0];
  return value;
};

const search = (req, res, next) => {
  try {
    // Normalize and validate q
    const q = (toScalar(req.query.q) || '').trim();
    if (!q) {
      const err = new Error("Query parameter 'q' is required");
      err.status = 400;
      return next(err);
    }

    // Normalize and validate platform
    let platform = (toScalar(req.query.platform) || '').trim().toLowerCase() || null;
    if (platform) {
      if (!VALID_PLATFORMS.includes(platform)) {
        const err = new Error('Invalid platform. Allowed values: web, mobile, data, devops');
        err.status = 400;
        return next(err);
      }
    }

    // Normalize and validate sort
    const sort = (toScalar(req.query.sort) || '').trim().toLowerCase() || 'relevance';
    if (!VALID_SORTS.includes(sort)) {
      const err = new Error('Invalid sort. Allowed values: relevance, name');
      err.status = 400;
      return next(err);
    }

    const results = skillsService.search(q, { platform, sort });

    res.status(200).json({
      data: results,
      meta: {
        total: results.length,
        query: q,
        platform: platform,
        sort: sort
      }
    });
  } catch (err) {
    next(err);
  }
};

module.exports = { search };
