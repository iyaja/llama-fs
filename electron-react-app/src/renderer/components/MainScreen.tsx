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
      <div className="bg-gradient-to-b from-blue-600 to-blue-700 dark:from-blue-900 dark:to-blue-950 border-r border-blue-800 p-4 flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <WandIcon className="h-6 w-6 text-blue-100" />
          <span className="font-bold text-blue-50 text-lg">
            FileFlow
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
              // Render FileFlow landing page with key information
              <div className="flex flex-col items-center justify-center h-full bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
                <div className="max-w-2xl text-center space-y-6">
                  {/* Logo and Title */}
                  <div>
                    <div className="flex justify-center mb-4">
                      <img src={llamaFsLogo} alt="FileFlow Logo" style={{ width: '120px' }} />
                    </div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-400 dark:to-blue-300 bg-clip-text text-transparent mb-2">
                      FileFlow
                    </h1>
                    <p className="text-xl text-gray-600 dark:text-gray-300 font-medium">
                      AI-Powered Intelligent File Organization
                    </p>
                  </div>

                  {/* Value Proposition */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                    <p className="text-gray-700 dark:text-gray-200 text-lg">
                      <span className="font-semibold">Your files organized intelligently.</span> Never waste time manually organizing files again.
                    </p>
                  </div>

                  {/* Key Features */}
                  <div className="grid grid-cols-2 gap-4 text-left">
                    <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
                      <p className="font-semibold text-blue-900 dark:text-blue-300 mb-1">⚡ Blazingly Fast</p>
                      <p className="text-sm text-blue-800 dark:text-blue-200">Most operations complete in &lt;500ms</p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-4 border border-green-200 dark:border-green-700">
                      <p className="font-semibold text-green-900 dark:text-green-300 mb-1">🔒 Privacy First</p>
                      <p className="text-sm text-green-800 dark:text-green-200">Local processing option with Ollama</p>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/30 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
                      <p className="font-semibold text-purple-900 dark:text-purple-300 mb-1">🧠 Learns from You</p>
                      <p className="text-sm text-purple-800 dark:text-purple-200">Watch mode learns your patterns</p>
                    </div>
                    <div className="bg-orange-50 dark:bg-orange-900/30 rounded-lg p-4 border border-orange-200 dark:border-orange-700">
                      <p className="font-semibold text-orange-900 dark:text-orange-300 mb-1">✨ Smart Organization</p>
                      <p className="text-sm text-orange-800 dark:text-orange-200">Understands file content with AI</p>
                    </div>
                  </div>

                  {/* How to Use */}
                  <div className="bg-gray-800 dark:bg-gray-900 rounded-lg p-6 text-left space-y-3 border border-gray-700">
                    <p className="font-semibold text-white text-lg mb-4">How to Get Started:</p>
                    <div className="space-y-2 text-gray-100 text-sm">
                      <p><span className="font-semibold">1. Enter a path:</span> Type a directory path in the input above</p>
                      <p><span className="font-semibold">2. Process:</span> Click the wand icon for batch mode or telescope for watch mode</p>
                      <p><span className="font-semibold">3. Review:</span> See AI-suggested organization in the tree</p>
                      <p><span className="font-semibold">4. Approve:</span> Accept/reject changes and confirm</p>
                    </div>
                  </div>

                  {/* Supported File Types */}
                  <div className="text-left">
                    <p className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Supported File Types:</p>
                    <div className="grid grid-cols-2 gap-2">
                      {supportedFileTypes.map((type, index) => (
                        <span key={index} className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-3 py-1 rounded text-sm">
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Operating Modes */}
                  <div className="border-t border-gray-300 dark:border-gray-700 pt-6">
                    <p className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Two Operating Modes:</p>
                    <div className="grid grid-cols-2 gap-4 text-left">
                      <div className="bg-blue-100 dark:bg-blue-900/20 rounded-lg p-4">
                        <p className="font-semibold text-blue-900 dark:text-blue-300 mb-2">📁 Batch Mode</p>
                        <p className="text-sm text-blue-800 dark:text-blue-200">Process a directory, review suggestions, apply changes</p>
                      </div>
                      <div className="bg-cyan-100 dark:bg-cyan-900/20 rounded-lg p-4">
                        <p className="font-semibold text-cyan-900 dark:text-cyan-300 mb-2">👁️ Watch Mode</p>
                        <p className="text-sm text-cyan-800 dark:text-cyan-200">Continuous monitoring that learns from your edits</p>
                      </div>
                    </div>
                  </div>
                </div>
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
