import "./Filmstrips.css";
import * as FilmstripController from "./FilmstripController";
import { Fragment, useEffect, useState, useRef } from "react";

function FilmstripRangeSlider({
  edit,
  edits,
  idx,
  seed,
  onChange,
  onSliderImageUpdate = null,
}) {
  const [x, setX] = useState();
  const [value, setValue] = useState(NaN);
  const [width, setWidth] = useState(0);
  const [img_sources, isUpdating] = FilmstripController.useImages(
    edits,
    idx,
    seed
  );
  const firstRun = useRef(0);
  const containerRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [pointerStatus, setPointerStatus] = useState("");

  useEffect(() => {
    document.addEventListener("mouseup", () => {
      setPointerStatus("UP");
      setDragging(false);
    });
    return () => {
      document.addEventListener("mouseup", null);
    };
  }, []);
  useEffect(() => {
    if (containerRef.current !== null) {
      let el = containerRef.current;
      let rect = el.getBoundingClientRect();
      setWidth(rect.right - rect.left);
      setX((rect.right - rect.left) / 2);
    }
  }, [containerRef]);
  useEffect(() => {
    if (width > 0) {
      let val = Math.round((x / width) * 100);
      setValue(val);
    }
  }, [x]);
  useEffect(() => {
    if (onChange && value != NaN) {
      if (firstRun.current < 2) {
        firstRun.current += 1;
        return;
      }
      onChange(value, edit.id, pointerStatus);
    }
  }, [value, pointerStatus]);
  useEffect(() => {
    if (onSliderImageUpdate) {
      onSliderImageUpdate(isUpdating, idx);
    }
  }, [isUpdating]);

  function handleMouseMove(evt) {
    if (dragging) {
      let target = evt.target;
      let rect = target.getBoundingClientRect();
      let clientX = evt.clientX;
      let x = FilmstripController.computeX(clientX, rect);
      setX(x);

      setPointerStatus("DRAG");
    }
    evt.preventDefault();
  }

  function handleClick(evt) {
    let target = evt.target;
    let rect = target.getBoundingClientRect();
    let clientX = evt.clientX;

    let x = FilmstripController.computeX(clientX, rect);
    setX(x);
  }
  return (
    <div
      ref={containerRef}
      className="filmstrip-container"
      draggable={false}
      onClick={handleClick}
      onPointerDown={(_) => {
        setPointerStatus("DOWN");
        setDragging(true);
      }}
      onPointerLeave={(evt) => {
        if (dragging) {
          let target = evt.target;
          let rect = target.getBoundingClientRect();
          let width = rect.right - rect.left;
          if (evt.clientX < rect.left + width / 2) {
            setX(FilmstripController.computeX(rect.left, rect));
          } else {
            setX(FilmstripController.computeX(rect.right, rect));
          }
        }
      }}
      onPointerUp={(_) => {
        setPointerStatus("UP");
        setDragging(false);
      }}
      onPointerMove={(evt) => {
        handleMouseMove(evt);
      }}
    >
      <div className="row gx-0 filmstrip" draggable={false}>
        {img_sources.map((i) => (
          <div className="col p-0">
            <img
              className={isUpdating ? "isupdate" : ""}
              src={
                i.data.length === 0
                  ? "https://via.placeholder.com/60x60.png"
                  : "data:image/png;base64, " + i.data
              }
            />
          </div>
        ))}
      </div>

      <div draggable="false" class="filmstrip-header" style={{ left: x - 4 }} />
    </div>
  );
}

export default function Filmstrips({ edits, seed, onChange = null, onSliderImageUpdate = null }) {
  return (
    <Fragment>
      {edits.map((edit, idx) => (
        <div div="configuration-root">
          <FilmstripRangeSlider
            seed={seed}
            idx={idx}
            edits={edits}
            edit={edit}
            onChange={(val, id, status) =>
              onChange ? onChange(val, id, edits, status) : null
            }
            onSliderImageUpdate={onSliderImageUpdate}
          />
          Value: {edit.value}
        </div>
      ))}
    </Fragment>
  );
}
