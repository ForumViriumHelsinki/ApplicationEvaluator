import _ from 'lodash';
import {Application, ApplicationRound, Criterion, CriterionGroup, Score, User} from "../components/types";
import settings from "/settings";

const sum = (lst: number[]) => lst.reduce((a, b) => a + b, 0);

const avg = (lst: number[]) => sum(lst) / lst.length;

function childCriteria(applicationRound: ApplicationRound, criterionGroup: CriterionGroup) {
  return applicationRound.criteria.filter(c => c.group == criterionGroup.id);
}

function childGroups(applicationRound: ApplicationRound, criterionGroup: CriterionGroup) {
  return applicationRound.criterion_groups.filter(g => g.parent == criterionGroup.id);
}

const allCriteria = (applicationRound: ApplicationRound, criterionGroup: CriterionGroup): Criterion[] => {
  return _.flatten([
    childCriteria(applicationRound, criterionGroup),
    // @ts-ignore
    childGroups(applicationRound, criterionGroup).map(g => allCriteria(applicationRound, g))
  ]);
};

export const addApplicationScores = (round: ApplicationRound, applications: Application[]) => {
  const thresholdGroups = round.criterion_groups.filter(g => g.threshold);
  const criteriaByGroup = Object.fromEntries(round.criterion_groups.map(g => [g.id, allCriteria(round, g)]))
  const weightIndex = Object.fromEntries(round.criteria.map(c => [c.id, c.weight]));

  const weightedAvg = (scores: Score[]) => {
    const scoresByCriterion = _.groupBy(scores, 'criterion');
    const avgScores = Object.entries(scoresByCriterion).map(([criterion, cScores]) => {
      const orgScores = Object.values(_.groupBy(cScores, s => s.evaluator.organization))
        .map(scores => avg(scores.map(s => s.score)));
      return {criterion, score: avg(orgScores)};
    });
    const weightedScores = avgScores.map(s => s.score * weightIndex[s.criterion]);
    const weights = avgScores.map(s => weightIndex[s.criterion]);
    return sum(weightedScores) / sum(weights);
  };

  const groupScores = (scores: Score[]) => {
    const groupScores: any = {};
    thresholdGroups.forEach(group => {
      const criterionIndex = Object.fromEntries(criteriaByGroup[group.id].map(c => [c.id, c]));
      const gScores = scores.filter(s => criterionIndex[s.criterion]);
      if (gScores.length) groupScores[group.id] = weightedAvg(gScores);
    });
    return groupScores;
  };

  applications.forEach(app => {
    app.groupScores = {};
    app.scoresByOrganization = {};
    if (!app.scores.length) return;
    app.scored = _.uniq(app.scores.map((s: Score) => s.criterion)).length == round.criteria.length;
    app.score = weightedAvg(app.scores);
    app.groupScores = groupScores(app.scores);

    const scoresByOrganization = _.groupBy(app.scores, s => s.evaluator.organization);
    app.scoresByOrganization =
      Object.fromEntries(Object.entries(scoresByOrganization)
        .map(([organization, scores]) =>
          [organization, {score: weightedAvg(scores), groupScores: groupScores(scores)}]));

    const scoresByEvaluator = _.groupBy(app.scores, s => username(s.evaluator));
    app.scoresByEvaluator =
      Object.fromEntries(Object.entries(scoresByEvaluator)
        .map(([evaluator, scores]) =>
          [evaluator, {score: weightedAvg(scores), groupScores: groupScores(scores)}]));
  });
  return round;
};

export const addScores = (rounds: ApplicationRound[]) => {
  rounds.forEach(round => addApplicationScores(round, round.applications))
  return rounds;
};

export const username = (user: User) => {
  return (user.first_name && user.last_name) ? `${user.first_name} ${user.last_name}` : user.username
};

const colors = [
  '#1B2C41',
  '#F9B122',
  '#56B4E9',
  '#009E73',
  '#0072B2',
  '#D55E00',
  '#CC79A7',
];

const organizationColors: any = {};
let colorIndex = 0;

export const organizationColor = (org: string) => {
  if (!organizationColors[org]) organizationColors[org] = colors[colorIndex++ % colors.length]
  return organizationColors[org];
};

export const slug = (name: string) => name.replace(/[^a-z]/ig, '');

export function getTotalScore(application: Application) {
  return application.score && (application.score * settings.finalScoreMultiplier).toPrecision(3);
}