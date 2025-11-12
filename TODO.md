# Contractor Pay Tracker - TODO List

**Last Updated**: 2025-11-12
**Current Status**: ✅ Contractor-umbrella mapping system implemented and deployed

---

## Completed ✅

### Phase 1: Core System (DONE)
- [x] Set up AWS infrastructure with Terraform
- [x] Implement S3 file upload
- [x] Build Excel parsing (Excel97-2004 support)
- [x] Implement contractor fuzzy matching
- [x] Build validation engine
- [x] Implement DynamoDB storage
- [x] Deploy Lambda functions with SQS event sources

### Phase 2: Bug Fixes (DONE)
- [x] Fix umbrella company determination bug
- [x] Fix JSONPath naming mismatch in Step Functions
- [x] Fix 8 bugs in excel_parser.py
- [x] Add 4 improvements to fuzzy_matcher.py
- [x] Investigate and resolve "zero TimeRecords" issue (was false alarm)

### Phase 3: AWS Resource Management (DONE - 2025-11-10)
- [x] Implement comprehensive AWS resource tagging
- [x] Create centralized tag management in Terraform (locals.tf)
- [x] Tag all 17 AWS resources with standardized schema
- [x] Activate cost allocation tags in AWS Billing
- [x] Generate comprehensive tagging documentation
- [x] Deploy updated Terraform configuration

### Phase 4: SQS Pipeline Infrastructure Fixes (DONE - 2025-11-11)
- [x] Fix Lambda environment variable bug (TABLE_NAME literal string)
- [x] Fix Lambda layer directory structure (python/ at root)
- [x] Deploy Lambda layer v36 with correct structure
- [x] Fix GSI3→GSI1 bug in contractor validation
- [x] Add detailed logging to validation stage
- [x] Fix Excel parser field mapping (contractor_name, pay_rate, units)
- [x] Identify contractor PROFILE records missing (root blocker)
- [x] Identify Flask API field name bug (CompanyName→LegalName)
- [x] Update project documentation (PROJECT_CONTEXT.md, TODO.md)

### Phase 5: Contractor-Umbrella Mapping System (DONE - 2025-11-12)
- [x] Design ContractorUmbrellaMapping database schema (one-to-many support)
- [x] Implement GET /api/contractor-umbrella-mappings endpoint
- [x] Implement POST /api/contractor-umbrella-mappings endpoint
- [x] Implement DELETE /api/contractor-umbrella-mappings endpoint
- [x] Implement GET /api/umbrellas endpoint
- [x] Build contractor-umbrella mapping UI page (/contractor-umbrella-mapping)
- [x] Add navigation link to base template
- [x] Update Lambda validation logic to use dynamic mappings
- [x] Deploy Lambda layer v2 with updated validators.py
- [x] Create 26 contractor-umbrella mappings (including Donna Smith double-mapping)
- [x] Fix JavaScript dropdown loading bug (success field check)
- [x] Test mapping creation and display functionality

---

## In Progress 🚧

### Validation Testing (P1)
- [ ] **Test end-to-end validation with fresh file upload**
  - **What**: Upload new test file and verify validation passes with contractor-umbrella mappings
  - **Why**: Validate that new mapping system works in production
  - **Effort**: Small (single test upload + CloudWatch logs review)
  - **Priority**: P1 - Verify deployment
  - **Dependencies**: None (mappings already created)
  - **Status**: Ready to test

- [ ] **Process all 48 production files from InputData/**
  - **What**: Upload all 48 Excel files and verify processing
  - **Why**: User's primary request - "count shld be the number of foles in this directory"
  - **Effort**: Medium (bulk upload + monitoring)
  - **Priority**: P0 - User requested
  - **Dependencies**: Verify single file validation first

---

## Potential Improvements (Low Priority)

### Data Quality
- [ ] Add contractor baseline rates for overtime validation
  - Currently: 85% of failures are missing baseline rates
  - Impact: Would increase success rate from 56% to ~95%
  - Effort: Medium (need to backfill data)

- [ ] Improve VAT calculation validation
  - Currently: 10% of failures are VAT calculation errors
  - Impact: Would reduce validation failures
  - Effort: Small (update validation rules)

### Validation Enhancements
- [ ] Make overtime validation more lenient for first-time imports
  - Currently: Strict validation requires existing baseline data
  - Impact: Better user experience for new contractors
  - Effort: Small (update validation logic)

### Reporting
- [ ] Build report generator functionality
  - Lambda function exists but not fully implemented
  - Impact: Ability to generate pay reports
  - Effort: Medium

### Monitoring
- [ ] Add CloudWatch alarms for failed executions
  - Impact: Proactive failure notifications
  - Effort: Small (Terraform + SNS)

- [ ] Create dashboard for system metrics
  - Impact: Visibility into system health
  - Effort: Medium (CloudWatch dashboards)

### Documentation
- [ ] Add inline code comments for PayRecord vs TimeRecord
  - Impact: Prevent future confusion
  - Effort: Trivial

- [ ] Document validation rules
  - Impact: Better understanding of validation logic
  - Effort: Small

- [ ] Create query examples for DynamoDB
  - Impact: Easier data exploration
  - Effort: Trivial

### Performance
- [ ] Optimize Excel parsing for large files
  - Impact: Faster processing times
  - Effort: Medium

- [ ] Add caching for contractor lookups
  - Impact: Faster fuzzy matching
  - Effort: Small

---

## Technical Debt

- [ ] Clean up background Bash processes from investigation
  - Multiple monitoring scripts still running
  - Safe to kill after current session

- [ ] Review and optimize Lambda memory/timeout settings
  - Current settings may not be optimal
  - Effort: Trivial

- [ ] Add error recovery logic in Step Functions
  - Currently: Failed executions require manual intervention
  - Effort: Medium

---

## Future Considerations

### Frontend
- [ ] Build web UI for file upload
  - Currently: Files uploaded via AWS CLI
  - Impact: Better user experience
  - Effort: Large

- [ ] Build dashboard for viewing reports
  - Impact: Easy access to pay data
  - Effort: Large

### API
- [ ] Build REST API for programmatic access
  - Impact: Integration with other systems
  - Effort: Medium (API Gateway + Lambda)

### Security
- [ ] Add authentication/authorization
  - Impact: Secure access control
  - Effort: Medium (Cognito)

- [ ] Implement data encryption at rest
  - Impact: Enhanced security
  - Effort: Small (already supported by AWS services)

### Testing
- [ ] Add unit tests for Lambda functions
  - Impact: Better code quality
  - Effort: Medium

- [ ] Add integration tests for Step Functions
  - Impact: Catch bugs before deployment
  - Effort: Medium

---

## Notes

### When Restarting Claude Code
1. Read `PROJECT_CONTEXT.md` first
2. Read this TODO file
3. Ask: "What feature do you want to build next?"
4. Update this file as we complete tasks

### Workflow Tips
- Commit after completing each major feature
- Update PROJECT_CONTEXT.md after significant changes
- Restart Claude Code every 1-2 hours to avoid compacting

### Feature Request Template
When adding a new feature to this list:
```markdown
- [ ] Feature Name
  - **What**: Brief description
  - **Why**: Business value
  - **Effort**: Small/Medium/Large
  - **Priority**: High/Medium/Low
  - **Dependencies**: List any blockers
  - **Technical Notes**: Implementation details
```

---

**Ready to Build**: System is stable and ready for new features!
