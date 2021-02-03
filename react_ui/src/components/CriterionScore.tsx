import React, {FocusEvent} from 'react';

import {AppContext, Application, Criterion, Score} from "components/types";
import Icon from "util_components/bootstrap/Icon";
import ConfirmButton from "util_components/bootstrap/ConfirmButton";
import {commentsUrl, commentUrl, scoresUrl, scoreUrl} from "urls";
import {username} from "components/utils";
import moment from "moment";

type CriterionScoreProps = {
  criterion: Criterion,
  application: Application
}

type CriterionScoreState = {
  changed?: boolean,
  showComment?: boolean
}

const initialState: CriterionScoreState = {};

export default class CriterionScore extends React.Component<CriterionScoreProps, CriterionScoreState> {
  state = initialState;
  static contextType = AppContext;

  render() {
    const {criterion, application} = this.props;
    const {changed, showComment} = this.state;
    const {user} = this.context;

    const scores = application.scores.filter(s => s.criterion == criterion.id);
    const myOrgScore = application.scores.find(s =>
      s.criterion == criterion.id && s.evaluator.organization == user.organization);

    const comments = application.comments.filter(s => s.criterion == criterion.id);

    return <div className="ml-2 mb-2">
      {criterion.name}:
      {!myOrgScore &&
      <div className="form-inline">
        <input type="number" min="0" max="10" className="form-control form-control-sm"
               onBlur={this.saveScore}
               onChange={() => this.setState({changed: true})}/>{' '}
        {changed && <button className="btn btn-sm btn-outline-primary ml-2">Save</button>}
      </div>
      }

      {scores.map((score: Score) =>
        <div key={score.id}>
          <strong>{score.score}</strong> (by {username(score.evaluator)})
          {score.evaluator.organization == user.organization &&
          <button className="btn btn-light btn-sm text-secondary p-1"
                  onClick={() => this.setState({showComment: true})}>
            <Icon icon="chat_bubble_outline"/>
          </button>
          }
          {score.evaluator.id == user.id &&
          <ConfirmButton className="btn-light btn-sm text-danger p-1 btn-trans" confirm="Delete score?"
                         onClick={this.deleteScore}>
            <Icon icon="clear"/>
          </ConfirmButton>
          }
        </div>
      )}

      {comments.length > 0 &&
      <div className="mt-1 mb-3">
        {comments.map((comment) =>
          <div key={comment.id} className="d-flex">
            <div>
              <strong>{username(comment.evaluator)} </strong>
              <small>{moment(comment.created_at).format('lll')}:</small><br/>
              {comment.comment}
            </div>
            {comment.evaluator.id == user.id &&
            <div>
              <ConfirmButton className="btn-light btn-sm text-danger p-1 btn-trans" confirm="Delete comment?"
                             onClick={() => this.deleteComment(comment.id)}>
                <Icon icon="clear"/>
              </ConfirmButton>
            </div>
            }
          </div>
        )}
      </div>
      }

      {showComment && <>
        <textarea className="form-control" rows={3} onBlur={this.saveComment}/>
        <button className="btn btn-sm btn-outline-primary btn-block mt-1">Save</button>
      </>}
    </div>;
  }

  saveScore = (e: FocusEvent<HTMLInputElement>) => {
    const {application, criterion} = this.props;
    const {reloadApplication, request} = this.context;
    const value = Number(e.target.value);
    if (!e.target.value || value > 10 || value < 0) return;
    const data = {application: application.id, criterion: criterion.id, score: value};
    request(scoresUrl, {method: 'POST', data}).then((response: Response) => {
      if (response.status < 300) {
        this.setState({changed: false});
        reloadApplication(application.id);
      }
    })
  };

  saveComment = (e: FocusEvent<HTMLTextAreaElement>) => {
    const {application, criterion} = this.props;
    const {reloadApplication, request} = this.context;
    const value = e.target.value;
    if (!value) return;
    const data = {application: application.id, criterion: criterion.id, comment: value};
    request(commentsUrl, {method: 'POST', data}).then((response: Response) => {
      if (response.status < 300) {
        this.setState({showComment: false});
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

  deleteComment = (commentId: number) => {
    const {application, criterion} = this.props;
    const {reloadApplication, request, user} = this.context;
    request(commentUrl(commentId), {method: 'DELETE'}).then((response: Response) => {
      if (response.status < 300) reloadApplication(application.id);
    })
  }
}
