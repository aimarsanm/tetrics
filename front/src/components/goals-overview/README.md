# Goals Overview Feature

## Overview

The Goals Overview page provides a high-level summary of all evaluation goals and their performance across different LLM tool configurations. This page serves as the main landing page for the Tetrics application.

## Features

### Main Table Layout

- **Rows**: Each row represents a Goal with:
  - Goal purpose (main title)
  - Focus area
  - Context information (if available)
  
- **Columns**: Each column represents an LLM Tool Configuration with:
  - Overall ranking (#1, #2, #3, etc.) based on average performance across all goals
  - Tool name
  - Model version

### Scoring System

#### Goal-Specific Scores
Each cell in the table shows:
1. **Goal-specific ranking** - Which LLM performs best for this particular goal
2. **Calculated score** - Weighted average of all criterion scores for this goal

The scores are calculated as follows:
```
Goal Score = Σ(Criterion Score × Criterion Weight) / Σ(Criterion Weight)
```

#### Overall Rankings (Column Headers)
The rankings in the column headers (#1, #2, etc.) represent the overall performance across ALL goals, calculated as:
```
Overall Rank = Average of all goal-specific scores for that LLM tool
```

### Visual Hierarchy

- **#1 ranked tools**: Displayed with primary badge variant (typically blue/accent color)
- **#2 ranked tools**: Displayed with secondary badge variant  
- **Other ranks**: Displayed with outline badge variant
- **N/A scores**: Displayed when no measurements are available for calculation

### Interactive Features

1. **Sorting**: Click any column header to sort goals by:
   - Goal name (alphabetically)
   - Performance for a specific LLM tool

2. **Navigation**: Click any goal row to navigate to the detailed view for that goal (when implemented)

## Data Flow

The Goals Overview page fetches and combines data from multiple sources:

1. **Evaluation Programs** - Context about the evaluation
2. **Goals** - List of all goals being evaluated
3. **Evaluation Criteria** - Criteria associated with each goal
4. **LLM Tool Configurations** - All LLM tools being compared
5. **Aggregated Scores** - Pre-calculated scores for each criterion+tool combination

## Component Structure

```
/components/goals-overview/
├── index.ts                    # Export file
├── goals-overview.tsx          # Main page component (data fetching, layout)
└── goals-overview-table.tsx    # Table component (scoring logic, rendering)
```

## Usage

### As Home Page
The Goals Overview is set as the default home page in `/app/page.tsx`:

```tsx
import { GoalsOverview } from '@/components/goals-overview/goals-overview';

export default function Home() {
  return <GoalsOverview />;
}
```

### With Navigation Callback
You can provide a custom callback when a goal is clicked:

```tsx
<GoalsOverview onGoalSelect={(goalId) => {
  router.push(`/goals/${goalId}`);
}} />
```

## Future Enhancements

1. **Goal Detail Navigation** - Implement routing to individual goal detail pages
2. **Filtering** - Add filters for goal categories, time periods, etc.
3. **Export** - Allow exporting the comparison table as CSV/PDF
4. **Visualization** - Add charts/graphs for visual comparison
5. **Multi-Goal Selection** - Allow selecting multiple goals for side-by-side comparison
6. **Historical Trends** - Show how scores change over time

## Related Components

- `/components/dashboard/dashboard.tsx` - Detailed single-goal view
- `/components/dashboard/eval-table-enhanced.tsx` - Detailed criterion and metric table

## Backend Dependencies

The Goals Overview relies on the following backend endpoints:

- `GET /api/v1/domain/evaluation-programs/` - Evaluation program context
- `GET /api/v1/domain/goals/` - All goals
- `GET /api/v1/domain/evaluation-criteria/` - All criteria with their goal associations
- `GET /api/v1/domain/llm-tool-configurations/` - All LLM tools
- `GET /api/v1/domain/aggregated-scores/` - Pre-calculated criterion scores

## Notes

- The backend should ensure that `aggregated_scores` are properly calculated before displaying on this page
- Scores are weighted by criterion weights to provide fair comparisons
- The page gracefully handles missing data with "N/A" indicators
