import "./SurveyPage.css"

import { LikertScale, LikertQuestion, NASA_TLX_DIMENSION } from "../components/Questionaire";
import { Fade } from 'react-reveal';
import { useState } from "react";
import { BaseButton } from "../components/BaseButton";

export function PostTaskSurveyPage(props) {
  const { onFinished, data, dispatchState } = props;
  const [alertMissingInput, setMissingInput] = useState(false);

  function handleOnLikertQuestionAnswer(ans) {
    dispatchState({
      type: 'likert',
      content: ans
    })
  }
  function handleTLXAnswered(ans) {
    dispatchState({
      type: 'nasa-tlx',
      content: {
        dimension: ans.dimension,
        answer: ans.value
      }
    })
  }
  function handleOnFinishedClicked() {
    let cond1 = data.likert.map(i => i.scales.map(s => s[1])).every(s => s.some(l => l == 1))
    let cond2 = data.nasa_tlx.map(i => i.answer).every(i => i !== "")

    if (cond1 && cond2) {
      onFinished()
    } else {
      setMissingInput(true)
    }
  }

  const scales = data.likert[0].scales.map(m => m[0]);
  return (
    <div className="survey-page-root">
      <div className="likert-scale-root">
        <h1>Part I</h1>
        <Fade collapse>
          <LikertScale scales={scales}>
            {data.likert.map(item => (
              <LikertQuestion
                alertMissingInput={alertMissingInput}
                item={item}
                onChange={handleOnLikertQuestionAnswer} />
            ))}
          </LikertScale>
        </Fade>
      </div>
      <div className="nasa-tlx-root">
        <h1>Part II</h1>
        {
          data.nasa_tlx.map(item => {
            return (
              <div className="nasa-dimension-root">
                <Fade collapse>
                  <NASA_TLX_DIMENSION
                    alertMissingInput={alertMissingInput}
                    question={item.question}
                    dimension={item.dimension}
                    answer={item.answer}
                    onChange={handleTLXAnswered} />
                </Fade>
              </div>
            )
          })
        }
      </div>
      <BaseButton
        onClick={() => handleOnFinishedClicked()}
        disabled={
          data.likert.map(i => i.scales.map(s => s[1])).some(s => s.every(l => l == 0)) ||
          data.nasa_tlx.map(i => i.answer).some(i => i === "")
        } />
    </div>
  )

}