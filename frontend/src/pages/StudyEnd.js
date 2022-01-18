import { useEffect, useRef, useState } from "react"

export function StudyEnd() {
    const [ sec, setSec ] = useState(10);
    const [ redirectLink, setRedirectLink ] = useState("");

    const interval = useRef(null);

    interval.current = setInterval(() => {
        setSec(prev => Math.max(0, prev - 1));
    }, 1000)

    useEffect(() => {
        if (sec == 0) {
            if (interval.current !== null) {
                clearInterval(interval.current);
                setRedirectLink(process.env.REACT_APP_PROLIFIC_URL)
            }
        }

    }, [ sec ])

    useEffect(() => {
        if (redirectLink) {
            window.location.replace(redirectLink)
        }
        
    }, [redirectLink])
    
    return (
        <div style={{maxWidth: 900, marginLeft: "auto", marginRight: "auto"}}>
            <h1>Thank You For Participating In This Study</h1>
            <p>You will be redirected Prolific in {sec} seconds ...</p>

            {
                (redirectLink)
                    ? <p>If the automatic forwarding does not work, kindly use <a href={process.env.REACT_APP_PROLIFIC_URL}>this link</a> to manually return to Prolific.</p>
                    : ""
            }
        </div>
    )
}