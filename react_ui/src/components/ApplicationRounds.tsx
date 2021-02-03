import React from 'react';
import {applicationRoundsUrl, applicationUrl} from "urls";
import {AppContext, ApplicationRound, User} from "components/types";
import ApplicationScores from "components/ApplicationScores";
import {addApplicationScores, addScores} from "components/utils";

type ApplicationRoundsProps = {
  user: User,
  request: (url: string, options?: any) => Promise<Response>
}

type AppOrder = 'name' | 'score' | 'unevaluated';

type ApplicationRoundsState = {
  applicationRounds?: ApplicationRound[],
  error?: boolean,
  order: AppOrder
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
    const {request} = this.props;
    request(applicationRoundsUrl).then(response => {
      if (response.status == 200)
        response.json().then(applicationRounds =>
          this.setState({applicationRounds: addScores(applicationRounds)}));
      else this.setState({error: true});
    })
  }

  reloadApplication = (appId: number) => {
    const {request} = this.props;
    request(applicationUrl(appId)).then(response => {
      if (response.status == 200) response.json().then(application => {
        const applicationRounds = [...(this.state.applicationRounds || [])];
        applicationRounds.forEach(r => {
          const i = r.applications.findIndex(a => a.id == appId);
          if (i > -1) {
            r.applications.splice(i, 1, application);
            addApplicationScores(r, [application]);
          }
        });
        this.setState({applicationRounds: applicationRounds})
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
    const {user, request} = this.props;
    if (!applicationRounds?.length) return null;

    const OrderBtn = ({order, label}: { order: AppOrder, label: string }) =>
      <>{' '}
        <button className="btn btn-sm btn-outline-secondary rounded-pill"
                onClick={() => this.setState({order})}>{label}</button>
      </>;

    return <AppContext.Provider value={{user, request, reloadApplication: this.reloadApplication}}>
      {applicationRounds.map(appRound =>
        <div className="mb-2 pt-3 pb-5" key={appRound.name}>
          <div className="pl-4 pr-4 z-1">
            <h3>{appRound.name}</h3>
            {this.scoredApps(appRound).length}/{appRound.applications.length} applications evaluated<br/>
            Order by:
            <OrderBtn label="Name" order="name"/>
            <OrderBtn label="Score" order="score"/>
            <OrderBtn label="Unevaluated" order="unevaluated"/>
          </div>
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

    if (order == 'unevaluated') apps.sort((a, b) =>
      a.scores.length - b.scores.length);

    else if (order == 'score') apps.sort((a, b) =>
      (b.score || 0) - (a.score || 0));
    return apps;
  }

  scoredApps(appRound: ApplicationRound) {
    return appRound.applications.filter(a => a.scores.length == appRound.criteria.length);
  }
}
