# pylint: disable=logging-fstring-interpolation,f-string-without-interpolation,consider-using-f-string
import logging
from collections import deque
from google.cloud import resourcemanager_v3

logger = logging.getLogger("default")


def list_all_folders(organization_id: str, exclude_folders_list: list = []):
  """
    Lists all folders under the specified organization, including nested folders.

    Args:
        organization_id: GCP organization ID

    Returns: A list of folder objects in deletion order (leaves first).
  """
  folders = []
  # Add organization as the first node
  folders.append(
      resourcemanager_v3.Folder(name=f"organizations/{organization_id}"))
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
