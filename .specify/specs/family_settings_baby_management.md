# Family Settings: Baby Management Specification

## Overview
Allow family administrators to manage registered babies within the Family Settings page. Specifically, enabling the deletion of a baby profile that was registered by mistake.

## Requirements

### 1. Baby List Section in Family Settings
- **Location**: `app/templates/family/settings.html`
- **Placement**: Below the "Family Invite Code" section and above or below "Member List".
- **Content**:
    - Section Title: "登録済みの赤ちゃん" (Registered Babies)
    - List of babies belonging to the family.
    - Information per baby: Name, Birthday (or Due Date).
    - **Actions**: "削除" (Delete) button for each baby.

### 2. Deletion Permission & Safety
- **Permission**: Only users with the `admin` role in the family can delete a baby.
- **Confirmation**: A confirmation dialog (browser native `confirm()` is sufficient for now) must appear before deletion to prevent accidental clicks.
    - Message: "本当に「{baby_name}」を削除しますか？関連するすべての記録も削除されます。この操作は取り消せません。"

### 3. Backend Implementation
- **Endpoint**: `DELETE /babies/{baby_id}`
- **Router**: `app/routers/baby.py`
- **Logic**:
    - Verify user is an admin of the family the baby belongs to.
    - Delete the `Baby` record.
    - Rely on SQLAlchemy `cascade="all, delete-orphan"` to clean up related records (Feedings, Sleeps, etc.), which is already configured in `app/models/baby.py`.
- **Response**:
    - On success: Redirect to `/families/settings` with a success message (or just reload).
    - Note: Since HTML forms don't support DELETE method natively, use a Form with `POST` method simulating DELETE (e.g., via hidden field or specific endpoint like `/babies/{id}/delete` for simplicity if not using AJAX), OR use JavaScript `fetch` with `DELETE` method.
    - **Decision**: For simplicity and consistency with current app (likely SSR), use a `POST` endpoint `/babies/{baby_id}/delete` or use a standard form. Let's use a `POST` form to `/babies/{baby_id}/delete` to keep it simple without complex JS.

## UI Design
- Use a simple list or table similar to the Member List.
- Delete button should be red (danger style).

## Plan
1.  Add `POST /babies/{baby_id}/delete` to `app/routers/baby.py`.
2.  Update `app/templates/family/settings.html` to display the baby list and delete forms.
