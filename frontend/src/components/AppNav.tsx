// frontend/src/components/AppNav.tsx
import React from 'react';

interface AppNavProps {
  title: string;
  onSettingsClick: () => void;
}

export default function AppNav({ title, onSettingsClick }: AppNavProps) {
  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold">{title}</h1>
        <button
          onClick={onSettingsClick}
          className="px-4 py-2 bg-blue-700 rounded hover:bg-blue-800 flex items-center gap-2"
        >
          <span className="text-xl">⚙️</span>
          <span>Settings</span>
        </button>
      </div>
    </nav>
  );
}