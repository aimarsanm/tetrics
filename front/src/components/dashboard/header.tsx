'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { PlusCircle, Edit, ChevronLeft } from 'lucide-react';

interface HeaderProps {
  onAddMeasure?: () => void;
  onEditContext?: () => void;
  /** Optional handler to navigate back to goals listing */
  onBack?: () => void;
  /** Optional handler when clicking logo/title */
  onLogoClick?: () => void;
  /** Whether to show the Add Measure and Edit Context buttons */
  showActionButtons?: boolean;
}

// ...existing code...

export function Header({ onAddMeasure, onEditContext, onBack, onLogoClick, showActionButtons = true }: Readonly<HeaderProps>) {
  return (
    <header className="flex items-center justify-between p-4 border-b bg-card shadow-sm sticky top-0 z-10">
      <div className="flex items-center gap-3">
        {onBack && (
          <Button variant="ghost" onClick={onBack} className="mr-2">
            <ChevronLeft className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">Back to goals</span>
          </Button>
        )}
        <button
          onClick={onLogoClick}
          aria-label="Go to home"
          className="flex items-center gap-3 bg-transparent border-0 p-0"
        >
          <div className="flex items-center h-12 w-12">
            <img src="/Tetrics_logo.svg" alt="Tetrics Logo" className="object-contain h-full w-full" />
          </div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight font-headline">Tetrics</h1>
        </button>
      </div>
      {showActionButtons && onAddMeasure && onEditContext && (
        <div className="flex items-center gap-2">
          <Button onClick={onAddMeasure}>
            <PlusCircle className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">Add New Measure</span>
          </Button>
          <Button onClick={onEditContext} variant="outline">
            <Edit className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">Edit Context</span>
          </Button>
        </div>
      )}
    </header>
  );
}
