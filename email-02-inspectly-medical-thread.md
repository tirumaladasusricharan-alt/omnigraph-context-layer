# Email Thread: Inspectly Bug in Medical Devices Module

**Subject**: URGENT: Inspectly Auto-Audit log failure for MedTech Corp
**Is Internal**: True

**From**: Alex (Customer Support Lead)
**To**: Engineering Team
**Date**: November 2, 2023

Hey all,
MedTech Corp just reported that the Auto-Audit Log feature missed three compliance events yesterday. Their QA Director is furious because they have an ISO27001 audit next week. This is a severity 1 issue.

**From**: Jessica (Lead Engineer)
**To**: Alex; Engineering Team
**Date**: November 2, 2023

Looking into it now. It seems the compliance scanner timed out due to the large volume of events they generated. 
Decision: We are pushing a hotfix to increase the timeout threshold and we will manually backfill the logs for them tonight. Do not mention the timeout issue externally, just tell them it's a "sync delay".
