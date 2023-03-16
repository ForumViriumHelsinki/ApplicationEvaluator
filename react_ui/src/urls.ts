export const loginUrl = '/rest-auth/login/';
export const registerUrl = '/rest-auth/registration/';
export const passwordResetUrl = '/rest-auth/password/reset/';
export const changePasswordUrl = '/rest-auth/password/reset/confirm/';

export const applicationRoundsUrl = '/rest/application_rounds/';
export const submitApplicationRoundUrl = (roundId: number) => `/rest/application_rounds/${roundId}/submit/`;
export const scoresUrl = `/rest/scores/`;
export const scoreUrl = (scoreId: number) => `/rest/scores/${scoreId}/`;
export const commentsUrl = `/rest/comments/`;
export const commentUrl = (commentId: number) => `/rest/comments/${commentId}/`;
export const applicationUrl = (appId: number) => `/rest/applications/${appId}/`;
export const approveApplicationUrl = (appId: number) => `/rest/applications/${appId}/approve/`;
export const unapproveApplicationUrl = (appId: number) => `/rest/applications/${appId}/unapprove/`;
