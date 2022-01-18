import { useEffect, useReducer, useState } from "react"

import * as api from '../api';

function useStudy() {
    const [ initState, dispatchState] = useReducer(nextState, {})
    const [ outState, setOutState ] = useState({})

    const questions = [
        "It was easy to decide which slider to adjust next",
        "It was easy to decide how far to adjust the slider",
        "I was confident about my interactions with the sliders",
        "I could interprete which feature individual sliders represented"
    ]

    const nasa_tlx_dimensions = [
        {dimension: "Mental Demand", question: "How mentally demanding was the task?"},
        {dimension: "Physical Demand", question: "How physically demanding was the task?"},
        {dimension: "Temporal Demand", question: "How hurried or rushed was the pace of the task?"},
        {dimension: "Performance", question: "How successful were you in accomplishing what you were asked to do?"},
        {dimension: "Effort", question: "How hard did you have to work to accomplish your level of performance?"},
        {dimension: "Frustration", question: "How insecure, discouraged, irritated, stressed, and annoyed were you?"}
    ]

    const likert_scales = [
        ["Strongly Agree", false],
        ["Agree", false],
        ["Neutral", false],
        ["Disagree", false],
        ["Strongly Disagree", false],
    ]
    

    function newEdit(oldState, action) {
        return {...oldState, init: oldState.init.map((entry) =>
            (entry.page == "DISPLAY_TASK"
                && entry.content.slider_type === action.content.slider_type
                && entry.content.targ_edit.length === action.content.num_sliders) 
                
                ? {page: entry.page, content: {...entry.content, edits: action.content.edits} } 
                : entry
        )}
    }

    function goToPage(oldState, action) {
        return {...oldState, curIdx: action.content};
    }

    function nextPage(oldState, action) {
        return {...oldState, curIdx: oldState.curIdx + 1};
    }

    function init(oldState, action) {
        return action.content
    }

    function likert(oldState, action) {
        let page = oldState.init[oldState.curIdx]
        let newLikertItems = page.content.likert.map(i => i.question === action.content.question
            ? action.content
            : i)
        let cp = {...oldState}
        cp.init[oldState.curIdx].content.likert = newLikertItems
        return cp
    }

    function nasa_tlx(oldState, action) {
        let page = oldState.init[oldState.curIdx]
        let newTLXItems = page.content.nasa_tlx.map(i => i.dimension === action.content.dimension
            ? {...i, answer: action.content.answer}
            : i)
        let cp = {...oldState}
        cp.init[oldState.curIdx].content.nasa_tlx = newTLXItems
        return cp     
    }

    function nextState(oldState, action) {
        switch(action.type) {
            case "init":
                return init(oldState, action)
            case "newEdit":
                return newEdit(oldState, action)
            case "nextPage":
                return nextPage(oldState, action)
            case "goToPage":
                return goToPage(oldState, action)
            case "likert":
                return likert(oldState, action)
            case "nasa-tlx":
                return nasa_tlx(oldState, action)
        }
    }

    useEffect(() => {
        if (initState.init !== undefined) {
            setOutState(initState.init[initState.curIdx])
        }
    }, [initState])

    useEffect(
        () => api.getConfig()
                .then(study => {
                    let tmpState = []
                    tmpState.push({page: "DISPLAY_PRIVACY_AGREEMENT", content: null})
                    tmpState.push({page: "DISPLAY_INSTRUCTIONS", content: null})

                    for (let i=0; i < study.length; i++) {
                        let tmpStudy = {
                            ...study[i],
                            targ_edit: study[i].targ_edit.map((e) => ({id: e[0], value: e[1]})),
                            edits: study[i].edits.map((e) => ({id: e[0], value: e[1]}))
                        }
                        tmpState.push({page: "DISPLAY_TASK", content: tmpStudy})
                        tmpState.push({page: "DISPLAY_POST_TASK_SURVEY", content: {
                            num_sliders: study[i].targ_edit.length,
                            slider_type: study[i].slider_type,
                            taskid: study[i].taskid,
                            likert: questions.map(q => ({question: q, scales: likert_scales})),
                            nasa_tlx: nasa_tlx_dimensions.map(d => ({dimension: d.dimension, question: d.question, answer: ""}))
                        }})
                    }

                    tmpState.push({page: "DISPLAY_POST_SURVEY", content: null})
                    tmpState.push({page: "DISPLAY_THANK_YOU_REDIRECT", ontent: null})
                    return dispatchState({type: 'init', content: {curIdx: 0, init: tmpState}})
    }), [])

    return [outState, initState, dispatchState]
}

export { useStudy };