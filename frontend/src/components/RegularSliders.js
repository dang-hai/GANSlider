import { Fragment, useState, useEffect } from "react";

export default function RegularSliders(props) {
    const { edits } = props;
    const { onChange } = props;
    const [ pointerStatus, setPointerStatus ] = useState("");

    const [ changed, setChanged ] = useState(undefined);

    useEffect(() => {
        document.addEventListener('mouseup', () => {
            setPointerStatus("UP")
        });
        return () => {
            document.addEventListener('mouseup', null)
        }
    }, [])

    useEffect(() => {
        if (changed !== undefined) {
            onChange(changed.value, changed.id, edits, pointerStatus)
        }
    }, [ changed, pointerStatus])

    return (
        <Fragment>
        {
            edits.map(
                e => (
                <label>
                    <input
                        style={{width: "100%"}}
                        type="range"
                        onPointerDown={evt => setPointerStatus("DOWN")}
                        onPointerUp={evt => setPointerStatus("UP")}
                        onPointerMove={evt => {
                            if (pointerStatus === "DOWN") {
                                setPointerStatus("DRAG");
                            }
                        }}
                        onChange={evt => setChanged({value: evt.target.value, id: e.id})}/>
                    Value: {e.value}
                </label>
            ))
        }
        </Fragment>
    )
}