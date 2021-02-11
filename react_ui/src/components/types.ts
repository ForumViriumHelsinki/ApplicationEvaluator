import React from "react";

export type User = {
    id: number,
    username: string,
    first_name: string,
    last_name: string,
    organization: string
};

export type AppContextType = {
    user?: User,
    reloadApplication: (id: number) => any,
    request: (url: string, options?: any) => Promise<Response>
}

export type Score = {
    id: number,
    score: number,
    evaluator: User,
    criterion: number
}

export type Comment = {
    created_at: string;
    id: number,
    comment: string,
    evaluator: User,
    criterion_group: number
}

export type Attachment = {
    name: string,
    attachment: string,
}

export type Application = {
    id: number,
    name: string,
    scores: Score[],
    comments: Comment[],
    attachments: Attachment[],
    score: number,
    scored: boolean,
    groupScores: any,
    scoresByOrganization: {
        [organization: string]: {
            score: number,
            groupScores: any,
        }
    }
    evaluating_organizations: string[]
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
    id: number,
    name: string,
    applications: Application[],
    criteria: Criterion[],
    criterion_groups: CriterionGroup[],
    attachments: Attachment[],
    submitted_organizations: string[]
}

export const AppContext = React.createContext({user: undefined} as AppContextType);
