import "./TaskPage.css";
import * as TaskController from "./TaskPageController";
import RegularSliders from "../components/RegularSliders";
import Filmstrips from "../components/Filmstrips";
import { BaseButton } from "../components/BaseButton";
import { useEffect, useMemo, useState } from "react";

import * as api from "../api";

export default function Task(props) {
  const { onFinished, onChange, sliderType, edits, targEdits, seed, taskid } =
    props;
  let [imageURL] = TaskController.useImage(edits, seed);
  let [targetImage] = TaskController.useImage(targEdits, seed);
  const [ formData, setFormData ] = useState("")
  const [ toggled, setAnswerToggled ] = useState("");

  function handleSliderValueChange(value, id, edits, status) {
    TaskController.new_edit(value, id, edits).then((edits) => {
      onChange(edits);
      TaskController.logEdits(edits, seed, sliderType, taskid, status);
    });
  }

  function handleSliderImageUpdate(isUpdating, idx) {
    api.log_slider_image_update(isUpdating, idx, taskid);
  }

  function renderSlider(sliderType, edits, seed, handleSliderValueChange) {
    if (sliderType == "REGULAR") {
      return (
        <RegularSliders edits={edits} onChange={handleSliderValueChange} />
      );
    } else if (sliderType == "FILMSTRIP") {
      return<Filmstrips
          edits={edits}
          seed={seed}
          onChange={handleSliderValueChange}
          onSliderImageUpdate={handleSliderImageUpdate}
        />
      ;
    }
  }

  useEffect(() => {
    api.log_task("START", taskid, edits, "");
  }, [])

  function handleNext(event) {
    const status = event.target.value;
    setAnswerToggled(status);
    setFormData(status);
  }

  function handleSubmit(taskid, edits, formData) {
    console.log(taskid, edits, formData)
    api.log_task("FINISH", taskid, edits, formData);
    onFinished(true); 
  }

  return (
    <div className="root" key={edits.length}>
      <div>
        <h1>Task</h1>

        <p>
          You can adjust the sliders to edit your image on the right. Your task
          is to adjust the sliders in such a way that your generated image
          matches the target image below. You can decide to continue with
          the next task when you are done editing or when you decided to skip the current task
          (e.g the task maybe too difficult or too exhausting).
        </p>
        <p>
          <span style={{ fontWeight: 500 }}>Note:</span><br/>
          Due to the computationally intensive image generation process you may experience some
          delay when dragging the slider heads. The images will eventually align
          to the dragged value with a short delay.
        </p>
      </div>

      <div className="task-content">
        <div>
          <h3>Slider Adjustments</h3>
          <div class="task-sliders">
            { useMemo(() => renderSlider(sliderType, edits, seed, handleSliderValueChange), [ edits ])}
          </div>
        </div>

        <div className="task">
          <h3>Your Image</h3>
          {imageURL.length > 0 ? (
            <img src={"data:image/png;base64, " + imageURL} />
          ) : (
            <img src="https://via.placeholder.com/256x256.png" />
          )}

          <h3>Target Image</h3>
          {targetImage.length > 0 ? (
            <img src={"data:image/png;base64, " + targetImage} />
          ) : (
            <img src="https://via.placeholder.com/256x256.png" />
          )}
        </div>
      </div>

      <form className="mt-5">
        <label>Please indicate whether you are done editing or you decided to skip this task:</label><br/>
        <div className="mb-3 form-check">
          <input
            className="form-check-input"
            type="radio"
            alt="I give up, I can't solve this problem."
            id="giveup"
            name="answer"
            value="GIVEUP"
            onChange={handleNext}
          />
          <label className="form-check-label" for="giveup">
            I want to skip this task.
          </label>
        </div>
        <div className="mb-3 form-check">
          <input
            className="form-check-input"
            type="radio"
            alt="I am done with this task. "
            id="done"
            name="answer"
            value="DONE"
            onChange={handleNext}
          />
          <label className="form-check-label" for="done">
            I'm done with this task.
          </label>
        </div>
        <BaseButton disabled={toggled === ""} onClick={() => handleSubmit(taskid, edits, formData)}>
          Confirm
        </BaseButton>
      </form>
    </div>
  );
}
