import React, { useState } from 'react';

interface SerialEditorProps {
  serials: string[];
  onChange: (serials: string[]) => void;
}

export default function SerialEditor({ serials, onChange }: SerialEditorProps) {
  const [text, setText] = useState(serials.join('\n'));

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    const newSerials = e.target.value.split('\n').filter(s => s.trim());
    onChange(newSerials);
  };

  return (
    <div className="p-4">
      <h3 className="font-semibold mb-2">Serial Numbers ({serials.length})</h3>
      <textarea
        value={text}
        onChange={handleChange}
        className="w-full h-64 p-2 border rounded font-mono text-sm"
        placeholder="Enter serial numbers, one per line"
      />
    </div>
  );
}