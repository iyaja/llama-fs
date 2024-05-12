import { Button } from '@nextui-org/button';
import React from 'react';
import FileIcon from './Icons/FileIcon';
import FolderIcon from './Icons/FolderIcon';
import LayoutGridIcon from './Icons/LayoutGridIcon';
import ListIcon from './Icons/ListIcon';
import PlusIcon from './Icons/PlusIcon';
import UploadIcon from './Icons/UploadIcon';
import ListOrderedIcon from './Icons/ListOrderedIcon';
import files from '../files.json';
import FileLine from './FileLine';

function preorderTraversal(
  node: { name: string; children?: any[] },
  prevfilename: string,
  depth: number,
  result: { filename: string; fullfilename: string; depth: number }[] = [],
) {
  result.push({
    filename: node.name,
    fullfilename: `${prevfilename}/${node.name}`,
    depth,
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

function MainScreen() {
  // console.log(files);
  const preOrderedFiles = preorderTraversal(files, '', -1).slice(1);
  console.log(preOrderedFiles);
  const [acceptedState, setAcceptedState] = React.useState(
    preOrderedFiles.reduce(
      (acc, file) => ({ ...acc, [file.fullfilename]: false }),
      {},
    ),
  );
  console.log(acceptedState);

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
            <Button variant="ghost">
              <LayoutGridIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </Button>
            <Button variant="ghost">
              <ListIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </Button>
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-2">
            <Button variant="ghost">
              <ListOrderedIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </Button>
            <Button variant="ghost">
              <UploadIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </Button>
            <Button variant="ghost">
              <PlusIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-auto p-4 space-y-2">
          {preOrderedFiles.map((file) => (
            <FileLine
              key={file.fullfilename}
              filename={file.filename}
              indentation={file.depth}
              fullfilename={file.fullfilename}
              acceptedState={acceptedState}
              setAcceptedState={setAcceptedState}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default MainScreen;
