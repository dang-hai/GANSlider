const ROOT = process.env.REACT_APP_ROOT_DIR;

export function getImage(edits, seed, size, signal = null) {
  if (edits === undefined) {
    return Promise.resolve("");
  }
  return fetch(ROOT + "api/image", {
    method: "POST",
    signal: signal,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      edits: edits,
      size: size,
      seed: seed,
    }),
  })
    .then((res) => res.json())
    .catch((err) => {
      // console.warn(err)
      return "";
    });
}

export function log_survey(data) {
  fetch(ROOT + "api/log/post_task_survey", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data.content),
  });
}

export function log_task(status, taskid, edits, extra) {
  fetch(ROOT + "api/log/task", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      timestamp: Date.now(),
      status: status,
      taskid: taskid,
      edits: edits,
      extra: extra
    }),
  });
}

export function log_final_survey(payload) {
  fetch(ROOT + "api/log/final_survey", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function getConfig() {
  return fetch(ROOT + "api/user_study/config").then((res) => res.json());
}

export function logInteraction(edits, seed, sliderType, taskid, status) {
  fetch(ROOT + "api/log/interaction", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      edits: edits,
      size: 0,
      seed: seed,
      timestamp: Date.now(),
      sliderType: sliderType,
      taskid: taskid,
      status: status,
    }),
  });
}

export function log_slider_image_update(isUpdating, idx, taskid) {
  fetch(ROOT + "api/log/slider_filmstrip_update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      isUpdating: isUpdating,
      taskid: taskid,
      idx:idx,
      timestamp: Date.now()
    })
  });
}
