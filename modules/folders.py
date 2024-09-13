# pylint: disable=logging-fstring-interpolation,f-string-without-interpolation,consider-using-f-string
"""
  Deletes all folders under an organization.
"""
import logging
from collections import deque
from google.cloud import resourcemanager_v3

logger = logging.getLogger("default")


def delete(organization_id, exclude_folders, dry_run):
  """
    Delete folders under the specified organization.

    Parameters:
        organization_id (str): The ID of the organization.
        exclude_folders (str): Comma-separated list of folder IDs to exclude from deletion.
        dry_run (bool, optional): If True, only simulate the deletions without actually performing them. Default is False.
    """
  logger.info("Starting processing folders")

  exclude_folders_list = exclude_folders.split(",") if exclude_folders else []
  folder_list = _list_all_folders(organization_id, exclude_folders_list)
  logger.info(f"Retrieved {len(folder_list)} folder(s)")

  client = resourcemanager_v3.FoldersClient()

  # Delete folders in reverse order to handle child folders first
  for folder in reversed(folder_list):
    folder_id = folder.name.split('/')[-1]

    if folder_id in exclude_folders_list:
      logger.info(f"Excluding folder '{folder_id}'")
      continue

    parent_folder_id = folder.parent.split('/')[-1] if folder.parent else None
    if parent_folder_id and parent_folder_id in exclude_folders_list:
      logger.info(
          f"Excluding folder '{folder_id}' because its parent folder '{parent_folder_id}' is excluded."
      )
      continue

    log_message = "%sDeleting folder %s." % ("(Simulated) " if dry_run else "",
                                             folder_id)
    logger.info(log_message)

    if not dry_run:
      try:
        client.delete_folder(name=folder.name)
      except Exception as e:
        logger.error(f"Failed to delete folder {folder_id}: {e}")

  logger.info("Done processing folders")


def _list_all_folders(organization_id: str, exclude_folders_list: list):
  """
    Lists all folders under the specified organization, including nested folders.

    Args:
        organization_id: GCP organization ID

    Returns: A list of folder objects in deletion order (leaves first).
  """
  folders = []
  queue = deque([f"organizations/{organization_id}"])

  while queue:
    parent = queue.popleft()
    if parent in exclude_folders_list:
      logger.info(f"Excluding folder '{parent}'")
      continue

    client = resourcemanager_v3.FoldersClient()
    request = resourcemanager_v3.ListFoldersRequest(parent=parent)
    logger.info(f"Retrieving folders under {parent}")
    for folder in client.list_folders(request=request):
      logger.info(f"Found folder parent={parent} folder={folder.name}")
      folders.append(folder)
      queue.append(folder.name)

  return folders
