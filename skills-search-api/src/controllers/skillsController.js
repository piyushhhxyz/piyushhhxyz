const skillsService = require('../services/skillsService');

const VALID_PLATFORMS = ['web', 'mobile', 'data', 'devops'];
const VALID_SORTS = ['relevance', 'name'];

const search = (req, res, next) => {
  try {
    // Normalize and validate q
    const q = (req.query.q || '').trim();
    if (!q) {
      const err = new Error("Query parameter 'q' is required");
      err.status = 400;
      return next(err);
    }

    // Normalize and validate platform
    let platform = (req.query.platform || '').trim().toLowerCase() || null;
    if (platform) {
      if (!VALID_PLATFORMS.includes(platform)) {
        const err = new Error('Invalid platform. Allowed values: web, mobile, data, devops');
        err.status = 400;
        return next(err);
      }
    }

    // Normalize and validate sort
    const sort = (req.query.sort || '').trim().toLowerCase() || 'relevance';
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
