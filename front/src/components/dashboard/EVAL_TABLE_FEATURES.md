# Enhanced Evaluation Table Features

## Overview

The evaluation table has been enhanced with @tanstack/react-table to provide powerful personalization features while maintaining the original design aesthetic.

## New Features

### 1. **Column Visibility Control**
- Click the "Customize" button (gear icon) in the top-right corner of the table
- A dropdown menu allows you to show/hide individual LLM tool columns
- The first two columns (Criterion/Metric and Details) are always visible and cannot be hidden
- Column visibility preferences persist during your session

### 2. **Column Reordering (Drag & Drop)**
- Hover over any LLM tool column header to see the grip icon (⋮⋮)
- Click and drag the column header to reorder columns
- The first two columns (Criterion/Metric and Details) are fixed and cannot be moved
- Reorder columns to compare specific models side-by-side

### 3. **Row Reordering (Drag & Drop)**
- Drag and drop criteria rows to reorder evaluation criteria
- Drag and drop metric rows to reorder metrics within each criterion
- Each criterion row shows a grip icon (⋮⋮) for easy dragging
- Each metric row shows a grip icon (⋮⋮) for reordering within its criterion (indented)
- Metrics can only be reordered within their parent criterion (cannot move between criteria)
- Visual feedback shows where the row will be dropped:
  - Blue border at top of row: will insert before this row
  - Blue border at bottom of row: will insert after this row
  - Blue highlighted zone at bottom: drop zone for moving criteria to the very end
- Drag to the top half of a row to insert before it
- Drag to the bottom half of a row to insert after it
- Special drop zone appears at the bottom of the table when dragging criteria, allowing you to easily move items to the end

### 3. **Preserved Original Features**
- All original functionality remains intact:
  - Expandable/collapsible criteria rows
  - Inline editing of measurements
  - Edit buttons for LLM tool configurations
  - Aggregated scores and overall scores
  - Badge styling and visual design
  - Hover effects and interactive elements

## Usage

The enhanced table is a drop-in replacement for the original table:

```tsx
import { EvalTableEnhanced } from './eval-table-enhanced';

<EvalTableEnhanced 
  criteria={criteria} 
  llmTools={filteredLlmTools}
  scores={scores}
  measurements={measurements}
  onScoreUpdate={handleScoreUpdate}
  onAddMeasurement={handleOpenMeasurementDialog}
  onEditLlmTool={handleEditLlmTool}
/>
```

## Technical Implementation

- Built with `@tanstack/react-table` v8
- Uses React hooks for state management
- Maintains TypeScript type safety
- Preserves all shadcn/ui components styling
- Responsive design maintained

## Future Enhancement Ideas

- Save column preferences to localStorage or user profile
- Add sorting capabilities
- Add filtering options
- Export table data to CSV/Excel
- Column resizing
- Grouping by criterion type
