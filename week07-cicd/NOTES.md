# NOTES.md — Week 7: CI/CD Integration Testing

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 142301003
seed: 1366810701
Wrote 6 images across 2 camera profiles -> D:\DS5619-MLOPS\week07-cicd\data\fixtures
Wrote 29 annotations -> D:\DS5619-MLOPS\week07-cicd\data\fixtures/_annotations.coco.json

## Why gate integration-test on needs: [lint, unit-test]?

To save time and resources. There is no point spending several minutes building a Docker container for the integration test if the basic code syntax (lint) or core logic (unit tests) is already broken locally!