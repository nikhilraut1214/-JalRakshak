import { useEffect, useRef } from 'react';

interface UseFocusTrapOptions {
  isOpen: boolean;
  onClose: () => void;
  initialFocusRef?: React.RefObject<HTMLElement | null>;
  triggerRef?: React.RefObject<HTMLElement | null>;
}

export function useFocusTrap<T extends HTMLElement = HTMLElement>({
  isOpen,
  onClose,
  initialFocusRef,
  triggerRef,
}: UseFocusTrapOptions) {
  const containerRef = useRef<T | null>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    // Capture currently focused element (or provided trigger) to restore upon close
    previousActiveElement.current = (triggerRef?.current || document.activeElement) as HTMLElement | null;

    const container = containerRef.current;
    if (!container) return;

    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ].join(', ');

    // Set initial focus to initialFocusRef, first focusable child, or container
    const focusableElements = container.querySelectorAll<HTMLElement>(focusableSelectors);
    const timer = setTimeout(() => {
      if (initialFocusRef?.current) {
        initialFocusRef.current.focus();
      } else if (focusableElements.length > 0) {
        focusableElements[0].focus();
      } else {
        container.focus();
      }
    }, 0);

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.stopPropagation();
        onClose();
        return;
      }

      if (e.key === 'Tab') {
        const elements = container.querySelectorAll<HTMLElement>(focusableSelectors);
        if (elements.length === 0) {
          e.preventDefault();
          return;
        }

        const firstElement = elements[0];
        const lastElement = elements[elements.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement || !container.contains(document.activeElement)) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement || !container.contains(document.activeElement)) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('keydown', handleKeyDown);
      if (previousActiveElement.current && typeof previousActiveElement.current.focus === 'function') {
        previousActiveElement.current.focus();
      }
    };
  }, [isOpen, onClose, initialFocusRef, triggerRef]);

  return containerRef;
}
