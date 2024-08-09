import { Button } from '@nextui-org/button';
import { Input } from '@nextui-org/input';
import React, { useState } from 'react';
import FileIcon from './Icons/FileIcon';
import FolderIcon from './Icons/FolderIcon';
import LayoutGridIcon from './Icons/LayoutGridIcon';
import ListIcon from './Icons/ListIcon';
import PlusIcon from './Icons/PlusIcon';
import UploadIcon from './Icons/UploadIcon';
import ListOrderedIcon from './Icons/ListOrderedIcon';
import files from '../files.json';
import FileLine from './FileLine';
import FileDetails from './FileDetails';
import WandIcon from './Icons/WandIcon';
import TelescopeIcon from './Icons/TelescopeIcon';
import TelescopeButton from './TelescopeButton';
import EnterIcon from './Icons/EnterIcon';
import ollamaWave from '../../../assets/ollama_wave.gif'
import llamaFsLogo from '../../../assets/llama_fs.png'

const supportedFileTypes = ['.pdf', '.txt', '.png', '.jpg', '.jpeg', '.pptx', '.docx', '.xlsx'];

function preorderTraversal(
  node: { name: string; children?: any[]; summary?: string; src_path?: string },
  prevfilename: string,
  depth: number,
  result: { filename: string; fullfilename: string; depth: number; summary?: string; src_path?: string }[] = [],
) {
  result.push({
    filename: node.name,
    fullfilename: `${prevfilename}/${node.name}`,
    depth,
    summary: node.summary,
    src_path: node.src_path,
  });

  if (node.children) {
    node.children.forEach((child) => {
      preorderTraversal(
        child,
        `${prevfilename}/${node.name}`,
        depth + 1,
        result,
      );
    });
  }

  return result;
}

function buildTree(paths) {
  const root = { name: 'root', children: [] };

  paths.forEach(({ src_path, dst_path, summary }) => {
    const parts = dst_path.split('/');
    let currentLevel = root.children;

    parts.forEach((part, index) => {
      let existingPath = currentLevel.find((p) => p.name === part);

      if (!existingPath) {
        if (index === parts.length - 1) {
          // It's a file, include the summary and source path
          existingPath = { name: part, summary: summary, src_path: src_path };
        } else {
          // It's a directory
          existingPath = { name: part, children: [] };
        }
        currentLevel.push(existingPath);
      }

      if (existingPath.children) {
        currentLevel = existingPath.children;
      }
    });
  });

  return root;
}


function MainScreen() {
  const [watchMode, setWatchMode] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePath, setFilePath] = useState('/Users/reibs/Projects/llama-fs/sample_data');
  const [loading, setLoading] = useState(false);

  // Function to handle file selection
  const handleFileSelect = (fileData: any) => {
    setSelectedFile(fileData);
  };

  const [newOldMap, setNewOldMap] = useState([]);
  const [preOrderedFiles, setPreOrderedFiles] = useState([]);
  // const preOrderedFiles = preorderTraversal(files, '', -1).slice(1);
  const [acceptedState, setAcceptedState] = React.useState([]);

  const handleBatch = async () => {
    setLoading(true);
    const response = await fetch('http://localhost:8000/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        path: filePath
        // path: '/Users/reibs/Projects/llama-fs/sample_data',
      }),
    });
    const data = await response.json();
    setNewOldMap(data);
    const treeData = buildTree(data);
    const preOrderedTreeData = preorderTraversal(treeData, '', -1).slice(1);
    setPreOrderedFiles(preOrderedTreeData);
    setAcceptedState(
      preOrderedTreeData.reduce(
        (acc, file) => ({ ...acc, [file.fullfilename]: false }),
        {},
      ),
    );
    setLoading(false);
  };
  const handleWatch = async () => {
    setLoading(true);
    const response = await fetch('http://localhost:8000/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        path: filePath
        // path: '/Users/reibs/Projects/llama-fs/sample_data',
      }),
    });
  };


  const handleConfirmSelectedChanges = async () => {
    const returnedObj = [];
    preOrderedFiles.forEach((file) => {
      const isAccepted = acceptedState[file.fullfilename];
      if (isAccepted) {
        const noRootFileName = file.fullfilename.replace('/root/', '');
        if (newOldMap.some((change) => change.dst_path === noRootFileName)) {
          const acceptedChangeMap = newOldMap.find(
            (change) => change.dst_path === noRootFileName,
          );
          returnedObj.push({
            base_path: filePath,
            src_path: acceptedChangeMap.src_path,
            dst_path: acceptedChangeMap.dst_path
          });
        }
      }
    });

    console.log(returnedObj)

    // commit endpoint only supports 1 change at a time
    returnedObj.forEach(async (change) => {
      const response = await fetch('http://localhost:8000/commit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(change),
      });
      console.log(response);
    });

    // clean objects
    setNewOldMap([]);
    setPreOrderedFiles([]);
    setAcceptedState([]);
  };

  // Add the className 'dark' to main div to enable dark mode
  return (
    <div className="flex h-screen w-full">
      <div className="bg-gray-100 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4 flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <FolderIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
          <span className="font-medium text-gray-700 dark:text-gray-300">
            Llama-FS
          </span>
        </div>
        <nav className="flex flex-col gap-2" >
          <div className="bg-white p-2 rounded">
            /Users/reibs/Projects/llama-fs/sample_data
          </div>
          <div className="bg-white p-2 rounded">
            /Users/reibs/Downloads
          </div>
          <div className="bg-white p-2 rounded">
            /Users/reibs/Projects/ollama
          </div>
        </nav>
      </div>
      <div className="flex-1 flex flex-col">
        <div className="bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Input
              className="w-max rounded-lg"
              placeholder="Enter file path"
              type="text"
              onChange={(e) => setFilePath(e.target.value)}
              defaultValue='/Users/reibs/Projects/llama-fs/sample_data'
              style={{
                width: '400px',
              }}
            />
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => handleBatch()}>
              <WandIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </Button>
            <div onClick={() => setWatchMode(!watchMode)}>
              <TelescopeButton isLoading={watchMode} />
            </div>
          </div>
        </div>
        <div className="flex-1 flex">
          <div
            className="w-1/2 overflow-auto p-4 space-y-2 border-r border-gray-200 dark:border-gray-700"
            style={{ maxHeight: 'calc(100vh - 4rem)' }}
          >
            {loading ? (
              // Existing loading block
              <div className="flex flex-col items-center">
                <h2 className="text-lg font-semibold mb-2">Reading and classifying your files...</h2>
                <div className="flex justify-center" style={{ width: '50%' }}>
                  <img src={ollamaWave} alt="Loading..." style={{ width: '100%' }} />
                </div>
              </div>
            ) : preOrderedFiles.length === 0 ? (
              // Render llamaFsLogo and supported file types when not loading and no files
              <div className="flex flex-col items-center" style={{ height: '100%' }}>
                <h1 className="text-lg font-semibold mb-2">Llama-FS</h1>
                <p>Organize your drive with LLMs. </p>
                <div className="flex justify-center" style={{ width: '50%' }}>
                  <img src={llamaFsLogo} alt="Llama FS Logo" style={{ width: '100%' }} />
                </div>
                <p className="text-center mt-4">Supported file types:</p>
                <ul className="list-disc text-center">
                  {supportedFileTypes.map((type, index) => (
                    <li key={index}>{type}</li>
                  ))}
                </ul>
              </div>
            ) : (
              // Existing file details block
              <FileDetails fileData={selectedFile} />
            )}
            {preOrderedFiles.map((file) => (
              <div onClick={() => handleFileSelect(file)}>
                <FileLine
                  key={file.fullfilename}
                  filename={file.filename}
                  indentation={file.depth}
                  fullfilename={file.fullfilename}
                  acceptedState={acceptedState}
                  setAcceptedState={setAcceptedState}
                />
              </div>
            ))}
          </div>
          <div className="w-1/2 overflow-auto p-4">
            <FileDetails fileData={selectedFile} />
            {/* Container for explaining the data in the file line that's selected */}
            {/* This container will be populated with content dynamically based on the selected FileLine */}
          </div>
        </div>
      </div>
      <div className="fixed inset-x-0 bottom-2 flex justify-center">
        <Button
          className="bg-green-300 text-gray-700 rounded p-3"
          onClick={() => handleConfirmSelectedChanges()}
        >
          Confirm selected changes
        </Button>
      </div>
    </div>
  );
}

export default MainScreen;
