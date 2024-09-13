# GCP Organization Cleaner

GCP Organization Cleaner is a command-line tool designed to help you purge all resources within a GCP organization. Its ultimate goal is to support the cleanup of E2E test deployments.

## Features

Deletes:

- custom roles
- firewall policies
- folders
- log sinks
- organization policies
- projects
- secure tags

## Prerequisites

- **Python 3.x**
- **Virtual Environment:** Create and activate a virtual environment:

```bash
python3 -m venv ~/.envs/gcp-org-cleaner
source ~/.envs/gcp-org-cleaner/bin/activate
pip install -r requirements.txt
```

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

Grant your Organization Administrator user the required permissions by running the following commands:

```bash
# set variable for current logged in user
export CURRENT_USER=$(gcloud config list --format 'value(core.account)')

# find and set your org id
gcloud organizations list
export ORG_ID=123456

# set needed roles
export ROLES="roles/compute.securityAdmin roles/logging.admin roles/orgpolicy.policyAdmin roles/resourcemanager.folderAdmin roles/resourcemanager.organizationAdmin roles/resourcemanager.tagAdmin roles/iam.roleAdmin roles/cloudasset.viewer"

for role in $ROLES; do
  gcloud organizations add-iam-policy-binding $ORG_ID \
    --member user:$CURRENT_USER --role $role --condition None
done
```

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
--exclude-folders: Exclude specific folders in 'folders/{id}' format, comma-separated.
--exclude-log-sinks: Exclude specific log sinks in '{organizations,folders}/{id}/sinks/{sink_name}' format, comma-separated.
--exclude-projects: Exclude specific projects using their project IDs, comma-separated.
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

Delete log sinks, with exceptions:

```bash
python org_cleaner.py <organization_id> --exclude-log-sinks=<sink1,sink2> --only-logsinks
```

Exclude specific custom roles

```bash
python org_cleaner.py <organization_id> --exclude-custom-roles='organizations/123456789/roles/CustomRole1,organizations/123456789/roles/CustomRole2' --only-customroles
```

Exclude specific projects

```bash
python org_cleaner.py <organization_id> --exclude-projects='project-1,project-2' --only-projects
```
