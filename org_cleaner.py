"""
  Deletes resources from a Google Cloud organization.
"""
import logging
import click
from google.cloud import asset
from modules import firewall_policies, log_sinks, org_policies, secure_tags, custom_roles, projects, folders

# Set up logging configuration
logger = logging.getLogger("default")
logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
logging.root.setLevel(logging.INFO)


# Define the main function using Click
@click.command()
@click.argument("organization_id", type=str, required=True)
@click.option("--dry-run", is_flag=True,
              help="Perform a dry-run without actual deletions.")
@click.option(
    "--exclude-customroles", help=
    "Custom roles to exclude, in 'organizations/{id}/roles/{customrole_name}' format, comma separated."
)
@click.option(
    "--exclude-folders",
    help="Folders to exclude, in 'folders/{folder_id}' format, comma separated."
)
@click.option(
    "--exclude-log-sinks", help=
    "Log sinks to exclude in '{organizations,folders}/{id}/sinks/{sink_name}' format, comma separated."
)
@click.option(
    "--exclude-projects", help=
    "Log sinks to exclude in '{organizations,folders}/{id}/sinks/{sink_name}' format, comma separated."
)
@click.option("--only-customroles", is_flag=True,
              help="Only delete custom roles.")
@click.option("--only-folders", is_flag=True, help="Only delete folders.")
@click.option("--only-fwpolicies", is_flag=True,
              help="Only delete firewall policies.")
@click.option("--only-logsinks", is_flag=True, help="Only delete log sinks.")
@click.option("--only-orgpolicies", is_flag=True,
              help="Only delete organization policies")
@click.option("--only-projects", is_flag=True, help="Only delete projects.")
@click.option("--only-securetags", is_flag=True,
              help="Only delete secure tag keys and values")
def main(organization_id, dry_run, exclude_customroles, exclude_log_sinks,
         exclude_projects, only_customroles, only_orgpolicies, only_projects,
         only_fwpolicies, only_logsinks, only_securetags, only_folders,
         exclude_folders):
  """
    Deletes resources from a Google Cloud organization.

    Args:
        organization_id (str): The ID of the organization.
        dry_run (bool): If True, only simulate the deletions without actually performing them.
        exclude_customroles (str): Comma-separated list of custom role names to exclude from deletion.
        exclude_folders (str): Comma-separated list of folder IDs to exclude from deletion.
        exclude_log_sinks (str): Comma-separated list of log sink names to exclude from deletion.
        exclude_projects (str): Comma-separated list of project IDs to exclude from deletion.
        only_customroles (bool): If True, only delete custom roles.
        only_folders (bool): If True, only delete folders.
        only_orgpolicies (bool): If True, only delete organization policies.
        only_projects (bool): If True, only delete projects.
        only_fwpolicies (bool): If True, only delete firewall policies.
        only_logsinks (bool): If True, only delete log sinks.
        only_securetags (bool): If True, only delete secure tag keys and values.
    """
  logger.info("Starting")

  delete_all = not any([
      only_customroles, only_orgpolicies, only_logsinks, only_fwpolicies,
      only_securetags, only_projects, only_folders
  ])

  cai_client = asset.AssetServiceClient()

  if delete_all or only_customroles:
    custom_roles.delete(organization_id, exclude_customroles, dry_run)

  if delete_all or only_orgpolicies:
    org_policies.delete(cai_client, organization_id, dry_run)

  if delete_all or only_fwpolicies:
    firewall_policies.delete(cai_client, organization_id, dry_run)

  if delete_all or only_logsinks:
    log_sinks.delete(cai_client, organization_id, exclude_log_sinks, dry_run)

  if delete_all or only_securetags:
    secure_tags.delete(cai_client, organization_id, dry_run)

  if delete_all or only_projects:
    projects.delete(organization_id, exclude_projects, dry_run)

  if delete_all or only_folders:
    folders.delete(organization_id, exclude_folders, dry_run)


if __name__ == "__main__":
  # pylint: disable=no-value-for-parameter
  main()
