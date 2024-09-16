# pylint: disable=logging-fstring-interpolation,f-string-without-interpolation,consider-using-f-string
"""
  Deletes all folders under an organization.
"""
import logging
from collections import deque
from google.cloud import resourcemanager_v3

logger = logging.getLogger("default")


def delete(folder_list, dry_run):
  """
    Delete folders under the specified organization.

    Parameters:
        organization_id (str): The ID of the organization.
        folders_list (list): List of folder objects to process for project deletion.
        dry_run (bool, optional): If True, only simulate the deletions without actually performing them. Default is False.
    """
  logger.info("Starting processing folders")

  logger.info(f"Retrieved {len(folder_list)} folder(s)")

  client = resourcemanager_v3.FoldersClient()

  # Delete folders in reverse order to handle child folders first
  for folder in reversed(folder_list):
    if folder.name.split('/')[0] == "organizations":
      continue

    folder_id = folder.name.split('/')[1]

    log_message = "%sDeleting folder %s." % ("(Simulated) " if dry_run else "",
                                             folder_id)
    logger.info(log_message)

    if not dry_run:
      try:
        client.delete_folder(name=folder.name)
      except Exception as e:
        logger.error(f"Failed to delete folder {folder_id}: {e}")

  logger.info("Done processing folders")
