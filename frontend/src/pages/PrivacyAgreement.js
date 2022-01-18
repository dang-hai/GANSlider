import { useState } from 'react';
import { BaseButton } from '../components/BaseButton';
import './PrivacyAgreement.css';

export function PrivacyAgreement(props) {
    const { onClick } = props;

    const [agreed, setAgreed] = useState(false);

    function toggle(event) {
        let checked = event.target.checked
        setAgreed(checked)
    }

    function handleClick(event) {
        onClick(agreed)
    }

    return (
        <div className="privacy-agreement-page">
            <div className="privacy-agreement-page-sec1">

                <h1>Generative Sliders For Image Manipulation</h1>

                <p>
                    <span className="privacy-agreement-page-section-point">Purpose and Tasks: </span>
                    Thank you for your participation in this study. In the following, you will be given a sequence 
                    of image manipulation tasks followed by short surveys to elicit your thoughts on the provided interactive elements.
                    In this study we are trying to understand how users can be supported to effectively generate images with deep learning models.
                    The learnings from this study may help to design new interactive elements in image editing programs like Photoshop.
                    Your answers will be provided through rating scales, or free-form text fields. Answers must be given in English.
                </p>

                <p>
                    <span className="privacy-agreement-page-section-point">Time Commitment: </span>
                    Participation in this study will take about 35 minutes. This survey is supposed to be completed in one sitting.
                </p>

                <p>
                    <span className="privacy-agreement-page-section-point">Suitability for the study: </span>
                    Legally competent adults are allowed as participants. The following criteria are required: 
                    Generally healthy and able to complete the tasks on a desktop device.
                </p>

                <p>
                    <span className="privacy-agreement-page-section-point">Voluntary participation: </span>
                    Participation in the survey is voluntary. You have the right to discontinue participation 
                    at any time without obligation to disclose any specific reasons.
                </p>

                <p>
                    <span className="privacy-agreement-page-section-point">Possible risks and their prevention: </span>
                    The experiment is not expected to carry any risks to the participants. At any time you feel the need
                    to discontinue the experiment, you are free to do so.
                </p>

                <p>
                    <span className="privacy-agreement-page-section-point">Collection of data: </span>
                    1) Survey responses; 2) Demographics (age, gender identification, profession).
                </p>

                <p>
                    <span className="privacy-agreement-page-section-point">Anonymity, secure storage, confidentiaity: </span>
                    The data will be used for scientific purposes only and are confidential. All data will be anonymised. 
                    No explicit clues of your identity will be left to the stored data. All data will be stored securely. 
                    According to the data storage plan of the project and to support open science, 
                    the anonymous data will be made available via platforms such as osf.io.
                </p>

                <p>
                    <span className="privacy-agreement-page-section-point">Supervision & Research Group: </span>
                    The study is conducted under the supervision of Hai Dang (<a href="mailto: hai.dang@uni-bayreuth.de">hai.dang@uni-bayreuth.de</a>). We are a research group on HCI and AI at the University of Bayreuth <a href="https://www.hciai.uni-bayreuth.de/en/index.html">https://www.hciai.uni-bayreuth.de/en/index.html</a>
                </p>
            </div>
            <div className="privacy-agreement-page-sec2">
                <h1>Data Policy: Information about study participation and data processing</h1>
                
                <p>1. I am aware that the collection, processing, and use of my data takes place on a voluntary basis. The participation in the study can be cancelled by me at any time without stating reasons, without this resulting in any disadvantages for me. In the event of termination, all data recorded by me up to that point will be irrevocably deleted after the data collection phase.</p>
                <p>2. I agree that my data including my demographics and my replies may be collected, stored and processed in anonymized form. No personal data is processed.</p>
                <p>3. The results and original data of this study will be published as a scientific publication. This is done in a completely anonymous form, i.e. the data cannot be assigned to the respective participants in the study. The completely anonymized data of this study will be made available as "open data" in a secure, internet-based repository called Open Science Framework (https://osf.io/). This study thus follows the recommendations of the German Research Foundation (DFG) for quality assurance in terms of verifiability and reproducibility of scientific results, as well as optimal post-use of data.</p>

                <p id="agreed-checkbox"><input checked={agreed} onChange={toggle} type="checkbox"/>I hereby confirm that I have read and understood the above declaration of consent. I confirm that I voluntarily participate in the study and agree to the processing of my data by the University of Bayreuth, Germany.</p>
            </div>

            <BaseButton disabled={!agreed} onClick={handleClick}/>
        </div>
    )
}