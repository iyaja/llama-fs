import { Button } from '@nextui-org/button';
import FileIcon from './Icons/FileIcon';
import FolderIcon from './Icons/FolderIcon';
import MusicIcon from './Icons/MusicIcon';
import VideoIcon from './Icons/VideoIcon';
import ImageIcon from './Icons/ImageIcon';
import CheckIcon from './Icons/CheckIcon';
import CrossIcon from './Icons/CrossIcon';

function FileLine({
  filename,
  indentation,
  fullfilename,
  acceptedState,
  setAcceptedState,
}: {
  readonly filename: string;
  readonly indentation: number;
  readonly fullfilename: string;
  readonly acceptedState: any;
  readonly setAcceptedState: any;
}) {
  let iconComponent;
  if (!filename.includes('.')) {
    iconComponent = (
      <FolderIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
    );
  } else {
    const fileExt = filename.split('.').pop() as string;
    const setMusicExt = new Set(['mp3', 'wav', 'flac', 'ogg']);
    const setVideoExt = new Set(['mp4', 'mkv', 'avi', 'mov']);
    const setImageExt = new Set(['jpg', 'jpeg', 'png', 'gif']);

    if (setMusicExt.has(fileExt)) {
      iconComponent = (
        <MusicIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
      );
    } else if (setVideoExt.has(fileExt)) {
      iconComponent = (
        <VideoIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
      );
    } else if (setImageExt.has(fileExt)) {
      iconComponent = (
        <ImageIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
      );
    } else {
      iconComponent = (
        <FileIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
      );
    }
  }
  // weird paddingleft is a hack as pl is not working always
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'row',
      alignItems: 'center',
      marginLeft: `${indentation > 1 ? indentation * 20 : 0}px`,

    }}>
      {indentation > 0
        &&
        <div
          style={{
            marginLeft: '10px'
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-7 w-7 text-gray-200 dark:text-gray-200"
            fill="none"
            viewBox="0 0 15 15"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 3v7h7"
            />
          </svg>
        </div>
      }
      <div
        className={`${acceptedState[fullfilename] ? 'bg-green-100' : 'bg-white'} dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow border border-gray-200 dark:border-gray-700 mx-2`}
      >
        <div className="p-4 flex items-center gap-4">
          {iconComponent}
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
            {filename}
          </span>
          <div className="ml-auto flex items-center gap-2">
            <Button
              variant="ghost"
              onClick={() => {
                setAcceptedState((prevState: any) => {
                  const newState = { ...prevState };
                  Object.keys(newState).forEach((key) => {
                    if (key.startsWith(fullfilename)) {
                      newState[key] = true;
                    }
                  });
                  return newState;
                });
              }}
            >
              <CheckIcon className="h-5 w-5 text-green-500" />
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                setAcceptedState((prevState: any) => {
                  const newState = { ...prevState };
                  Object.keys(newState).forEach((key) => {
                    if (key.startsWith(fullfilename)) {
                      newState[key] = false;
                    }
                  });
                  return newState;
                });
              }}
            >
              <CrossIcon className="h-5 w-5 text-red-500" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
export default FileLine;
