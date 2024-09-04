# pylint: disable=logging-fstring-interpolation,f-string-without-interpolation,consider-using-f-string
"""
  Deletes custom IAM roles at the organization level.
"""

import logging
from google.cloud.iam_admin_v1 import IAMClient, ListRolesRequest, RoleView, DeleteRoleRequest, Role
from google.cloud.iam_admin_v1.services.iam.pagers import ListRolesPager
from google.api_core.exceptions import FailedPrecondition, NotFound

logger = logging.getLogger("default")


def delete(organization_id, exclude_custom_roles, dry_run):
  """
    Delete custom roles at the organization level.

    Parameters:
      organization_id (str): The ID of the organization.
      exclude_custom_roles (str): Comma-separated list of custom role names to exclude from deletion.
      dry_run (bool, optional): If True, only simulate the deletions without actually performing them. Default is False.
    """
  logger.info("Starting processing custom roles")

  custom_role_list = _list_custom_roles(organization_id)

  logger.info(f"Retrieved {len(custom_role_list)} custom role(s)")

  exclude_custom_roles_list = exclude_custom_roles.split(
      ",") if exclude_custom_roles else []

  for role in custom_role_list:
    role_id = role.name.split('/')[-1]

    if role.name in exclude_custom_roles_list:
      logger.info(f"Excluding custom role '{role.name}'")
      continue

    log_message = "%sDeleting custom role %s ." % ("(Simulated) " if dry_run
                                                   else "", role.name)
    logger.info(log_message)

    if not dry_run:
      _delete_custom_role(organization_id, role_id)

  logger.info("Done processing custom roles")


def _list_custom_roles(organization_id: str) -> ListRolesPager:
  """
    Lists custom IAM roles in a GCP organization.

    Args:
        organization_id: GCP organization ID

    Returns: A pager for traversing through the roles
  """
  client = IAMClient()
  parent = f"organizations/{organization_id}"
  request = ListRolesRequest(
      parent=parent,
      show_deleted=False,
      view=RoleView.BASIC,
  )
  roles = client.list_roles(request)
  custom_roles = [role for role in roles]
  return custom_roles


def _delete_custom_role(organization_id: str, role_id: str) -> Role:
  """
    Deletes a custom IAM role in a GCP organization.

    Args:
        organization_id: GCP organization ID
        role_id: ID of the GCP custom IAM role

    Returns: The deleted google.cloud.iam_admin_v1.Role object
  """
  client = IAMClient()
  name = f"organizations/{organization_id}/roles/{role_id}"
  request = DeleteRoleRequest(name=name)
  try:
    role = client.delete_role(request)
    logger.info(f"Deleted role: {role_id}: {role}")
    return role
  except NotFound:
    logger.warning(f"Role with id [{role_id}] not found")
  except FailedPrecondition as err:
    logger.warning(f"Role with id [{role_id}] cannot be deleted", err)
