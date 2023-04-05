import React from 'react';
import {Application, ApplicationRound, CriterionGroup} from "/components/types";
import {organizationColor} from "/components/utils";

type ApplicationScoresTableProps = {
  application: Application,
  applicationRound: ApplicationRound,
  showEvaluators: boolean,
  onOrganizationHover?: (org: string | null) => any
}

type ApplicationScoresTableState = {}

const initialState: ApplicationScoresTableState = {};

export default class ApplicationScoresTable extends React.Component<ApplicationScoresTableProps, ApplicationScoresTableState> {
  state = initialState;

  render() {
    const {application, applicationRound, showEvaluators, onOrganizationHover} = this.props;
    const thresholdGroups = applicationRound.criterion_groups.filter(g => g.threshold);
    const scoresIndex = applicationRound.scoring_model === 'Evaluators average' ? application.scoresByEvaluator
        : application.scoresByOrganization;
    const organizations = Object.keys(scoresIndex);
    const showOrganizations = showEvaluators && organizations.length > 1;

    const GroupScore = ({group, groupScores}: { group: CriterionGroup, groupScores: any }) => {
      const groupScore = groupScores[group.id];
      return <td key={group.id} className={groupScore < group.threshold ? 'text-danger font-weight-bold' : ''}>
        {groupScore && groupScore.toPrecision(2)}
      </td>;
    };

    const LegendPill = ({org}: { org: string }) =>
      <span className="rounded-pill d-inline-block" style={this.legendPillStyle(org)}></span>;

    const selectNone = () => onOrganizationHover && showOrganizations && onOrganizationHover(null);

    return <table className="table table-hover table-sm mt-2 border-bottom mb-0">
      <thead>
      <tr>
        {showOrganizations && <>
          <th></th>
          <th></th>
        </>}
        {thresholdGroups.map(group => <th key={group.abbr}>{group.abbr}</th>)}
      </tr>
      </thead>
      <tbody onMouseOut={selectNone}>
      {showOrganizations && Object.entries(scoresIndex).map(
        ([organization, {groupScores, score}]) =>
          <tr key={organization}
              onMouseOver={() => onOrganizationHover && onOrganizationHover(organization)}>
            <td><LegendPill org={organization}/> {organization}</td>
            <td className="font-weight-bold">{score.toPrecision(3)}</td>
            {thresholdGroups.map(group =>
              <GroupScore key={group.id} group={group} groupScores={groupScores}/>)}
          </tr>
      )}
      <tr onMouseOver={selectNone}>
        {showOrganizations && <>
          <td style={{paddingLeft: 29}}>Total</td>
          <td className="font-weight-bold">{application.score?.toPrecision(3)}</td>
        </>}
        {thresholdGroups.map(group =>
          <GroupScore key={group.id} group={group} groupScores={application.groupScores}/>)}
      </tr>
      </tbody>
    </table>;
  }

  private legendPillStyle(org: string) {
    const color = organizationColor(org);
    return {
      backgroundColor: color + '10',
      width: 20, height: 20,
      verticalAlign: 'bottom',
      border: `2px solid ${color}`
    };
  }
}
