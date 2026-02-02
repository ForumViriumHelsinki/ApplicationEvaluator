import React from 'react';
import ExcelJS from 'exceljs';
import { saveAs } from 'file-saver';
import type {
  Application,
  ApplicationRound,
  Comment,
  CriterionGroup,
  Score,
} from '/components/types';
import { getTotalScore } from '/components/utils';

type ExportScoresWidgetProps = {
  applicationRound: ApplicationRound;
};

type ExportScoresWidgetState = {
  expanded?: boolean;
};

const initialState: ExportScoresWidgetState = {};

export default class ExportScoresWidget extends React.Component<
  ExportScoresWidgetProps,
  ExportScoresWidgetState
> {
  state = initialState;

  render() {
    const {} = this.props;
    const { expanded } = this.state;
    return (
      <div className="dropdown mt-2">
        <button
          className="btn btn-compact btn-sm btn-outline-dark dropdown-toggle"
          onClick={() => this.setState({ expanded: !expanded })}
        >
          Export scores
        </button>
        {expanded && (
          <div className="dropdown-menu show">
            <button className="dropdown-item" onClick={() => this.export('.xlsx')}>
              .xlsx
            </button>
            <button className="dropdown-item" onClick={() => this.export('.csv')}>
              .csv
            </button>
            <button className="dropdown-item" onClick={() => this.exportSummary('.xlsx')}>
              .xlsx (summary)
            </button>
            <button className="dropdown-item" onClick={() => this.exportSummary('.csv')}>
              .csv (summary)
            </button>
          </div>
        )}
      </div>
    );
  }

  // Export individual scores, one score per row:
  async export(format: string) {
    const applicationRound = this.props.applicationRound;
    const { applications, name } = applicationRound;
    const criteria = Object.fromEntries(applicationRound.criteria.map((c) => [c.id, c]));
    const groups = Object.fromEntries(applicationRound.criterion_groups.map((c) => [c.id, c.name]));

    const columns = [
      { name: 'Application', value: (_s: Score, a: Application) => a.name },
      {
        name: 'Criterion group',
        value: (s: Score | Comment, _a: Application) =>
          groups[(s as Comment).criterion_group || criteria[(s as Score).criterion].group],
      },
      {
        name: 'Criterion',
        value: (s: Score, _a: Application) => criteria[s.criterion]?.name,
      },
      {
        name: 'Organization',
        value: (s: Score, _a: Application) => s.evaluator.organization,
      },
      {
        name: 'First name',
        value: (s: Score, _a: Application) => s.evaluator.first_name,
      },
      {
        name: 'Last name',
        value: (s: Score, _a: Application) => s.evaluator.last_name,
      },
      { name: 'Score', value: (s: Score, _a: Application) => s.score },
      { name: 'Comment', value: (s: Comment, _a: Application) => s.comment },
    ];

    const rows: (string | number | undefined)[][] = [columns.map((c) => c.name)];

    applications.forEach((a) => {
      a.scores.forEach((s) =>
        rows.push(columns.map((c) => c.value(s as Score & Comment, a) as string)),
      );
      a.comments.forEach((s) =>
        rows.push(columns.map((c) => c.value(s as Score & Comment, a) as string)),
      );
    });

    await this.writeFile(rows, name + format, format);
  }

  // Export score summary, one application per row:
  async exportSummary(format: string) {
    const applicationRound = this.props.applicationRound;
    const { applications, name } = applicationRound;
    const groups = applicationRound.criterion_groups;
    const groupIndex = Object.fromEntries(groups.map((g: CriterionGroup) => [g.id, g]));

    const columns = [
      { name: 'Application number', value: (a: Application) => a.name },
      { name: 'Id', value: (a: Application) => a.application_id },
      ...groups.map((g: CriterionGroup) => ({
        name: g.name,
        value: (a: Application) => a.groupScores[g.id],
      })),
      { name: 'Total score', value: (a: Application) => getTotalScore(a) },
      { name: 'Approved', value: (a: Application) => a.approved },
      {
        name: 'Comments',
        value: (a: Application) =>
          a.comments
            .map(
              (c) =>
                `${c.evaluator.first_name} ${c.evaluator.last_name} - ${groupIndex[c.criterion_group].name}: ${c.comment}`,
            )
            .join('\n'),
      },
    ];

    const rows: (string | number | boolean | undefined)[][] = [columns.map((c) => c.name)];

    applications.forEach((a: Application) => rows.push(columns.map((c) => c.value(a) as string)));

    await this.writeFile(rows, name + format, format);
  }

  private async writeFile(rows: (string | number | boolean | undefined)[][], filename: string, format: string) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Scores');

    // Add rows to worksheet
    rows.forEach((row) => {
      worksheet.addRow(row);
    });

    if (format === '.xlsx') {
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      saveAs(blob, filename);
    } else if (format === '.csv') {
      const buffer = await workbook.csv.writeBuffer();
      const blob = new Blob([buffer], { type: 'text/csv;charset=utf-8' });
      saveAs(blob, filename);
    }
  }
}
