import React from "react";

export type User = {
    id: number,
    username: string,
    first_name: string,
    last_name: string,
};

export type AppContextType = {
    user?: User,
    reloadApplication: (id: number) => any
}

export type Score = {
    id: number,
    score: number,
    evaluator: User,
    criterion: number
}

export type Application = {
    id: number,
    name: string,
    scores: Score[],
    score: number,
    groupScores: any
}

export type Criterion = {
    id: number,
    name: string,
    group: number,
    weight: number
}

export type CriterionGroup = {
    name: string,
    abbr: string,
    id: number,
    parent?: number,
    threshold: number
}

export type ApplicationRound = {
    name: string,
    applications: Application[],
    criteria: Criterion[],
    criterion_groups: CriterionGroup[]
}

export const AppContext = React.createContext({user: undefined} as AppContextType);
