type IIconProps = {
  className?: string;
};

export const EnIcon = (props: IIconProps) => {
  return (
    <svg
      width="28"
      height="20"
      className={props.className}
      viewBox="0 0 28 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g clipPath="url(#clip0_1843_93771)">
        <rect width="27.5" height="20" rx="2" fill="#1A47B8" />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M2.92544 0H0V3.33333L24.5587 20L27.5 20V16.6667L2.92544 0Z"
          fill="white"
        />
        <path
          d="M0.975724 0L27.5 18.0472V20H26.5471L0 1.93408V0H0.975724Z"
          fill="#F93939"
        />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M24.881 0H27.5001V3.33333C27.5001 3.33333 10.4891 14.4374 2.61911 20H6.10352e-05V16.6667L24.881 0Z"
          fill="white"
        />
        <path
          d="M27.5 0H26.6118L0 18.0628V20H0.975724L27.5 1.94868V0Z"
          fill="#F93939"
        />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M10.0009 0H17.5219V6.16909H27.5V13.8268H17.5219V20H10.0009V13.8268H0V6.16909H10.0009V0Z"
          fill="white"
        />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M11.5789 0H15.9211V7.69231H27.5V12.3077H15.9211V20H11.5789V12.3077H0V7.69231H11.5789V0Z"
          fill="#F93939"
        />
      </g>
      <defs>
        <clipPath id="clip0_1843_93771">
          <rect width="27.5" height="20" rx="2" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
};
