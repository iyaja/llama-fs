import { Button } from '@nextui-org/button';
import TelescopeIcon from './Icons/TelescopeIcon';
import './Telescope.css';

function TelescopeButton(props: any) {
  return (
    <div className="relative">
      <TelescopeIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
      {props.isLoading && (
        <svg
          className="h-8 w-8 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
          viewBox="0 0 24 24"
        >
          <rect
            className="progress stroke-current text-gray-600 dark:text-gray-400"
            x="2"
            y="2"
            width="20"
            height="20"
            rx="5"
            fill="none"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      )}
    </div>
  );
}
export default TelescopeButton;
