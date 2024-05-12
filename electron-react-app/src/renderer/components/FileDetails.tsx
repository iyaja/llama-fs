import React from 'react';

interface FileDetailsProps {
    fileData: {
        filename: string;
        fullfilename: string;
        summary?: string; // Optional property for file summary
        src_path?: string; // Optional property for original source path
    };
}

const FileDetails: React.FC<FileDetailsProps> = ({ fileData }) => {
    if (!fileData) {
        return <div className="text-center text-gray-600 py-4">No file selected</div>;
    }

    return (
        <div className="file-details-container p-4 border rounded shadow-lg bg-white dark:bg-gray-800">
            <h3 className="text-lg font-bold text-gray-800 dark:text-white">{fileData.filename}</h3>
            {fileData.src_path && (
                <p className="text-sm text-gray-400 line-through">{fileData.src_path}</p>
            )}
            <p className="text-sm text-gray-600 dark:text-gray-400">{fileData.fullfilename}</p>
            {fileData.summary && (
                <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-700 rounded">
                    <h4 className="text-sm font-semibold text-gray-800 dark:text-white">Summary</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">{fileData.summary}</p>
                </div>
            )}
        </div>
    );
};

export default FileDetails;