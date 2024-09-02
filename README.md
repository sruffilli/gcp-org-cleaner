# GCP Organization Cleaner

GCP Organization Cleaner is a command-line tool designed to help you purge all resources within a GCP organization. Its ultimate goal is to support the cleanup of E2E test deployments.

## Features

- Delete organization policies: Remove organization-level IAM policies that are no longer needed.
- Delete firewall policies: Clean up firewall policies associated with the specified organization.
- Delete log sinks: Remove log sinks (export destinations) that are configured for the organization.
- Delete secure tags: Delete secure tag keys and values associated with the organization.
- Delete custom roles: Remove custom roles that are no longer needed.
- Delete projects: Delete projects within the specified organization, including any existing liens.

## Prerequisites

- **Python 3.x**
- **Required Libraries:** Install the necessary libraries using `pip install -r requirements.txt`.
- **Authentication:** Ensure that your environment is authenticated to use the Google Cloud SDK. You can achieve this by running `gcloud auth application-default login`.
- **Permissions:** The user or service account running the script needs at least the following permissions at the organization level:

- `roles/compute.securityAdmin` (For deleting firewall policies)
- `roles/logging.admin` (For deleting log sinks)
- `roles/orgpolicy.policyAdmin` (For deleting organization policies)
- `roles/resourcemanager.folderAdmin` (For listing resources in folders)
- `roles/resourcemanager.organizationAdmin` (For deleting projects and other organization-level resources)
- `roles/resourcemanager.tagAdmin` (For deleting secure tags)
- `roles/iam.roleAdmin` (For deleting custom roles)
- `roles/cloudasset.viewer` (For searching resources using Cloud Asset Inventory)

## Usage

To use GCP Organization Cleaner run:

```bash
python org_cleaner.py <organization_id> [options]
```

Replace <organization_id> with the ID of the target GCP organization.

Available options:

```bash
--dry-run: Perform a dry-run without actual deletions.
--exclude-custom-roles: Exclude specific custom roles in 'organizations/{id}/roles/{customrole_name}' format, comma-separated.
--exclude-log-sinks: Exclude specific log sinks in '{organizations,folders}/{id}/sinks/{sink_name}' format, comma-separated.
--exclude-projects: Exclude specific projects using their project IDs, comma-separated
--only-custom-roles: Only delete custom roles.
--only-fwpolicies: Only delete firewall policies.
--only-logsinks: Only delete log sinks.
--only-orgpolicies: Only delete organization policies.
--only-projects: Only delete projects
--only-securetags: Only delete secure tag keys and values.
```

Examples
Delete all types of resources within the organization:

```bash
python org_cleaner.py <organization_id>
```

Delete only organization policies and log sinks (dry-run):

```bash
python org_cleaner.py <organization_id> --dry-run --only-orgpolicies --only-logsinks
```

Delete specific log sinks:

```bash
python org_cleaner.py <organization_id> --exclude-log-sinks=<sink1,sink2> --only-logsinks
```

Exclude specific custom roles and delete the rest

```bash
python org_cleaner.py <organization_id> --exclude-custom-roles='organizations/123456789/roles/CustomRole1,organizations/123456789/roles/CustomRole2' --only-customroles
```

Exclude specific projects

```bash
python org_cleaner.py <organization_id> --exclude-projects='project-1,project-2' --only-projects
```
