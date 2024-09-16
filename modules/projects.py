# pylint: disable=logging-fstring-interpolation,f-string-without-interpolation,consider-using-f-string
"""
  Deletes all projects which exist within an organization.
"""
import logging
from google.cloud import resourcemanager_v3
from google.cloud.resourcemanager_v3 import SearchProjectsRequest
from google.cloud.resourcemanager_v3.services.projects.pagers import ListProjectsPager

from googleapiclient.discovery import build

logger = logging.getLogger("default")


def delete(folders_list, exclude_projects, dry_run):
  """
  Delete projects within the specified organization, including any existing liens.

  Parameters:
      organization_id (str): The ID of the organization.
      folders_list (list): List of folder objects to process for project deletion.
      exclude_projects(str): Comma-separated list of project IDs to exclude from deletion.
      dry_run (bool, optional): If True, only simulate the deletions without actually performing them. Default is False.
  """
  logger.info("Starting processing projects")

  exclude_projects_list = exclude_projects.split(
      ",") if exclude_projects else []
  project_client = resourcemanager_v3.ProjectsClient()

  for folder in reversed(folders_list):
    project_list = _list_projects(folder.name)
    logger.info(
        f"Retrieved {len(list(project_list))} project(s) under folder {folder.name}"
    )

    for project in project_list:
      project_id = project.project_id

      if project_id not in exclude_projects_list:
        log_message = "%sDeleting project %s." % ("(Simulated) " if dry_run else
                                                  "", project_id)
        logger.info(log_message)

        if not dry_run:
          _delete_project(project_client, project_id)

  logger.info("Done processing projects")


def _list_projects(folder_name: str) -> ListProjectsPager:
  """
  Lists projects within the specified folder.

  Args:
      folder_name: GCP folder name in the format 'folders/{folder_id}'

  Returns: A pager for traversing through the projects
  """
  client = resourcemanager_v3.ProjectsClient()
  request = SearchProjectsRequest(
      query=f"parent.id:{folder_name.split('/')[-1]} state:ACTIVE",)
  projects = client.search_projects(request=request)
  return projects


def _delete_project(project_client, project_id):
  """
  Deletes a project, handling any existing liens.

  Parameters:
      project_client (google.cloud.resourcemanager_v3.ProjectsClient): The Resource Manager Projects client
      project_id (str): The ID of the project to delete
  """
  try:
    project_client.delete_project(name=f"projects/{project_id}")
  except Exception as e:
    if "lien" in str(e):
      logger.warning(
          f"Project {project_id} has a lien. Removing lien before deletion.")
      _remove_project_lien(project_id)
      # Retry deleting the project after removing the lien
      logger.warning(f"Retrying to delete {project_id} after cleaning lien(s).")
      project_client.delete_project(name=f"projects/{project_id}")
    else:
      logger.error(f"Failed to delete project {project_id}: {e}")


def _remove_project_lien(project_id):
  """
  Removes any liens associated with the project

  Parameters:
      project_id (str): The ID of the project
  """

  # Build the Cloud Resource Manager API client
  lien_service = build('cloudresourcemanager', 'v3', cache_discovery=False)
  parent = f"projects/{project_id}"
  # pylint: disable=no-member
  request = lien_service.liens().list(parent=parent)

  response = request.execute()
  liens = response.get("liens", [])
  if not liens:
    logger.error(
        f"Well that's unexpected! No liens found for project {project_id}")
  else:
    for lien in liens:
      logger.info(f"Deleting lien {lien['name']}")
      lien_service.liens().delete(name=lien['name']).execute()
  return liens
