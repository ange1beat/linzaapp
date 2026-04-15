import React from "react";

import { Select as GSelect } from "@gravity-ui/uikit";

interface ISelect<T extends { value: string; label: string }> {
  className?: string;
  disabled?: boolean;
  placeholder?: string;
  value: string;
  options: T[];
  size: "m" | "s" | "l" | "xl";
  renderOption?: (option: T) => React.ReactNode;
  onChange: (option: T) => void;
}

function Select<T extends { value: string; label: string }>({
  className,
  disabled,
  placeholder,
  value,
  options,
  renderOption,
  size,
  onChange,
}: ISelect<T>) {
  const onUpdate = (values: string[]) => {
    const result = options.find((data) => data.value === values[0]);
    result && onChange(result);
  };

  return (
    <GSelect
      className={className}
      size={size}
      disabled={disabled}
      placeholder={placeholder}
      value={[value]}
      onUpdate={onUpdate}
    >
      {options.map((option) => {
        return (
          <GSelect.Option value={option.value} key={option.label}>
            {renderOption ? renderOption(option) : option.label}
          </GSelect.Option>
        );
      })}
    </GSelect>
  );
}

Select.defaultProps = {
  size: "l",
};

export default Select;
