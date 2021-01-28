import _ from 'lodash';
import {ApplicationRound, Criterion, CriterionGroup, Score, User} from "components/types";

const sum = (lst: number[]) => lst.reduce((a, b) => a + b, 0);

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

export const addScores = (rounds: ApplicationRound[]) => {
  rounds.forEach(round => {
    const thresholdGroups = round.criterion_groups.filter(g => g.threshold);
    const criteriaByGroup = Object.fromEntries(round.criterion_groups.map(g => [g.id, allCriteria(round, g)]))
    const weightIndex = Object.fromEntries(round.criteria.map(c => [c.id, c.weight]));

    const weightedAvg = (scores: Score[]) => {
      const weightedScores = scores.map(s => s.score * weightIndex[s.criterion]);
      const weights = scores.map(s => weightIndex[s.criterion]);
      return sum(weightedScores) / sum(weights);
    };

    round.applications.forEach(app => {
      app.groupScores = {};
      if (!app.scores.length) return;
      app.score = weightedAvg(app.scores);
      thresholdGroups.forEach(group => {
        const criterionIndex = Object.fromEntries(criteriaByGroup[group.id].map(c => [c.id, c]));
        const scores = app.scores.filter(s => criterionIndex[s.criterion]);
        if (scores.length) app.groupScores[group.id] = weightedAvg(scores);
      })
    })
  });
  return rounds;
};

export const username = (user: User) => {
  return (user.first_name && user.last_name) ? `${user.first_name} ${user.last_name}` : user.username
};