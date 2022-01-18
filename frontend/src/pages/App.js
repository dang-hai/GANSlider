import { useStudy } from './StudyController';
import { PostSurveyPage as FinalSurveyPage } from './PostSurveyPage';
import { PostTaskSurveyPage } from './SurveyPage';
import { PrivacyAgreement } from './PrivacyAgreement';
import { Loading } from './LoadingPage';
import { StudyEnd } from './StudyEnd';
import { BasePage } from './BasePage';

import TaskPage from './TaskPage';
import ReactJson from 'react-json-view'
import { Instructions } from './Instructions';

import * as api from '../api';

export default function App() {
  const [state, initState, dispatchState] = useStudy();
  const DEBUG = parseInt(process.env.REACT_APP_GANSLIDER_DEBUGGING);

  function renderNext(data) {
    if (data === undefined) return;

    switch (data.page) {
      case "DISPLAY_PRIVACY_AGREEMENT":
        return (
          <PrivacyAgreement onClick={_ => dispatchState({ type: "nextPage" })} />
        )
      case "DISPLAY_INSTRUCTIONS":
        return <Instructions onClick={_ => dispatchState({ type: "nextPage" })} />
      case "DISPLAY_TASK":
        return <TaskPage
          seed={data.content.seed}
          edits={data.content.edits}
          targEdits={data.content.targ_edit}
          taskid={data.content.taskid}
          sliderType={data.content.slider_type}
          onChange={(edit) => dispatchState({
            type: "newEdit", content: {
              edits: edit,
              slider_type: data.content.slider_type,
              num_sliders: data.content.targ_edit.length
            }
          })}
          onFinished={_ => {
            dispatchState({ type: "nextPage" });
          }} />
      case "DISPLAY_POST_TASK_SURVEY":
        return <PostTaskSurveyPage
          dispatchState={dispatchState}
          onFinished={_ => {
            api.log_survey(data)
            dispatchState({ type: "nextPage" })
          }}
          data={data.content}
        />
      case "DISPLAY_POST_SURVEY":
        return <FinalSurveyPage onFinished={_ => {
          dispatchState({ type: "nextPage" })
        }} />
      case "DISPLAY_THANK_YOU_REDIRECT":
        return <StudyEnd />
      default:
        return <Loading />
    }
  }

  function renderDebugging(state) {
    if (initState.init === undefined) return
    return (
      <div style={{ display: 'grid', gridTemplateColumns: '300px auto' }}>
        <div style={{ paddingLeft: 16, paddingTop: 48, height: 600, overflow: 'scroll' }}>
          {
            initState.init.map((item, idx) => (
              <div style={{ marginBottom: 32, backgroundColor: (initState.curIdx === idx) ? "yellow" : "" }}>
                {idx}. <button onClick={() => dispatchState({ type: "goToPage", content: idx })}>GO {item.page}</button>
                <br />
                {(item.content) ? <ReactJson
                  src={item.content}
                  enableEdit={false}
                  enableClipboard={false}
                  enableAdd={false}
                  enableDelete={false}
                  collapsed={initState.curIdx !== idx}
                  theme="monokai" /> : ""}
              </div>
            ))
          }
        </div>
        {
          renderNext(state)
        }
      </div>

    )
  }

  return (
    <BasePage pageIdx={initState.curIdx} totalPages={initState.init ? initState.init.length : 0}>
      {(DEBUG) ? renderDebugging(state) : renderNext(state)}
    </BasePage>
  )
}