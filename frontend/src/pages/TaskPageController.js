import { useEffect, useReducer, useRef, useState } from "react";
import * as api from "../api";
import { check_valid } from "../utils";

let MIN_VALUE = -5;
let MAX_VALUE = 5;
let TOTAL_RANGE = Math.abs(MAX_VALUE - MIN_VALUE);

function keepAvailableImage(state, action) {
  return action.length === 0 ? state : action;
}

export function logEdits(edits, seed, sliderType, taskid, status) {
  api.logInteraction(edits, seed, sliderType, taskid, status);
}

function update(signal, edits, seed, dispatchImage, setIsUpdating) {
  let tmpImage = "";

  if (signal.aborted) {
    // console.log("ABORTED", data, edits)
    return;
  }

  // console.log("REQUEST", edits, seed)
  api.getImage(edits, seed, 256).then((data) => {
    if (check_valid(data, edits)) {
      // console.log("SUCCESS", data, edits, seed)
      tmpImage = data.content.image_data;
      dispatchImage(tmpImage);
      setIsUpdating(false);
    } else {
      if (signal.aborted) {
        // console.log("ABORTED", data, edits)
        return;
      }
      setTimeout(
        () => update(signal, edits, seed, dispatchImage, setIsUpdating),
        100
      );
    }
  });
}

export function useImage(edits, seed) {
  const [image, dispatchImage] = useReducer(keepAvailableImage, "");
  const [isUpdating, setIsUpdating] = useState(true);

  useEffect(() => {
    let abortController = new AbortController();
    setTimeout(() => {
      if (!abortController.signal.aborted) {
        update(
          abortController.signal,
          edits,
          seed,
          dispatchImage,
          setIsUpdating
        );
      }
    }, 200);
    return () => {
      // console.log("ABORTING PEDNING REQUESTS")
      abortController.abort();
    };
  }, [...edits.map((elem) => elem.value)]);

  return [image, isUpdating];
}

export function new_edit(new_value, id, edits) {
  return Promise.resolve(
    edits.map((e) =>
      e.id === id
        ? {
            id: id,
            value: parseFloat(
              (MIN_VALUE + (new_value / 100) * TOTAL_RANGE).toFixed(1)
            ),
          }
        : { ...e }
    )
  );
}

export function getTargetEdits(num) {
  let targEdits = [];

  for (let i = 0; i < num; i++) {
    targEdits.push({
      id: i,
      value: parseFloat((MIN_VALUE + Math.random() * TOTAL_RANGE).toFixed(1)),
    });
  }

  return Promise.resolve(targEdits);
}

export function getNextTask(currNumSliders) {
  if (currNumSliders + 1 == 10) {
    return Promise.resolve(null);
  }

  let tmp = [];
  for (let j = 0; j < currNumSliders + 1; j++) {
    tmp.push({ id: String(j), value: 0.0 });
  }
  return Promise.resolve(tmp);
}
