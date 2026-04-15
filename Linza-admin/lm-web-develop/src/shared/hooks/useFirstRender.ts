import { useEffect, useRef } from "react";

export function useFirstRender(callback: () => void) {
  const isFirst = useRef(true);

  useEffect(() => {
    if (isFirst.current) {
      callback();
    }
    isFirst.current = false;
  }, []);
}
