import React from 'react';

interface QuickActionsProps {
  onActionClick: (text: string) => void;
}

export default function QuickActions({ onActionClick }: QuickActionsProps) {
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      <button 
        onClick={() => onActionClick("My status")}
        className="bg-bgCard hover:bg-bgCard/80 border border-borderC text-textMain px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
      >
        📊 My Status
      </button>
      <button 
        onClick={() => onActionClick("I have 60 minutes")}
        className="bg-bgCard hover:bg-bgCard/80 border border-borderC text-textMain px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
      >
        🎯 60 Min Plan
      </button>
      <button 
        onClick={() => onActionClick("How ready am I for Celebal?")}
        className="bg-bgCard hover:bg-bgCard/80 border border-borderC text-textMain px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
      >
        🏢 Celebal Check
      </button>
      <button 
        onClick={() => onActionClick("Give me a SQL quiz")}
        className="bg-bgCard hover:bg-bgCard/80 border border-borderC text-textMain px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
      >
        📝 SQL Quiz
      </button>
    </div>
  );
}
