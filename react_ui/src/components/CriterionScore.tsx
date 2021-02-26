import React, {FocusEvent} from 'react';

import {AppContext, Application, Criterion, Score} from "components/types";
import Icon from "util_components/bootstrap/Icon";
import ConfirmButton from "util_components/bootstrap/ConfirmButton";
import {scoresUrl, scoreUrl} from "urls";
import {username} from "components/utils";

type CriterionScoreProps = {
  criterion: Criterion,
  application: Application,
  readOnly?: boolean
}

type CriterionScoreState = {
  changed?: boolean,
  addScore?: boolean,
  error?: boolean
}

const initialState: CriterionScoreState = {};

export default class CriterionScore extends React.Component<CriterionScoreProps, CriterionScoreState> {
  state = initialState;
  static contextType = AppContext;

  render() {
    const {criterion, application, readOnly} = this.props;
    const {changed, addScore, error} = this.state;
    const {user} = this.context;

    const scores = application.scores.filter(s => s.criterion == criterion.id);
    const myScore = application.scores.find(s =>
      s.criterion == criterion.id && s.evaluator.id == user.id);
    const myOrgScore = application.scores.find(s =>
      s.criterion == criterion.id && s.evaluator.organization == user.organization);

    return <div className="ml-2 mb-2">
      {criterion.name}:{' '}
      {!myScore && !readOnly && (!myOrgScore || addScore) &&
      <div className="form-inline">
        <input type="number" min="0" max="10" className={`form-control form-control-sm ${error ? 'is-invalid' : ''}`}
               onBlur={this.saveScore}
               onChange={() => this.setState({changed: true})}/>{' '}
        {changed && <button className="btn btn-sm btn-outline-primary ml-2">Save</button>}
      </div>
      }

      {scores.map((score: Score) =>
        <div key={score.id}>
          <strong>{score.score}</strong> (by {username(score.evaluator)})
          {score.evaluator.id == user.id && !readOnly &&
          <ConfirmButton className="btn-light btn-sm text-danger p-1 btn-trans" confirm="Delete score?"
                         onClick={this.deleteScore}>
            <Icon icon="clear"/>
          </ConfirmButton>
          }
        </div>
      )}
      {myOrgScore && !myScore && !addScore &&
      <a className="clickable text-success d-block" style={{marginLeft: -4}}
         onClick={() => this.setState({addScore: true})}>
        <Icon icon="add"/>
      </a>
      }
    </div>;
  }

  saveScore = (e: FocusEvent<HTMLInputElement>) => {
    const {application, criterion} = this.props;
    const {reloadApplication, request} = this.context;
    const value = Number(e.target.value);
    if (!e.target.value || value > 10 || value < 0) return this.setState({error: true});
    else this.setState({error: false});
    const data = {application: application.id, criterion: criterion.id, score: value};
    request(scoresUrl, {method: 'POST', data}).then((response: Response) => {
      if (response.status < 300) {
        this.setState({changed: false, addScore: false});
        reloadApplication(application.id);
      }
    })
  };

  deleteScore = () => {
    const {application, criterion} = this.props;
    const {reloadApplication, request, user} = this.context;
    const score = application.scores.find(s => s.criterion == criterion.id && s.evaluator.id == user.id);
    if (!score) return;
    request(scoreUrl(score.id), {method: 'DELETE'}).then((response: Response) => {
      if (response.status < 300) reloadApplication(application.id);
    })
  };
}
