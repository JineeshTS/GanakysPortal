"use client";

import { create } from "zustand";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  title: string;
  description?: string;
  type: ToastType;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (toast) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast = { ...toast, id };

    set((state) => ({
      toasts: [...state.toasts, newToast],
    }));

    // Auto-remove after duration (default 5 seconds)
    const duration = toast.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        }));
      }, duration);
    }
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
  clearToasts: () => set({ toasts: [] }),
}));

// Hook for convenience
export function useToast() {
  const { addToast, removeToast, clearToasts, toasts } = useToastStore();

  return {
    toasts,
    toast: (props: Omit<Toast, "id">) => addToast(props),
    dismiss: removeToast,
    clearAll: clearToasts,
  };
}

// Shorthand functions
export function toast(props: Omit<Toast, "id">) {
  useToastStore.getState().addToast(props);
}

export function toastSuccess(title: string, description?: string) {
  toast({ title, description, type: "success" });
}

export function toastError(title: string, description?: string) {
  toast({ title, description, type: "error" });
}

export function toastWarning(title: string, description?: string) {
  toast({ title, description, type: "warning" });
}

export function toastInfo(title: string, description?: string) {
  toast({ title, description, type: "info" });
}
