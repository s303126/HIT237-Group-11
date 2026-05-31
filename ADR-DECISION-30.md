### ADR-030: Organise automated tests into dedicated modules with shared helpers

**Date:** 31/05/2026

**Author:** Aaron Madelo

**Status:** Accepted

**AI Usage:** ChatGPT was used to help structure the testing files and draft this ADR. The final decision was adapted to match the project’s Django app structure and Assessment 4 requirements.

**Context:**

Assessment 4 requires a meaningful test suite covering models, services, views, and permission boundaries. The application now includes authentication, role-based permissions, a service layer, exception handling, search, pagination, and the recording review workflow.

Keeping all automated tests in a single `tests.py` file would make the test suite harder to read and maintain. Many tests also require the same setup data, such as users, species, recordings, anomalies, and approved researchers. Repeating this setup in every test file would create duplicated code and increase the chance of inconsistent test data.

**Alternatives considered:**

- Option 1: Keep all tests in `tests.py`.
  - Pros: Simple default Django structure.
  - Cons: Becomes difficult to navigate as the suite grows.

- Option 2: Create separate test files but repeat setup data in each file.
  - Pros: Tests are grouped by topic.
  - Cons: Repeated setup code violates DRY and makes changes harder.

- Option 3: Use a `tests/` package with dedicated test modules and shared helper functions.
  - Pros: Organises tests by responsibility and reduces duplicated setup code.
  - Cons: Requires slightly more file structure.

**Decision:**

Use a dedicated `tests/` package inside `group11_app`, with test files organised by system responsibility:

- `helpers.py` for reusable test data creation
- `test_models.py` for model behaviour
- `test_services.py` for service-layer logic
- `test_permissions.py` for authentication and role boundaries
- `test_review_workflow.py` for recording approval workflow behaviour
- `test_anomalies.py` for anomaly flagging and resolution behaviour
- `test_validation.py` for validation and exception handling

This structure keeps the test suite easier to navigate and aligns the tests with the application architecture.

**Code reference:**

- `group11_app/tests/__init__.py`
- `group11_app/tests/helpers.py`
- `group11_app/tests/test_models.py`
- `group11_app/tests/test_services.py`
- `group11_app/tests/test_permissions.py`
- `group11_app/tests/test_review_workflow.py`
- `group11_app/tests/test_anomalies.py`
- `group11_app/tests/test_validation.py`

**Consequences:**

The test suite is more maintainable and easier to extend as the project grows. Shared helpers reduce repeated setup code and make test data more consistent.

The trade-off is that the project now contains more files, so contributors must understand where different categories of tests belong. This is acceptable because the clearer structure supports the larger Assessment 4 codebase.