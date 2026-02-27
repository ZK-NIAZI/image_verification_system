import { useRef, useState, useCallback } from 'react';

const MAX_SIZE = 10 * 1024 * 1024; // 10 MB
const ALLOWED = ['image/jpeg', 'image/png', 'image/jpg'];

export default function UploadZone({ file, onFileSelect, disabled }) {
    const inputRef = useRef(null);
    const [dragActive, setDragActive] = useState(false);

    const handleFile = useCallback((f) => {
        if (!f) return;
        if (!ALLOWED.includes(f.type)) {
            alert('Only JPEG and PNG images are supported.');
            return;
        }
        if (f.size > MAX_SIZE) {
            alert('File is too large. Maximum size is 10 MB.');
            return;
        }
        onFileSelect(f);
    }, [onFileSelect]);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (disabled) return;
        const f = e.dataTransfer.files[0];
        handleFile(f);
    }, [disabled, handleFile]);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (disabled) return;
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, [disabled]);

    const handleClick = () => {
        if (!disabled) inputRef.current?.click();
    };

    const handleChange = (e) => {
        handleFile(e.target.files[0]);
        e.target.value = '';
    };

    const formatSize = (bytes) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <>
            <div
                className={`upload-zone ${dragActive ? 'upload-zone--active' : ''} ${disabled ? 'upload-zone--disabled' : ''}`}
                onClick={handleClick}
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                id="upload-zone"
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept="image/jpeg,image/png"
                    onChange={handleChange}
                    id="file-input"
                />
                <span className="upload-zone__icon">
                    {dragActive ? '📥' : '📸'}
                </span>
                <p className="upload-zone__title">
                    {dragActive ? 'Drop your image here' : 'Drag & drop or click to upload'}
                </p>
                <p className="upload-zone__subtitle">
                    Supports <span>JPEG</span> and <span>PNG</span> · Max 10 MB
                </p>
            </div>

            {file && (
                <div className="preview">
                    <img
                        src={URL.createObjectURL(file)}
                        alt="Preview"
                        className="preview__image"
                    />
                    <div className="preview__info">
                        <p className="preview__name">{file.name}</p>
                        <p className="preview__size">{formatSize(file.size)}</p>
                    </div>
                    <button
                        className="preview__remove"
                        onClick={(e) => {
                            e.stopPropagation();
                            onFileSelect(null);
                        }}
                        title="Remove file"
                        id="remove-file"
                    >
                        ✕
                    </button>
                </div>
            )}
        </>
    );
}
