import React from 'react';
import {FocusEvent} from 'react';
import {AppContext, Application, Criterion, User} from "components/types";
import Icon from "util_components/bootstrap/Icon";
import Confirm from "util_components/bootstrap/Confirm";
import ConfirmButton from "util_components/bootstrap/ConfirmButton";
import sessionRequest from "sessionRequest";
import {scoresUrl, scoreUrl} from "urls";

type CriterionScoreProps = {
  criterion: Criterion,
  application: Application
}

type CriterionScoreState = {
  changed?: boolean
}

const initialState: CriterionScoreState = {};

const username = (user: User) => {
  return (user.first_name && user.last_name) ? `${user.first_name} ${user.last_name}` : user.username
};

export default class CriterionScore extends React.Component<CriterionScoreProps, CriterionScoreState> {
  state = initialState;
  static contextType = AppContext;

  render() {
    const {criterion, application} = this.props;
    const {changed} = this.state;
    const {user} = this.context;

    const score = this.getScore();

    return <div className="ml-2 mb-2">
      {criterion.name}:
      {score && (score.evaluator.pk != user.id) ?
        <div><strong>{score.score}</strong> (by {username(score.evaluator)})</div>
      : score ?
        <div>
          <strong>{score.score}</strong> (by {username(score.evaluator)})
          <ConfirmButton className="btn-light btn-sm text-danger p-1" confirm="Delete score?"
                         onClick={this.deleteScore}>
            <Icon icon="clear"/>
          </ConfirmButton>
        </div>
      : <div className="form-inline">
          <input type="number" min="0" max="10" className="form-control form-control-sm"
                 onBlur={this.saveScore}
                 onChange={() => this.setState({changed: true})}/>{' '}
            {changed && <button className="btn btn-sm btn-outline-primary ml-2">Save</button>}
        </div>
      }
    </div>;
  }

  getScore() {
    const {criterion, application} = this.props;
    return application.scores.find(s => s.criterion == criterion.id);
  }

  saveScore = (e: FocusEvent<HTMLInputElement>) => {
    const {application, criterion} = this.props;
    const {reloadApplication} = this.context;
    const value = Number(e.target.value);
    if (!value || value > 10 || value < 0) return;
    const data = {application: application.id, criterion: criterion.id, score: value};
    sessionRequest(scoresUrl, {method: 'POST', data}).then(response => {
      if (response.status < 300) {
        this.setState({changed: false});
        reloadApplication(application.id);
      }
    })
  };

  deleteScore = () => {
    const {application} = this.props;
    const {reloadApplication} = this.context;
    const score = this.getScore();
    if (!score) return;
    sessionRequest(scoreUrl(score.id), {method: 'DELETE'}).then(response => {
      if (response.status < 300) reloadApplication(application.id);
    })
  }
}
