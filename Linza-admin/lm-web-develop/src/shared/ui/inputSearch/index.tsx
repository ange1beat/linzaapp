import React from "react";

import { Magnifier } from "@gravity-ui/icons";
import { Icon, TextInput as GInputSearch } from "@gravity-ui/uikit";
import { useController, useForm } from "react-hook-form";

import { Button } from "@/shared/ui";

import styles from "./InputSearch.module.scss";

interface IInputPassword {
  className?: string;
  disabled?: boolean;
  errorMessage?: string;
  isError?: boolean;
  name?: string;
  placeholder?: string;
  size?: "xl" | "l" | "m" | "s";
  autoFocus?: boolean;
  onSearchChange: (search: string) => void;
}

function InputSearch({ size = "xl", ...props }: IInputPassword) {
  const iconSize = {
    xl: "20",
    l: "18",
    m: "16",
    s: "12",
  };

  const { handleSubmit, control } = useForm({
    defaultValues: {
      search: "",
    },
  });
  const { field: search } = useController({
    control: control,
    name: "search",
  });

  return (
    <form
      className={styles["input-search__form"]}
      onSubmit={handleSubmit((val) => props.onSearchChange(val.search))}
    >
      <GInputSearch
        {...props}
        validationState={props.isError ? "invalid" : undefined}
        className={props.className}
        value={search.value}
        onChange={search.onChange}
        size={size}
        ref={search.ref}
        rightContent={
          <Button
            view="normal"
            size="m"
            iconRight={
              <Icon
                data={Magnifier}
                size={iconSize[size]}
                className={styles["input-search__icon"]}
              />
            }
            className={styles["input-search__button"]}
            type="submit"
          />
        }
      />
    </form>
  );
}

export default InputSearch;
