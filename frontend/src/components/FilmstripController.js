import * as api from '../api'
import { useEffect, useState, useReducer, useRef } from "react";

let IMAGES_PER_FILMSTRIP = 5;
let MIN_VALUE = -5;
let MAX_VALUE = 5;
let TOTAL_RANGE = Math.abs(MAX_VALUE - MIN_VALUE);
let STEP_SIZE = TOTAL_RANGE / (IMAGES_PER_FILMSTRIP - 1)

/**
 * Check if there are images in the filmstrips that need to be loaded.
 * @param {str} images 
 * @returns boolean - wether additional images have to be loaded
 */
function checkMissingImages(images) {
    return !images.map(entry => entry.length).every(l => l > 0) 
}

function loadMissingImages(images, filmstrip_edits, seed) {
    // If image has already been loaded then simply resolve old value
    // otherwise fetch new image.

    const keepLoadedImages = (imageData, i) => (imageData.length > 0) 
        ? Promise.resolve(imageData) 
        : api.getImage(filmstrip_edits[i], seed, 50).then(res => res.content.image_data)

    const toLoad = images.map(keepLoadedImages)
    return toLoad
}

/**
 * Shows the image content if present otherwise keep the previous state.
 * @param {*} state 
 * @param {*} action 
 */
function keepAvailableImage(prev, content) {
    let newState = content.map((elem, i) => (elem.length === 0) 
        ? {data: prev[i].data}
        : {data: elem}
    )
    return newState 
}

function computeFilmstripEdits(edits, idx) {
    let filmstrip_edits = [];

    for (let j=0; j<IMAGES_PER_FILMSTRIP; j++) {
        let edits_cp = JSON.parse(JSON.stringify(edits));
        edits_cp[idx] = { id: edits_cp[idx].id, value: MIN_VALUE + j * STEP_SIZE };
        filmstrip_edits.push(edits_cp);
    }
    
    return filmstrip_edits
}

function update(signal, idx, edits, seed, dispatchImages, setIsUpdating, tmpImages=["", "", "", "", ""]) {
    setIsUpdating(true)

    if (signal.aborted) {
      // console.log("ABORTED", data, edits)
      setIsUpdating(false)
      return
    }
    // console.log("REQUEST", edits, seed)

    let filmstrip_edits = computeFilmstripEdits(edits, idx);
    const toLoad = loadMissingImages(tmpImages, filmstrip_edits, seed)
    Promise.all(toLoad)
        .then(content => {
            dispatchImages(content)

            if (!tmpImages.every(item => item.length > 0) && !signal.aborted) {
                setTimeout(() => {
                    if (!signal.aborted) {
                        update(signal, idx, edits, seed, dispatchImages, setIsUpdating, content)
                    }
                }, 200)
            } else {
                setIsUpdating(false)
            }
    })
  }

export function useImages(edits, idx, seed) {
    const [ images, dispatchImages] = useReducer(keepAvailableImage, [
        {data: ""},{data: ""},{data: ""},{data: ""},{data: ""} 
    ])
    const [ isUpdating, setIsUpdating ] = useState(true);
    const prevEditVals = useRef(edits);

    useEffect(() => {
        let abortController = new AbortController()
        setTimeout(() => {
            if (!abortController.signal.aborted) {
                update(abortController.signal, idx, edits, seed, dispatchImages, setIsUpdating)
            }
        }, 200)

        return () => {
            // console.log("ABORTING PEDNING REQUESTS")
            if (abortController) {
                abortController.abort()
                setIsUpdating(false)
            }
        }
    },
    [
       edits
    ])

    return [images, isUpdating]
}


export function computeX(clientX, rect) {
    return Math.max(0, Math.min(rect.right - rect.left, clientX - rect.left));
}