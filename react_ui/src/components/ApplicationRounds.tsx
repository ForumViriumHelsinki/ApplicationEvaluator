import React from 'react';
import {applicationRoundsUrl, applicationUrl} from "urls";
import {AppContext, ApplicationRound, User} from "components/types";
import {addApplicationScores, addScores} from "components/utils";
import ApplicationRoundCard from "components/ApplicationRoundCard";

type ApplicationRoundsProps = {
  user: User,
  request: (url: string, options?: any) => Promise<Response>
}

type AppOrder = 'name' | 'score' | 'unevaluated';

type ApplicationRoundsState = {
  applicationRounds?: ApplicationRound[],
  error?: boolean,
  order: AppOrder,
  showEvaluators: boolean
}

const initialState: ApplicationRoundsState = {
  order: 'name',
  showEvaluators: true
};

export default class ApplicationRounds extends React.Component<ApplicationRoundsProps, ApplicationRoundsState> {
  state = initialState;

  componentDidMount() {
    this.loadRounds();
  }

  loadRounds = () => {
    const {request} = this.props;
    request(applicationRoundsUrl).then(response => {
      if (response.status == 200)
        response.json().then(applicationRounds =>
          this.setState({applicationRounds: addScores(applicationRounds)}));
      else this.setState({error: true});
    })
  };

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
    const {user, request} = this.props;
    const {error, applicationRounds} = this.state;

    const context = {user, request, reloadApplication: this.reloadApplication, loadRounds: this.loadRounds};

    return applicationRounds ?
      applicationRounds.length ?
        <AppContext.Provider value={context}>
          {applicationRounds.map(appRound =>
            <ApplicationRoundCard applicationRound={appRound} key={appRound.id}/>)}
        </AppContext.Provider>
        : <div className="container mt-4 mb-5 rounded trans-bg pl-0 pr-0">
          <h5 className="text-center">No applications currently awaiting evaluation.</h5>
        </div>
      : error ?
        <div className="container mt-4 mb-5 rounded trans-bg pl-0 pr-0">
          <h5 className="text-center">Error fetching applications. Perhaps try reloading or logging out and in
            again?</h5>
        </div>
        : null;
  }
}
