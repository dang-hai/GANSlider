import { useState } from 'react';
import { BaseButton } from '../components/BaseButton';

import * as api from '../api';

import './PostSurveyPage.css'

export function PostSurveyPage(props) {
    const Q1 = "Is there anything you would add to the slider interface to improve it?"
    const Q2 = "Can you think of other use cases where the filmstrip slider interface would be helpful?"
    const Q3 = "Do you have any final remarks on the interpretabillity of the different slider types?"

    const [ answer1, setA1 ] = useState("");
    const [ answer2, setA2 ] = useState("");
    const [ answer3, setA3 ] = useState("");

    const { onFinished } = props;

    function handleFinishSurvey() {
        const payload = {questions: [
            {"question": Q1, "answer": answer1},
            {"question": Q2, "answer": answer2},
            {"question": Q3, "answer": answer3},
        ]}
        api.log_final_survey(payload);

        onFinished()
    }

    return (
        <div className="post-survey-page">
          <div>
            <h3>{Q1}</h3>
            <textarea value={answer1} onChange={evt => setA1(evt.target.value)}/>
        </div>
        <div>
            <h3>{Q2}</h3>
            <textarea value={answer2} onChange={evt => setA2(evt.target.value)}/>
        </div>
        <div>
            <h3>{Q3}</h3>
            <textarea value={answer3} onChange={evt => setA3(evt.target.value)}/>
        </div>
        <BaseButton onClick={() => handleFinishSurvey()}/>
        </div>
    )

}