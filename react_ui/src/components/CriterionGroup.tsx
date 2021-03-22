import React, {FocusEvent} from 'react';
import moment from "moment";

import {AppContext, Application, ApplicationRound, CriterionGroup} from "components/types";
import CriterionScore from "components/CriterionScore";
import {commentsUrl, commentUrl} from "urls";
import {username} from "components/utils";
import ConfirmButton from "util_components/bootstrap/ConfirmButton";
import Icon from "util_components/bootstrap/Icon";

type CriterionGroupProps = {
  applicationRound: ApplicationRound,
  group: CriterionGroup,
  application: Application
}

type CriterionGroupState = {
  comment: string,
  editingComment?: boolean
}

const initialState: CriterionGroupState = {
  comment: ""
};

export default class CriterionGroupComponent extends React.Component<CriterionGroupProps, CriterionGroupState> {
  state = initialState;
  static contextType = AppContext;

  render() {
    const {group, applicationRound, application} = this.props;
    const {comment, editingComment} = this.state;
    const {user} = this.context;

    const groupCriteria = applicationRound.criteria.filter(c => c.group == group.id);
    const subGroups = applicationRound.criterion_groups.filter(g => g.parent == group.id);
    const submitted = applicationRound.submitted_organizations.includes(user.organization);

    if (!subGroups.length && !groupCriteria.length) return null;

    const comments = application.comments.filter(s => s.criterion_group == group.id);
    const myComment = comments.find(c => c.evaluator.id == user.id);
    const showNewComment = !submitted && groupCriteria.length > 0 && !myComment;

    const editCommentField = () =>
      <>
        <textarea className="form-control" rows={3} onBlur={this.saveComment} maxLength={500}
                  value={comment} autoFocus={editingComment}
                  onChange={(e) => this.setState({comment: e.target.value})}/>
        <small className="text-black-50">
          500 characters max{comment.length > 0 && <>, {500 - comment.length} left.</>}
        </small>
        {comment.length > 0 &&
        <button className="btn btn-sm btn-outline-primary btn-block mt-1">Save</button>
        }
      </>;

    return <div className="ml-2 mt-4" key={group.name}>
      {subGroups.length ? <h5 className="text-primary">{group.name}</h5> :
        <h6 className="text-secondary">{group.name}</h6>}
      {subGroups.map(childGroup =>
        <CriterionGroupComponent key={childGroup.name} group={childGroup} applicationRound={applicationRound}
                                 application={application}/>
      )}
      {groupCriteria.map(criterion =>
        <CriterionScore key={criterion.name} criterion={criterion} application={application} readOnly={submitted}/>
      )}

      {comments.length > 0 &&
      <div className="mt-1 mb-3 ml-2">
        {comments.map((comment) =>
          <div key={comment.id} className="d-flex">
            <div className={editingComment ? "flex-grow-1" : ''}>
              <strong>{username(comment.evaluator)} </strong>
              <small>{moment(comment.created_at).format('lll')}:</small><br/>
              {comment.evaluator.id == user.id && editingComment ? editCommentField() : comment.comment}
            </div>
            {comment.evaluator.id == user.id && !submitted && !editingComment &&
            <div className="flex-grow-1">
              <button className="btn btn-light btn-sm p-1 btn-trans"
                      onClick={() => this.setState({editingComment: true, comment: comment.comment})}>
                <Icon icon="mode_edit"/>
              </button>
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

      {showNewComment && <div className="mt-3 ml-2">
        {group.abbr || group.name} - Reasoning and conclusions:
        {editCommentField()}
      </div>}
    </div>;
  }

  saveComment = (e: FocusEvent<HTMLTextAreaElement>) => {
    const {application, group} = this.props;
    const {reloadApplication, request, user} = this.context;
    const comments = application.comments.filter(s => s.criterion_group == group.id);
    const myComment = comments.find(c => c.evaluator.id == user.id);
    const value = e.target.value;
    if (!value) return;

    const req =
      myComment ?
        request(commentUrl(myComment.id), {method: 'PATCH', data: {comment: value}})
        :
        request(commentsUrl, {
          method: 'POST',
          data: {application: application.id, criterion_group: group.id, comment: value}
        });

    req.then((response: Response) => {
      if (response.status < 300) {
        this.setState({comment: '', editingComment: false});
        reloadApplication(application.id);
      }
    })
  };

  deleteComment = (commentId: number) => {
    const {application} = this.props;
    const {reloadApplication, request} = this.context;
    request(commentUrl(commentId), {method: 'DELETE'}).then((response: Response) => {
      if (response.status < 300) reloadApplication(application.id);
    })
  }
}
