# WeatherApp Improvement Tasks

Below is an ordered, actionable checklist of improvements. Each item begins with a checkbox placeholder and is written to be directly actionable. The sequence starts with correctness and consistency, then architecture, quality, security, performance, UX, and finally DevOps and documentation.

1. [ ] Audit and resolve inconsistencies between URLs, views, forms, and templates
   - [ ] Align weatherarchive/urls.py to point to existing views (e.g., use views.daily_data instead of non-existent location_search).
   - [ ] Ensure templates referenced by views exist and match context keys (results.html currently expects city/postcode/coords, while views.daily_data uses display_name, arrays, etc.).
   - [ ] Decide on the primary flow: simple location search vs. daily history with charts. Remove unused/stub pathways or complete them.

2. [ ] Implement WeatherDailyForm with proper fields and validation
   - [ ] Define location (CharField), start_date, end_date (DateFields) with validation for ranges and max span.
   - [ ] Validate that start_date <= end_date and not in the future, with helpful error messages.
   - [ ] Add clean methods and user-friendly labels/help_text.

3. [ ] Remove or complete LocationForm flow
   - [ ] If keeping LocationForm (city/postcode/manual), implement corresponding view logic and templates to use it.
   - [ ] If not needed, remove LocationForm and related templates to avoid confusion.

4. [ ] Create a cohesive results template for daily data
   - [ ] Build results.html to render:
     - [ ] Form for new queries with preserved values.
     - [ ] Summary of geocoded display_name and coordinates.
     - [ ] Chart-ready arrays (e.g., Plotly) or basic tables when JS is unavailable.
     - [ ] Download CSV link wired to download_daily_csv with current querystring.
   - [ ] Handle and display error messages (e.g., location not found).

5. [ ] Add a dedicated template for the search form/home page
   - [ ] Provide a page hosting WeatherDailyForm (GET method), linking to results display or combined page.
   - [ ] Ensure CSRF usage is correct (for POST if used) and consistent styling.

6. [ ] Harden external API interactions (Open-Meteo)
   - [ ] Add retries with backoff and reasonable timeouts for _geocode and _fetch_daily.
   - [ ] Validate API responses defensively; log anomalies.
   - [ ] Consider server-side caching of geocoding results to reduce repeated lookups.

7. [ ] Introduce proper logging
   - [ ] Configure Django logging in settings.py with handlers/formatters.
   - [ ] Log key events: input parameters, API requests outcomes, errors, and performance metrics.

8. [ ] Add typing and docstrings across the codebase
   - [ ] Type annotate views, helpers (_geocode, _fetch_daily), and forms.
   - [ ] Add concise docstrings describing responsibilities and parameters.

9. [ ] Separate concerns and improve module structure
   - [ ] Move API client logic to a services module (e.g., weatherarchive/services/open_meteo.py).
   - [ ] Keep views thin by delegating to forms/services and serializers/adapters.
   - [ ] Centralize constants (e.g., daily parameter lists) in a config module.

10. [ ] Improve error handling and user feedback
    - [ ] Standardize error messages for common failure modes (validation, API errors, not found).
    - [ ] Show actionable guidance in UI when errors occur.

11. [ ] Security and configuration hygiene
    - [ ] Move SECRET_KEY and environment-specific settings to environment variables (e.g., using python-dotenv or Django-environ) and out of source control.
    - [ ] Set DEBUG based on environment and configure ALLOWED_HOSTS for deployments.
    - [ ] Add security middlewares/settings for production (SECURE_*, CSRF_TRUSTED_ORIGINS, etc.).

12. [ ] Static assets and front-end hygiene
    - [ ] Configure static files (STATIC_ROOT, STATICFILES_DIRS) for collectstatic in production.
    - [ ] Add basic styling/CSS and responsive layout for forms and tables.

13. [ ] Accessibility and i18n
    - [ ] Add accessible labels, ARIA attributes, and form field help texts.
    - [ ] Mark templates for translation and set up Django i18n basics.

14. [ ] Tests: unit and integration
    - [ ] Add tests for WeatherDailyForm validation (date bounds, required fields, invalid inputs).
    - [ ] Add tests for _geocode and _fetch_daily with mocked requests.
    - [ ] Add view tests for daily_data and download_daily_csv happy paths and error cases.

15. [ ] Continuous Integration setup
    - [ ] Add a basic CI workflow (GitHub Actions) to run flake8/ruff, mypy (optional), and Django tests.
    - [ ] Include coverage reporting gate.

16. [ ] Linting and formatting
    - [ ] Configure ruff or flake8 with sensible rules; add isort and/or black for formatting.
    - [ ] Add pre-commit hooks to enforce style and prevent committing secrets.

17. [ ] Performance and caching
    - [ ] Cache geocoding results (e.g., in-memory or Django cache backend) for recent queries.
    - [ ] Consider HTTP caching headers for CSV downloads.

18. [ ] Data modeling (optional, future)
    - [ ] If persistence is desired, add a model to store query history and cached daily data with TTL.
    - [ ] Admin integration for viewing query logs and caches.

19. [ ] Robust CSV generation
    - [ ] Ensure CSV writer handles missing values and proper locale/encoding (utf-8-sig if needed).
    - [ ] Escape/normalize display_name for safe filenames across OSes.

20. [ ] Input validation and sanitization
    - [ ] Sanitize the location input to avoid issues with external requests and file names.
    - [ ] Add length limits and regex where applicable.

21. [ ] Improve URL routing and namespacing
    - [ ] Namespace app URLs (app_name = 'weatherarchive') and use named URLs for reverses.
    - [ ] Provide distinct routes: '/' for form, '/results' for showing results (or combined), '/download' for CSV.

22. [ ] Error pages and empty states
    - [ ] Create user-friendly 404/500 templates and handle empty result sets gracefully in results page.

23. [ ] Documentation for users and developers
    - [ ] Add a README with setup, running, and testing instructions.
    - [ ] Document environment variables and how to obtain API access if needed (Open-Meteo is public, but note usage limits).

24. [ ] Optional: Containerization and local dev tooling
    - [ ] Add a dev Dockerfile and docker-compose for easy local setup.
    - [ ] Provide Makefile or invoke/nox tasks for common commands.

25. [ ] Secrets and environment management
    - [ ] Add a .env.example file and load env vars in settings.py securely.
    - [ ] Ensure .env is in .gitignore.

26. [ ] Pagination or range limits for large queries
    - [ ] Enforce a maximum date range in the form to prevent heavy API calls.
    - [ ] Provide UI feedback when truncation/limits apply.

27. [ ] Timezone handling
    - [ ] Confirm timezone usage ('auto' from API) aligns with UI expectations; expose selected timezone in UI if needed.

28. [ ] Resilience and rate limiting
    - [ ] Implement simple in-process rate limiting per IP/session for requests triggering external API calls.
    - [ ] Backoff on repeated failures and provide user feedback.

29. [ ] Monitoring and metrics (future)
    - [ ] Add basic request/response metrics and error rates (e.g., Prometheus/Django integration) for production.

30. [ ] Clean up placeholder and dead code
    - [ ] Remove commented/placeholder lines (e.g., stray docstring in urls.py, incomplete WeatherDailyForm stub) once replaced.
