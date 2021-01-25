import React from 'react';
import sessionRequest from "sessionRequest";
import {applicationRoundsUrl, applicationUrl} from "urls";
import {AppContext, ApplicationRound, CriterionGroup, User} from "components/types";
import CriterionGroupComponent from "components/CriterionGroup";
import ApplicationScores from "components/ApplicationScores";
import {averageScore} from "components/utils";

type ApplicationRoundsProps = {
  user: User
}

type ApplicationRoundsState = {
  applicationRounds?: ApplicationRound[],
  error?: boolean,
  order: 'name' | 'score'
}

const initialState: ApplicationRoundsState = {
  order: 'name'
};

export default class ApplicationRounds extends React.Component<ApplicationRoundsProps, ApplicationRoundsState> {
  state = initialState;

  componentDidMount() {
    this.loadRounds();
  }

  loadRounds() {
    sessionRequest(applicationRoundsUrl).then(response => {
      if (response.status == 200) response.json().then(applicationRounds => this.setState({applicationRounds}));
      else this.setState({error: true});
    })
  }

  reloadApplication = (appId: number) => {
    sessionRequest(applicationUrl(appId)).then(response => {
      if (response.status == 200) response.json().then(application => {
        const applicationRounds = [...(this.state.applicationRounds || [])];
        applicationRounds.forEach(r => {
          const i = r.applications.findIndex(a => a.id == appId);
          if (i > -1) r.applications.splice(i, 1, application);
        });
        this.setState({applicationRounds})
      });
      else this.setState({error: true});
    })
  };

  render() {
    const {} = this.props;
    const {error, applicationRounds} = this.state;

    return applicationRounds ?
      applicationRounds.length ? this.renderMain()
      : <h5 className="text-center">No applications currently awaiting evaluation.</h5>
    : error ?
      <h5 className="text-center">Error fetching applications. Perhaps try reloading or logging out and in again?</h5>
      : null;
  }

  renderMain() {
    const {applicationRounds} = this.state;
    const {user} = this.props;
    if (!applicationRounds?.length) return null;

    return <AppContext.Provider value={{user, reloadApplication: this.reloadApplication}}>
      {applicationRounds.map(appRound =>
        <div className="mb-2" key={appRound.name}>
          <h3>{appRound.name}</h3>
          {this.scoredApps(appRound).length}/{appRound.applications.length} applications evaluated<br/>
          Order by:{' '}
          <button className="btn btn-sm btn-outline-secondary rounded-pill"
                  onClick={() => this.setState({order: 'name'})}>Name</button>{' '}
          <button className="btn btn-sm btn-outline-secondary rounded-pill"
                  onClick={() => this.setState({order: 'score'})}>Score</button>{' '}
          {this.getApplications(appRound).map(app =>
            <ApplicationScores application={app} applicationRound={appRound} key={app.name}/>
          )}
        </div>
      )}
    </AppContext.Provider>
  }

  getApplications(appRound: ApplicationRound) {
    const {order} = this.state;
    if (order == 'name') return appRound.applications;

    const apps = [...appRound.applications];
    apps.sort((a, b) => averageScore(b) - averageScore(a));
    return apps;
  }

  scoredApps(appRound: ApplicationRound) {
    return appRound.applications.filter(a => a.scores.length == appRound.criteria.length);
  }
}