# Frontend Routing
* **Objective**: SPA navigation.
* **Technology**: `react-router-dom` v7.
* **Internal Architecture**: Nested Ecosystems.
* **Protected Routes**: `<ProtectedRoute>` HOC checks `AuthContext.user`. Returns `<Navigate to="/login" />` if null.
* **Lazy Loading**: `React.lazy()` used for `CodingWorkspacePage` to defer Monaco Editor bundle.
