# Fitness.AI Web Application

**Description**: Fitness.AI is a web application designed with Flask in Python, serving as the backend. The application offers several features, including user registration, login, profile management, meal generation, and account updates.

## Registration and Login

### Registration
- **Page**: `register.html`
- **Inputs**: Username, Password, Confirm Password
- **Backend**: `app.py`
  - Checks if passwords match.
  - Ensures the username is unique.

### Login
- **Page**: `login.html`
- **Inputs**: Username, Password
- **Backend**: `app.py`
  - Verifies username existence.
  - Checks password validity using `check_password_hash`.
  - Redirects authenticated users to the home page (`/`).
  - Login route is controlled by `login_required` in `helpers.py`.

## Logout

- **Functionality**:
  - Clears the session using `session.clear()`.

## Home Route (`/`)

- **Behavior**:
  - Checks if user profile (height) is complete.
  - Redirects to `new.html` for profile completion if needed.
  - Displays statistics on the home page once the profile is complete.

## Profile Completion

- **Page**: `new.html`
- **Redirection**: To home page after completion.

## Helpers

- **File**: `helpers.py`
- **Functions**:
  - `BMI`: Calculates Body Mass Index using height and weight.
  - `weight_class`: Determines weight class.
  - `BMR`: Calculates daily caloric needs based on activity level from `index.html`.

## Meal Generator

- **Page**: `meal.html`
- **Functionality**:
  - Form for meal options.
  - Sends request to OpenAI API for meal generation.
  - Displays results on `result.html`.
  - Options to save or regenerate meal:
    - **Save**: Adds meal to the "meals" table in the database.
    - **Regenerate**: Redirects to `meal.html`.

## Saved Meals

- **Page**: `saved.html`
- **Display**:
  - Shows all saved meals using a loop.
  - Meals displayed in card containers.
  - Hovering reveals meal details.
  - Remove option to delete meals from the database via `/saved` route.

## Account Management

- **Page**: `account.html`
- **Forms**:
  - **Change Password**: Executed if "old_password" is present in the form.
  - **Update Information**: Updates height, weight, and age.
  - Changes are reflected using `UPDATE SET` in SQLite.

## Styling

- **CSS File**: `style.css`
- **Inclusion**: Included in `layout.html` for consistent styling across pages.
