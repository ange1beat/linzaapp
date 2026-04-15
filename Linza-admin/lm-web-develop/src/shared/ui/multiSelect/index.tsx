import { ChevronDown, Xmark } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import cn from "classnames";
import { components, MultiValue } from "react-select";
import AsyncSelect from "react-select/async";

import Loader from "../loader";
import Spin from "../spin";

import styles from "./MultiSelect.module.scss";

type IOption = {
  value: string;
  label: string;
};

function MultiSelect({
  className,
  placeholder,
  values,
  loadOptions,
  onChange,
  noOptionsMessage,
  isClearable,
  isLoading,
  isDisabled,
}: {
  className?: string;
  placeholder?: string;
  values: IOption[];
  loadOptions: (v: string) => Promise<IOption[]>;
  noOptionsMessage: string;
  isClearable?: boolean;
  isLoading?: boolean;
  isDisabled?: boolean;
  onChange: (values: MultiValue<IOption>) => void;
}) {
  const classes = cn(className, styles["multi-select"]);
  return (
    <AsyncSelect
      className={classes}
      classNames={{
        control: () => styles["multi-select__control"],
        placeholder: () => styles["multi-select__placeholder"],
        valueContainer: () => styles["multi-select__value-container"],
        multiValue: () =>
          cn(styles["multi-select__multi-value"], {
            [styles["multi-select__multi-value--disabled"]]: isDisabled,
          }),
        multiValueLabel: () => styles["multi-select__multi-value-label"],
        indicatorsContainer: () => styles["multi-select__indicators-container"],
        menu: () => styles["multi-select__menu"],
        option: () => styles["multi-select__option"],
        multiValueRemove: () => styles["multi-select__multi-value-remove"],
      }}
      value={values}
      components={{
        IndicatorSeparator: () => null,
        DropdownIndicator: () => (
          <div className={styles["multi-select__chevron"]}>
            <Icon data={ChevronDown} size={16} />
          </div>
        ),
        ClearIndicator: ({ innerProps }) => (
          <div {...innerProps} className={styles["multi-select__clear"]}>
            <Icon data={Xmark} size={16} />
          </div>
        ),
        LoadingIndicator: () => (
          <div className={styles["multi-select__loading"]}>
            <Spin size="xs" />
          </div>
        ),
        LoadingMessage: () => (
          <div className={styles["multi-select__loader"]}>
            <Loader size="s" />
          </div>
        ),
        MultiValueRemove: (props) => (
          <components.MultiValueRemove {...props}>
            <Icon data={Xmark} size={12} />
          </components.MultiValueRemove>
        ),
      }}
      placeholder={placeholder}
      isMulti={true}
      isDisabled={isDisabled}
      isClearable={isClearable}
      isLoading={isLoading}
      noOptionsMessage={() => noOptionsMessage}
      defaultOptions={true}
      loadOptions={loadOptions}
      onChange={onChange}
    />
  );
}

export default MultiSelect;
