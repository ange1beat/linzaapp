import React, { SetStateAction, useEffect, useState } from "react";

export function useDebounce<T>(
  initialVal: T,
  delay = 500,
): [T, React.Dispatch<SetStateAction<T>>, T] {
  const [value, setValue] = useState<T>(initialVal);
  const [debouncedValue, setDebouncedValue] = useState<T>(initialVal);

  useEffect(() => {
    const debounce = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(debounce);
  }, [value, delay]);
  return [value, setValue, debouncedValue];
}
