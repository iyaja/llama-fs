import React from 'react';

interface FileDetailsProps {
    fileData: {
        filename: string;
        fullfilename: string;
        // Add any other relevant props for the file data here
    };
}

const FileDetails: React.FC<FileDetailsProps> = ({ fileData }) => {
    if (!fileData) {
        return <div>No file selected</div>;
    }

    return (
        <div className="file-details-container p-4 border rounded shadow-lg">
            <h3 className="text-lg font-bold">{fileData.filename}</h3>
            <p className="text-sm">{fileData.fullfilename}</p>
            {/* Render other file details here */}
        </div>
    );
};

export default FileDetails;
