import {Application} from "components/types";

export function averageScore(application: Application) {
  const sum = application.scores.map(a => a.score).reduce((a, b) => a + b, 0);
  const avg = application.scores.length && sum / application.scores.length;
  return avg;
}