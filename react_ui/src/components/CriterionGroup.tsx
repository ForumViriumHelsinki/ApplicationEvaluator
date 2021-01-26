import React from 'react';
import {Application, Criterion, CriterionGroup} from "components/types";
import CriterionScore from "components/CriterionScore";

type CriterionGroupProps = {
  group: CriterionGroup,
  allGroups: CriterionGroup[],
  criteria: Criterion[],
  application: Application
}

type CriterionGroupState = {}

const initialState: CriterionGroupState = {};

export default class CriterionGroupComponent extends React.Component<CriterionGroupProps, CriterionGroupState> {
  state = initialState;

  render() {
    const {group, allGroups, criteria, application} = this.props;
    const {} = this.state;

    const groupCriteria = criteria.filter(c => c.group == group.id);
    const subGroups = allGroups.filter(g => g.parent == group.id);

    if (!subGroups.length && !groupCriteria.length) return null;

    return <div className="ml-2 mt-4" key={group.name}>
      {subGroups.length ? <h5 className="text-primary">{group.name}</h5> : <h6 className="text-secondary">{group.name}</h6>}
      {subGroups.map(childGroup =>
        <CriterionGroupComponent key={childGroup.name} group={childGroup} allGroups={allGroups}
                                 criteria={criteria} application={application}/>
      )}
      {groupCriteria.map(criterion =>
        <CriterionScore key={criterion.name} criterion={criterion} application={application}/>
      )}
    </div>;
  }
}
