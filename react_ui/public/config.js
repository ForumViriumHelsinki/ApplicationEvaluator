// Runtime configuration - injected at container startup via envsubst
// For local development, these are sensible defaults
// In production, environment variables override these values
window.__CONFIG__ = {
  serverRoot: "",
  maxScore: 5,
  finalScoreMultiplier: 4,
  showScoresFromOtherUsers: true,
  allowSubmit: false,
};
