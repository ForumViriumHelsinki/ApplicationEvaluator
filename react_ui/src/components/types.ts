import React from 'react';

export type User = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  organization: string;
  is_superuser?: boolean;
};

export type SessionRequestOptions = RequestInit & {
  data?: unknown;
};

export type AppContextType = {
  user?: User;
  reloadApplication: (id: number) => void;
  updateApplication: (app: Application) => void;
  loadRounds: () => void;
  request: (url: string, options?: SessionRequestOptions) => Promise<Response>;
};

export type Score = {
  id: number;
  score: number;
  evaluator: User;
  criterion: number;
};

export type Comment = {
  created_at: string;
  id: number;
  comment: string;
  evaluator: User;
  criterion_group: number;
};

export type Attachment = {
  name: string;
  attachment: string;
};

export type Application = {
  id: number;
  application_id?: string;
  name: string;
  description: string;
  scores: Score[];
  comments: Comment[];
  attachments: Attachment[];
  score: number;
  scored: boolean;
  approved?: boolean;
  groupScores: Record<string, number>;
  scoresByOrganization: {
    [organization: string]: {
      score: number;
      groupScores: Record<string, number>;
    };
  };
  scoresByEvaluator: {
    [evaluator: string]: {
      score: number;
      groupScores: Record<string, number>;
    };
  };
  evaluating_organizations: string[];
};

export type Criterion = {
  id: number;
  name: string;
  group: number;
  weight: number;
};

export type CriterionGroup = {
  name: string;
  abbr: string;
  id: number;
  parent?: number;
  threshold: number;
};

export type ScoringModel =
  | 'Organizations average'
  | 'Evaluators average'
  | 'Simple average'
  | string;

export type ApplicationRound = {
  id: number;
  name: string;
  description: string;
  applications: Application[];
  criteria: Criterion[];
  criterion_groups: CriterionGroup[];
  attachments: Attachment[];
  submitted_organizations: string[];
  scoring_completed?: boolean;
  scoring_model?: ScoringModel;
};

export const AppContext = React.createContext<AppContextType>({
  user: undefined,
  reloadApplication: () => {},
  updateApplication: () => {},
  loadRounds: () => {},
  request: () => Promise.resolve(new Response()),
});
