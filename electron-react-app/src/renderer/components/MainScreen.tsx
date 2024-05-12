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
      let existingPath = currentLevel.find(p => p.name === part);

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
  const [filePath, setFilePath] = useState('');

  // Function to handle file selection
  const handleFileSelect = (fileData: any) => {
    setSelectedFile(fileData);
  };

  const [preOrderedFiles, setPreOrderedFiles] = useState([]);
  // const preOrderedFiles = preorderTraversal(files, '', -1).slice(1);
  const [acceptedState, setAcceptedState] = React.useState([]);

  const handleBatch = async () => {
    const response = await fetch('http://localhost:8000/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        // path: filePath
        path: '/Users/reibs/Projects/llama-fs/sample_data'
      }),
    });
    const data = await response.json();
    console.log('DATA!!')
    console.log(data)
    const treeData = buildTree(data);
    const preOrderedTreeData = preorderTraversal(treeData, '', -1).slice(1);
    setPreOrderedFiles(preOrderedTreeData);
    setAcceptedState(
      preOrderedTreeData.reduce(
        (acc, file) => ({ ...acc, [file.fullfilename]: false }),
        {},
      ),
    );
  };
  console.log(watchMode)

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
        <nav className="flex flex-col gap-2" />
      </div>
      <div className="flex-1 flex flex-col">
        <div className="bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Input
              className="flex-1 rounded-lg"
              placeholder="Enter file path"
              type="text"
              onChange={(e) => setFilePath(e.target.value)}
            />
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => handleBatch()}>
              <WandIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </Button>
            <div onClick={() => setWatchMode(!!!watchMode)}>
              <TelescopeButton isLoading={watchMode} />
            </div>
          </div>
        </div>
        <div className="flex-1 flex">
          <div
            className="w-1/2 overflow-auto p-4 space-y-2 border-r border-gray-200 dark:border-gray-700"
            style={{ maxHeight: 'calc(100vh - 4rem)' }}
          >
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
      <div className="flex-1">
        <button className="bg-gray-400 text-white w-full rounded p-4">
          Accept
        </button>
      </div>
    </div>
  );
}

export default MainScreen;
