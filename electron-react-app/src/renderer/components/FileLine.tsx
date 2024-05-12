import FileIcon from './Icons/FileIcon';
import FolderIcon from './Icons/FolderIcon';
import MusicIcon from './Icons/MusicIcon';
import VideoIcon from './Icons/VideoIcon';
import ImageIcon from './Icons/ImageIcon';

function FileLine({
  filename,
  indentation,
}: {
  readonly filename: string;
  readonly indentation: number;
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
    <div
      className="bg-white dark:bg-gray-950 rounded-md shadow-sm hover:shadow-md transition-shadow"
      style={{ paddingLeft: `${indentation * 20}px` }}
    >
      <div className="p-4 flex items-center gap-4">
        {iconComponent}
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
          {filename}
        </span>
      </div>
    </div>
  );
}
export default FileLine;
