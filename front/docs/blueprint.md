# **App Name**: LLM Eval Insights

## Core Features:

- Data Table Display: Display the evaluation data in a structured table format with fixed columns for 'Metric Type' and 'Metric Name'.
- Dynamic Model Columns: Enable adding new columns for different LLM models dynamically.
- Add Evaluation Program: Button for admin to create a new Evaluation program to allow later goal association
- Add Goals: Admin to populate a new evaluation with one or many goals as the starting point
- Configure tool usage for each Metric: Allows the administrator to attach llm-tool-configurations objects, to determine with wich tools and setups, we have meassurements.
- Add Raw Metrics to Configuration Tool: Provide a way for the admins to define and collect different types of metrics with its configurations. Each Tool + Setup produces one Meassurement.

## Style Guidelines:

- Primary color: Deep purple (#6750A4) for a sophisticated and intellectual feel.
- Background color: Light grey (#F2F0F4) to provide a clean and neutral backdrop.
- Accent color: Soft lavender (#D0BCFF) to highlight key elements and actions.
- Body and headline font: 'Inter' for a modern and neutral appearance. This is appropriate because of the large blocks of text in the source document, but also its precise scientific topic.
- Use simple, consistent icons to represent different metric types and actions.
- Ensure the table is responsive and adapts to different screen sizes.
- Subtle transitions for adding new columns or rows.