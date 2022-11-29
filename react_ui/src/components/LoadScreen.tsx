import React from "react";
import CenteredSpinner from "/util_components/bootstrap/CenteredSpinner";

export default class LoadScreen extends React.Component {
  render() {
    return <div className="container">
      <div className="jumbotron mt-5 bg-light shadow text-center">
        <img className="w-50" src="images/PNG_AI4CITIES_Logo.png"/>
        <h3>FVH Application Evaluator</h3>
        <CenteredSpinner/>
      </div>
    </div>;
  }
}
