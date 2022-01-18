import { useState } from 'react';

import './Instructions.css'
import Filmstrips from '../components/Filmstrips'
import RegularSliders from '../components/RegularSliders';
import { BaseButton } from '../components/BaseButton';
import * as TaskController from './TaskPageController';

export function Instructions(props) {
    const { onClick } = props;
    
    const [ filmEdits, setFilmEdits ] = useState([{id: 0, value: 0.0}]);
    const [ regularEdits, setRegularEdits ] = useState([{id: 0, value: 0.0}]);
    
    let [ filmImageData ] = TaskController.useImage(filmEdits, 0)
    let [ regularImageData ] = TaskController.useImage(regularEdits, 0)
    
    function renderImage(imgData) {
        return (imgData.length > 0)
        ? <img src={"data:image/png;base64, " + imgData}/>
        : <img src="https://via.placeholder.com/256x256.png"/>
    }

    return (
        <div className="instructions-root">
            <h1>Instructions</h1>
            <p>
                The goal of this study is to evaluate two types of sliders for the manipulation
                of image features. Below you see  wo types of sliders. Try moving each slider by dragging
                the slider header and observe how the image on right changes in response.
                You can play with the sliders to become familiar with the interaction before
                moving to the actual task.
            </p>
            <div class="regular-slider">
                <h3>Slider Type 1</h3>
                <RegularSliders edits={filmEdits} seed={0} onChange={value =>
                    TaskController.new_edit(value, 0, filmEdits).then(setFilmEdits)
                }/>
                <div>{renderImage(filmImageData, filmEdits)}</div>
            </div>
            <div class="filmstrip-slider">
                <h3>Slider Type 2</h3>
                <Filmstrips edits={regularEdits} seed={0} onChange={value => 
                    TaskController.new_edit(value, 0, regularEdits).then(setRegularEdits)
                }/>
                <div>
                    {renderImage(regularImageData)}
                </div>
            </div>
            <BaseButton onClick={() => onClick()}/>
        </div>
    )
}