import { Button } from '@nextui-org/button';
import FileIcon from './FileIcon';
import FolderIcon from './FolderIcon';
import LayoutGridIcon from './LayoutGridIcon';
import ListIcon from './ListIcon';
import PlusIcon from './PlusIcon';
import UploadIcon from './UploadIcon';
import ListOrderedIcon from './ListOrderedIcon';

function MainScreen() {
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
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow">
            <div className="p-4 flex items-center gap-4">
              <FolderIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Documents
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Document.pdf
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Presentation.pptx
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow">
            <div className="p-4 flex items-center gap-4">
              <FolderIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Images
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Image1.jpg
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Image2.png
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow">
            <div className="p-4 flex items-center gap-4">
              <FolderIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Music
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Song1.mp3
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Song2.mp3
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow">
            <div className="p-4 flex items-center gap-4">
              <FolderIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Videos
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Video1.mp4
              </span>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow pl-8">
            <div className="p-4 flex items-center gap-4">
              <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                Video2.mov
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainScreen;
