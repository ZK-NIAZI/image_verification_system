export default function ResultCard({ result, verbose }) {
    if (!result) return null;

    const isPass = result.valid;
    const details = result.result?.details || {};
    const stageTimes = result.result?.stage_times_ms || {};
    const inferenceTime = result.result?.inference_time_ms ?? result.inference_time_ms;

    // Determine which checks passed/failed/were skipped
    const checks = getChecks(result, details);

    return (
        <div className={`result ${isPass ? 'result--pass' : 'result--fail'}`} id="result-card">
            {/* Header */}
            <div className="result__header">
                <div className="result__icon">
                    {isPass ? '✓' : '✗'}
                </div>
                <div>
                    <div className="result__title">
                        {isPass ? 'Verification Passed' : 'Verification Failed'}
                    </div>
                    <div className="result__reason">
                        {result.reason || result.result?.reason || 'Unknown'}
                    </div>
                </div>
            </div>

            {/* Body */}
            <div className="result__body">
                {/* Check breakdown */}
                <div className="checks">
                    {checks.map((check) => (
                        <div className="check" key={check.name}>
                            <div className={`check__icon check__icon--${check.status}`}>
                                {check.status === 'pass' ? '✓' : check.status === 'fail' ? '✗' : '—'}
                            </div>
                            <span className="check__label">{check.label}</span>
                            <span className={`check__status check__status--${check.status}`}>
                                {check.statusLabel}
                            </span>
                        </div>
                    ))}
                </div>

                {/* Message */}
                <div className="result__message">
                    {result.message || result.result?.message || 'No additional details.'}
                </div>

                {/* Verbose timing */}
                {verbose && inferenceTime !== undefined && (
                    <div className="verbose">
                        <div className="verbose__title">⏱ Performance Breakdown</div>
                        <div className="verbose__grid">
                            <div className="verbose__item">
                                <div className="verbose__label">Total Time</div>
                                <div className="verbose__value">{inferenceTime} ms</div>
                            </div>
                            {Object.entries(stageTimes).map(([stage, ms]) => (
                                <div className="verbose__item" key={stage}>
                                    <div className="verbose__label">{stage}</div>
                                    <div className="verbose__value">{ms} ms</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function getChecks(result, details) {
    const reason = result.reason || result.result?.reason || '';

    // Map check stages to their status
    const lightingStatus = details.lighting?.status;
    const clarityStatus = details.clarity?.status;
    const faceStatus = details.face?.status;

    // If no detailed info (minimal response), infer from reason
    if (!lightingStatus && !clarityStatus && !faceStatus) {
        return inferChecksFromReason(reason, result.valid);
    }

    return [
        {
            name: 'lighting',
            label: '💡 Lighting',
            status: lightingStatus === 'GOOD_LIGHTING' ? 'pass' : lightingStatus ? 'fail' : 'skip',
            statusLabel: lightingStatus === 'GOOD_LIGHTING' ? 'Passed' : lightingStatus || 'Skipped',
        },
        {
            name: 'clarity',
            label: '🔍 Clarity',
            status: clarityStatus === 'CLEAR' ? 'pass' : clarityStatus ? 'fail' : 'skip',
            statusLabel: clarityStatus === 'CLEAR' ? 'Passed' : clarityStatus || 'Skipped',
        },
        {
            name: 'face',
            label: '👤 Face Detection',
            status: faceStatus === 'SUCCESS' ? 'pass' : faceStatus ? 'fail' : 'skip',
            statusLabel: faceStatus === 'SUCCESS' ? 'Passed' : faceStatus || 'Skipped',
        },
    ];
}

function inferChecksFromReason(reason, valid) {
    if (valid) {
        return [
            { name: 'lighting', label: '💡 Lighting', status: 'pass', statusLabel: 'Passed' },
            { name: 'clarity', label: '🔍 Clarity', status: 'pass', statusLabel: 'Passed' },
            { name: 'face', label: '👤 Face Detection', status: 'pass', statusLabel: 'Passed' },
        ];
    }

    const lightingFail = ['TOO_DARK', 'TOO_BRIGHT'].includes(reason);
    const clarityFail = reason === 'TOO_BLURRY';
    const faceFail = ['NO_FACE', 'MULTIPLE_FACES'].includes(reason);

    return [
        {
            name: 'lighting',
            label: '💡 Lighting',
            status: lightingFail ? 'fail' : (clarityFail || faceFail) ? 'pass' : 'skip',
            statusLabel: lightingFail ? reason : (clarityFail || faceFail) ? 'Passed' : 'Unknown',
        },
        {
            name: 'clarity',
            label: '🔍 Clarity',
            status: clarityFail ? 'fail' : faceFail ? 'pass' : lightingFail ? 'skip' : 'skip',
            statusLabel: clarityFail ? reason : faceFail ? 'Passed' : lightingFail ? 'Skipped' : 'Unknown',
        },
        {
            name: 'face',
            label: '👤 Face Detection',
            status: faceFail ? 'fail' : (lightingFail || clarityFail) ? 'skip' : 'skip',
            statusLabel: faceFail ? reason : 'Skipped',
        },
    ];
}
