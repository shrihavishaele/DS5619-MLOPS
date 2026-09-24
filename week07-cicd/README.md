# Week 7: CI/CD Integration Testing

In this lab, we built an automated pipeline using GitHub Actions to test our code every time it is updated. The pipeline performs three main steps:
1. **Linting**: Checks the code for syntax errors and style issues.
2. **Unit Testing**: Runs quick tests on individual parts of our Python application.
3. **Integration Testing**: Builds a complete Docker container and tests the actual running application with a sample image.

By linking these steps, we ensure that a broken application is never merged or deployed to production!
