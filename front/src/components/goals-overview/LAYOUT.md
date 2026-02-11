# Goals Overview Page Layout

## Table Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Goals Overview                                      │
│  Compare overall performance of LLM tools across all evaluation goals      │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────┤
│                 │     #1          │     #2          │     #3              │
│     Goal        │  GPT-4 Turbo    │  Claude 3       │  Gemini Pro         │
│                 │  gpt-4-turbo    │  claude-3-opus  │  gemini-1.0-pro     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ Code Quality    │      #1         │      #2         │      #3             │
│ Focus: Clean... │     85.2        │     82.1        │     78.5            │
│                 │                 │                 │                     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ Documentation   │      #2         │      #1         │      #3             │
│ Focus: Clear... │     78.3        │     88.7        │     75.2            │
│                 │                 │                 │                     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ Performance     │      #1         │      #3         │      #2             │
│ Focus: Speed... │     92.1        │     80.4        │     85.6            │
│                 │                 │                 │                     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

## Legend

### Column Headers
- **#1, #2, #3**: Overall ranking across ALL goals
- **Tool Name**: LLM tool name (e.g., GPT-4 Turbo)
- **Model Version**: Specific version identifier

### Row Content
- **Goal Title**: Main purpose of the goal
- **Focus**: What the goal focuses on (truncated)
- **Context**: Additional context (if available)

### Cell Content (per goal-tool combination)
- **Top badge (#1, #2, #3)**: Goal-specific ranking
  - Which tool performs best for THIS specific goal
- **Bottom number**: Calculated score
  - Weighted average of all criterion scores for this goal
- **"N/A"**: No measurements available

## Color Coding

```
┌──────────────────────────────────────────────┐
│  Rank #1: Primary Badge (Blue/Accent)       │
│  Rank #2: Secondary Badge (Gray)            │
│  Others:  Outline Badge (Border only)       │
│  N/A:     Neutral Outline (Muted)           │
└──────────────────────────────────────────────┘
```

## Interactive Features

1. **Sortable Columns**
   - Click column header to sort by that tool's performance
   - Click "Goal" to sort alphabetically

2. **Clickable Rows**
   - Click any goal row to view detailed metrics (when implemented)

3. **Sticky Column**
   - First column (Goals) stays visible when scrolling horizontally

## Example: Interpreting the Table

Looking at the "Documentation" goal:
- **GPT-4 Turbo**: Rank #2 for this goal (78.3 score)
- **Claude 3**: Rank #1 for this goal (88.7 score) - BEST for documentation
- **Gemini Pro**: Rank #3 for this goal (75.2 score)

Even though GPT-4 Turbo has the best OVERALL rank (#1 in column header),
Claude 3 performs better specifically for Documentation goals.

This allows users to:
- Choose the best tool overall (look at column header ranks)
- Choose the best tool for specific purposes (look at cell ranks)
