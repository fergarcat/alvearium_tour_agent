import { useState, useLayoutEffect } from 'react';

function useAutosize(ref, value) {
  const [borderWidth, setBorderWidth] = useState(0);

  useLayoutEffect(() => {
    if (ref.current) {
      const style = window.getComputedStyle(ref.current);
      setBorderWidth(parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth));
    }
  }, [ref]);

  useLayoutEffect(() => {
    if (ref.current) {
      ref.current.style.height = 'inherit';
      ref.current.style.height = `${ref.current.scrollHeight + borderWidth}px`;
    }
  }, [ref, value, borderWidth]);
}

export default useAutosize;
