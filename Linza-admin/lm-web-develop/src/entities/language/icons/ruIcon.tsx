type IIconProps = {
  className?: string;
};

export const RuIcon = (props: IIconProps) => {
  return (
    <svg
      width="28"
      height="20"
      viewBox="0 0 28 20"
      className={props.className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g clipPath="url(#clip0_1843_93781)">
        <rect width="27.5" height="20" rx="2" fill="#1A47B8" />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M0 13.333H27.5V19.9997H0V13.333Z"
          fill="#F93939"
        />
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M0 0H27.5V6.66667H0V0Z"
          fill="white"
        />
      </g>
      <defs>
        <clipPath id="clip0_1843_93781">
          <rect width="27.5" height="20" rx="2" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
};
