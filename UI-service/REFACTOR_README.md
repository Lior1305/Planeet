# ✨ Planeet UI Refactor: Page-per-Tab + Standalone Planning Modal

## Overview

The Planeet UI has been refactored from a single tabbed dashboard to a page-per-tab architecture with reusable components. This improves code organization, maintainability, and user experience.

## New Structure

```
/ (project root)
├─ index.html                         # redirect to welcome (unchanged)
├─ welcome.html                       # login/register page (unchanged)
├─ plan.html                          # NEW: Plan page (was Plan tab)
├─ profile.html                       # NEW: Profile page (was Profile tab)
├─ history.html                       # NEW: Previous Outings page (was History tab)
├─ dashboard-hub.html                 # NEW: Lightweight hub page (optional)
├─ components/
│  ├─ header.html                     # NEW: shared top header (logo, user, nav)
│  ├─ planning-modal.html             # NEW: standalone multi-step modal
│  └─ settings-modal.html             # NEW: shared settings modal
├─ js/
│  ├─ welcome.js                      # keep login/register logic (unchanged)
│  ├─ plan.js                         # NEW: page controller for Plan page
│  ├─ profile.js                      # NEW: page controller for Profile page
│  ├─ history.js                      # NEW: page controller for History page
│  ├─ common.js                       # NEW: utilities (user load/save, nav, fetch helpers)
│  └─ dashboard.js                    # OLD: can be removed if not needed
└─ styles.css                         # enhanced with new component styles
```

## Key Changes

### 1. **Page-per-Tab Architecture**
- **Plan page** (`plan.html`): Hosts the planning interface and lazy-loads the planning modal
- **Profile page** (`profile.html`): Shows user profile with working settings
- **History page** (`history.html`): Displays previous outings with empty state CTA
- **Dashboard Hub** (`dashboard-hub.html`): Optional lightweight landing page

### 2. **Component-Based Architecture**
- **Header component** (`components/header.html`): Shared navigation and user info
- **Planning modal** (`components/planning-modal.html`): Multi-step wizard (lazy-loaded)
- **Settings modal** (`components/settings-modal.html`): User settings (lazy-loaded)

### 3. **JavaScript Controllers**
- **`common.js`**: Shared utilities, user management, component loading
- **`plan.js`**: Planning flow logic, multi-step validation, form submission
- **`profile.js`**: Profile display and settings management
- **`history.js`**: Outings history display (ready for backend integration)

## Backend Contract (Unchanged)

### Users Service
- **Endpoint**: `http://localhost:8080/users`
- **Login/Registration**: Same validation and error handling
- **User Storage**: `localStorage.planeetUser` (unchanged)

### Planning Service
- **Endpoint**: `http://localhost:8001/v1/plans/create`
- **Request Schema**: Identical to current implementation
- **Payload**: `user_id`, `plan_id`, `venue_types`, `location`, `radius_km`, `max_venues`, `date`, `duration_hours`, `group_size`, `budget_range`, `min_rating`, `amenities`, `dietary_restrictions`, `accessibility_needs`

## How It Works

### 1. **Authentication Flow**
1. User logs in via `welcome.html`
2. Success redirects to `plan.html` (instead of `dashboard.html`)
3. `plan.html` loads user data and components
4. If no user data, redirects to `welcome.html`

### 2. **Component Loading**
- Each page loads `common.js` first
- Header and settings modal are fetched and injected via `fetch()`
- Planning modal is only loaded on the Plan page
- Components are mounted into designated `<div>` elements

### 3. **Navigation**
- Header contains real links to each page
- Active page is highlighted based on `window.location.pathname`
- No JavaScript tab switching - each "tab" is its own page

### 4. **Planning Flow**
- **Plan page** shows planning card with "Start Planning" button
- Button opens the **standalone multi-step modal**
- Modal uses same validation logic as before
- Form submission posts to same endpoint with same schema
- Success shows plan ID and refreshes page

## Usage

### For Users
1. **Login/Register** at `welcome.html`
2. **Plan outings** at `plan.html` (default landing page)
3. **View profile** at `profile.html`
4. **Check history** at `history.html`
5. **Navigate** using header links

### For Developers
1. **Add new pages**: Create HTML + JS controller + mount points
2. **Modify components**: Edit files in `components/` directory
3. **Update styles**: Modify `styles.css` (new styles added for components)
4. **Backend integration**: Use `commonUtils.apiFetch()` helper

## Benefits

✅ **Better Code Organization**: Each page has its own controller and responsibilities  
✅ **Reusable Components**: Header, modals, and utilities shared across pages  
✅ **Easier Maintenance**: Clear separation of concerns  
✅ **Better UX**: Real page navigation instead of JavaScript tabs  
✅ **Scalable**: Easy to add new pages and features  
✅ **Backend Compatible**: All existing API contracts preserved  

## Migration Notes

- **Login redirects** now go to `plan.html` instead of `dashboard.html`
- **Tab switching logic** removed from `dashboard.js`
- **Planning modal** extracted to standalone component
- **Settings modal** extracted to standalone component
- **User authentication** flow unchanged
- **API endpoints** and request schemas unchanged

## Testing

1. **Login flow**: Should redirect to `plan.html`
2. **Navigation**: Header links should work between pages
3. **Planning**: Multi-step modal should work on Plan page only
4. **Settings**: Should work on all pages
5. **Authentication**: Should redirect to login if no user data

## Future Enhancements

- **Backend integration** for outings history
- **User preferences** persistence
- **Advanced filtering** and search
- **Mobile responsiveness** improvements
- **Accessibility** enhancements
