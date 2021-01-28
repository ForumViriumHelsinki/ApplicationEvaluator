import _ from 'lodash';
import {Application, ApplicationRound, Criterion, CriterionGroup} from "components/types";

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

export function averageScore(application: Application,
                             applicationRound: ApplicationRound,
                             criterionGroup?: CriterionGroup) {
  const weightIndex = Object.fromEntries(applicationRound.criteria.map(c => [c.id, c.weight]));
  let scores;

  if (criterionGroup) {
    const criterionIndex = Object.fromEntries(allCriteria(applicationRound, criterionGroup).map(c => [c.id, c]));
    scores = application.scores.filter(s => criterionIndex[s.criterion]);
  } else scores = application.scores;

  if (!scores.length) return null;

  const weightedScores = scores.map(s => s.score * weightIndex[s.criterion]);
  const weights = scores.map(s => weightIndex[s.criterion]);
  return sum(weightedScores) / sum(weights);
}