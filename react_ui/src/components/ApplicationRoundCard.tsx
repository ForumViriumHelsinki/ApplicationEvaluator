import React from 'react';
import {ApplicationRound} from "components/types";
import ApplicationScores from "components/ApplicationScores";

type ApplicationRoundCardProps = {
  applicationRound: ApplicationRound
}

type AppOrder = 'name' | 'score' | 'unevaluated';

type ApplicationRoundCardState = {
  order: AppOrder,
  showEvaluators: boolean,
  expanded?: boolean
}

const initialState: ApplicationRoundCardState = {
  order: 'name',
  showEvaluators: true
};

export default class ApplicationRoundCard extends React.Component<ApplicationRoundCardProps, ApplicationRoundCardState> {
  state = initialState;

  render() {
    const {applicationRound} = this.props;
    const {showEvaluators, expanded} = this.state;
    const scoredApps = applicationRound.applications.filter(a => a.scores.length == applicationRound.criteria.length);

    const OrderBtn = ({order, label}: { order: AppOrder, label: string }) =>
      <>{' '}
        <button className="btn btn-sm btn-outline-secondary rounded-pill"
                onClick={() => this.setState({order})}>{label}</button>
      </>;

    return <div className="container mt-4 mb-3 rounded trans-bg pl-0 pr-0 pt-4 pb-4">
      <div className="pl-4 pr-4 z-1">
        <h3 className="clickable text-primary" onClick={() => this.setState({expanded: !expanded})}>
          {applicationRound.name}
        </h3>
        {applicationRound.attachments.length > 0 &&
        <div>
          Documents:
          {applicationRound.attachments.map(({attachment, name}) =>
            <a href={attachment} target='_blank' className="text-secondary ml-2" key={attachment}>{name}</a>
          )}
        </div>
        }
        {scoredApps.length}/{applicationRound.applications.length} applications evaluated
        {expanded &&
        <div className="mt-2">
          Order by:
          <OrderBtn label="Name" order="name"/>
          <OrderBtn label="Score" order="score"/>
          <OrderBtn label="Unevaluated" order="unevaluated"/>
          <div className="form-check d-inline-block ml-3"
               onClick={() => this.setState({showEvaluators: !showEvaluators})}>
            <input className="form-check-input" type="checkbox" checked={showEvaluators}/>
            <label className="form-check-label">Show evaluators</label>
          </div>
        </div>
        }
      </div>
      {expanded && this.getApplications().map(app =>
        <ApplicationScores application={app} applicationRound={applicationRound}
                           key={app.name} showEvaluators={showEvaluators}/>
      )}
    </div>;
  }

  getApplications() {
    const {order} = this.state;
    const {applicationRound} = this.props;
    if (order == 'name') return applicationRound.applications;

    const apps = [...applicationRound.applications];

    if (order == 'unevaluated') apps.sort((a, b) =>
      a.scores.length - b.scores.length);

    else if (order == 'score') apps.sort((a, b) =>
      (b.score || 0) - (a.score || 0));
    return apps;
  }
}
