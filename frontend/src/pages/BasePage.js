import './BasePage.css'


export function BasePage(props) {
    const { pageIdx, totalPages } = props;

    return (
        <>
            <div>
                <nav className="navbar navbar-expand-lg navbar-light bg-light">
                    <img className="ms-2" src="assets/images/logo.svg" height="60"/>
                    {/* <span className="brand-logo" aria-label="brand-logo"></span> */}
                    <span className="ms-auto me-auto">Part {pageIdx} of {totalPages - 1}</span>
                </nav>
            </div>
            <div className="container-fluid">
                {/* <TopBar {...props}/> */}
                {props.children}
            </div>
        </>
    )
}