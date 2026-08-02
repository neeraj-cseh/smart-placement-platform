# Component: ThemeContext
* **Objective**: Handle Light/Dark modes.
* **State Management**: `useState` boolean wrapped in `Context.Provider`.
* **Implementation**: Toggles `data-theme="dark"` attribute on `<html>` tag.
* **Styling Dependency**: Vanilla CSS Custom Variables in `index.css`.
