import React from 'react';
import { useState, useReducer, useEffect } from "react";
import "./Questionaire.css";

export function LikertQuestion(props) {
  const { item, onChange, alertMissingInput } = props;

  function handleChecked(val) {
    onChange({
      ...item,
      scales: item.scales.map(s => (val === s[0]) ? [s[0], !s[1]]: [s[0], false])});
  }

  return (
    <tr className={`likert-questions ${alertMissingInput && !item.scales.map(s=>s[1]).some() ? 'question-error': ''}`}>
      <td className="likert-question-text">{item.question}</td>
      {
      item.scales.map((val, idx) =>(
        <td width={80}>
          <div className="likert-scale-div">
            <input
              key={val[0]}
              type="radio"
              checked={val[1]}
              onChange={() => handleChecked(val[0])}/>
          </div>
        </td>
      ))
    }
    </tr>
  )
}

function LikertScale(props) {
  const { scales } = props;

  function renderHeaders() {
    const headers = ["", ...scales]
    return headers.map(h => <th>{h}</th>)
  }

  return (
    <div>
      <table >
        <thead>
          {renderHeaders()}
        </thead>
        <tbody>
          {props.children}       
        </tbody>
      </table>
    </div>

  )
}

function NASA_TLX_DIMENSION(props) {
  const { dimension, question, answer, onChange, alertMissingInput } = props;
  const [checked, dispatch] = useReducer(toggle, initChecked());

  function initChecked() {
    let res = [];
    for (let i = 0; i < 20; i++) {
      res.push({ id: i, checked: false, hovered: false });
    }
    return res;
  }

  function toggle(state, action) {
    switch(action.type) {
      case "hoverStart":
        return state.map((elem, idx) =>
          idx === action.idx
            ? { id: elem.id, checked: elem.checked,  hovered: true }
            : { id: elem.id,  checked: elem.checked, hovered: false }
        );
      case "hoverEnd":
        return state.map((elem, idx) =>
          idx === action.idx
            ? { id: elem.id, checked: elem.checked, hovered: false }
            : { id: elem.id, checked: elem.checked, hovered: false }
        );
      case "select":
          return state.map((elem, idx) =>
            idx === action.idx
              ? { id: elem.id, checked: !elem.checked,  hovered: false }
              : { id: elem.id, checked: false,  hovered: false }
          );
    }
    return 
  }

  // useEffect(() => {

  // }, [ checked ])

  function renderScale(num, checked, dimension, answer) {
    let scale = [];
    for (let i = 0; i < num; i++) {
      const lr = i % 2 === 0 ? "left" : "right";
      const styleChecked = answer === i ? "checked" : "";
      const hoveredStyle = checked[i].hovered ? "hovered" : "";
      scale.push(
        <td
          onMouseEnter={() => dispatch({type: "hoverStart", idx: i})}
          onMouseLeave={() => dispatch({type: "hoverEnd", idx: i})}
          onClick={() => {
            onChange({dimension: dimension, value: i})
            dispatch({type: "select", idx: i})
          }}
          className={`${lr} ${styleChecked} ${hoveredStyle}`}
        ></td>
      );
    }
    return scale;
  }
  return (
    <div className={`${alertMissingInput && (checked.filter(i => i.checked).length == 0) ? 'question-error': ''}`}>
      <h3 className="nasa-dimension-header">{dimension}</h3>
      <h5>{question}</h5>
      <table className="nasa-dimension-table">
        <tr className="top">{renderScale(20, checked, dimension, answer)}</tr>
        <tr className="bottom">{renderScale(20, checked, dimension, answer)}</tr>
        <tr>
          <td colSpan={10}>Low</td>
          <td colSpan={10} style={{textAlign:"right"}}>High</td>
        </tr>
      </table>
    </div>
  );
}


export { LikertScale, NASA_TLX_DIMENSION };
