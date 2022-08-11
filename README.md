# FVH Application Evaluator

The application evaluator is an open source web app for collaboratively evaluating applications (e.g. funding applications) by a set of weighted criteria, with support for multiple evaluating organizations.

It was developed and used for evaluating the applications in the AI4Cities project in 2021/22. The tool is suitable for cases where large numbers of applications, evaluators and evaluation criteria make it cumbersome and error-prone to use general purpose tools such a spreadsheets for the evaluation process.

<img width="1021" alt="application list screenshot" src="https://user-images.githubusercontent.com/58427813/184099914-392dd252-ca71-4cc7-b720-f1176c143dc7.png">

## Features

 * Definition of **Application rounds**, each round defining its own hierarchy of weighed **Evaluation criteria**, along with minimum average score thresholds for consideration
 * Batch import of **Applications** for consideration into each application round
 * Definition of **Evaluating organizations** with allocated evaluating users 
 * Allocation of applications to organizations; each application may be allocated to one or more organizations for evaluation
 * Evaluation UI used by the evaluators, allowing:
   * live overview of the evaluation process and completeness for each evaluators own organization while scoring
   * live computation of each applications final score as the weighted average of given scores
   * comparison of the final scores by evaluating organization, once the final scores have been submitted
   * graphical and tabular presentation of the scores of each application by evaluating organization and criteria for quick comparisons and better understanding of the relative strengths and weaknesses of different applications
 
<img width="1047" alt="scoring view screenshot" src="https://user-images.githubusercontent.com/58427813/184098299-1d1d76e2-074e-41f7-9776-d662695abc34.png">

## Maturity and future work (status summer 2022)

Currently, defining new application rounds and evaluation criteria and allocating applications is done through a less-than-perfectly intuitive Django-based admin interface; application scoring and result comparisons are done through the easy-to-use evaluator UI. The tool was used with success and favorable feedback for the complex use cases of the AI4Cities project, allowing > 100 individual evaluators from 6 different organizations to process hundreds of applications.

Possible next steps include improvements to the application round definition interfaces, and implementation of an application submittal interface for use directly by the applicants. So far, the timetable for that work has not been decided.

## Architecture and development

The application is based on a Django ReST Framework-based backend and a React/TypeScript/Bootstrap frontend. If you are interested in taking the tool into use and / or developing it further, feel free to contact johan.lindqvist(at)forumvirium.fi.

To start UI development:

* Install node.js
* Run:
```
npm install -g yarn
cd react_ui
yarn
yarn start
```
This should install all dependencies in react_ui/node_modules and start a react dev environment serving the UI app at localhost:3000 or a nearby available port.
