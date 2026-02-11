# Family Settings Header Specification

## Overview
The Family Settings page currently lacks a proper page header consistent with other pages (e.g., Dashboard, Growth Record). This specification defines the requirement to add a header and commonize the header component for future use.

## Requirements

### 1. Common Header Component
- Create a reusable UI component for page headers.
- **Location**: `app/templates/components/page_header.html` (or macro)
- **Features**:
    - **Title**: Main page title (e.g., "Family Settings").
    - **Subtitle**: Optional descriptive text (e.g., Family Name).
    - **Actions**: Optional slot for action buttons (e.g., "Add New", "Edit").
    - **Back Link**: Optional link to go back (if needed, though not explicitly requested, good for future).
- **Styling**:
    - Consistent with `dashboard.html`:
        - Wrapper: `flex flex-col md:flex-row ... justify-between ... gap-4`
        - Title: `text-2xl md:text-3xl font-bold`
        - Subtitle: `text-gray-600 dark:text-gray-400`

### 2. Family Settings Page Update
- **Target**: `app/templates/family/settings.html`
- **Changes**:
    - Remove the current header inside the card (`<h2>家族設定: {{ family.name }}</h2>`).
    - Implement the new Common Header Component at the top of the page (outside the card).
    - Title: "家族設定"
    - Subtitle: `{{ family.name }}`
    - Content wrapper width should be consistent (e.g., `max-w-4xl` or keep `max-w-2xl` if content is small, but header usually spans or aligns).

## Technical Implementation
- Use Jinja2 `macro` for the component to allow passing arguments easily.
- Define in `app/templates/components/page_header.html`.
