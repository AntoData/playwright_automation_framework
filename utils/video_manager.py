"""
This module provides functionality for managing Playwright videos
during tests runs. It includes a class for video settings, which
retrieves configuration parameters from a specified configuration file,
 and a function that handles the saving of Playwright videos at the
 end of each tests. The function ensures that videos are saved to a
specified path with a unique name based on the tests name and timestamp,
  and includes error handling to log any issues that arise during the
  saving process.
"""
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page
from utils import config_adapter
from utils import settings_manager
from utils import path_utils
from utils import logging_adapter


@settings_manager.settings_manager(connector=config_adapter.ConfigFileAdapter,
                                   path="/config/config.ini",
                                   settings_list=["temp_video_path",
                                                  "final_video_path"])
class VideoSettings:
    """
    Manages the settings for Playwright video management module
    """
    settings: dict | None = None


def playwright_video_manager(page: Page, video_name: str) -> None:
    """
    Manages the saving of Playwright videos for tests runs. This
    function should be called at the end of each tests to ensure that
     videos are saved correctly.

    :param page: The Playwright Page object associated with the current
    tests.
    :type page: Page
    :param video_name: A name to identify the video, typically
    related to the tests name
    :type video_name: str
    """
    log: logging.Logger = (
        logging_adapter.LoggingAdapter.get_logger())
    video = page.video
    log.info("")
    log.info("--- After test execution: Managing Playwright video ---")
    video_path_relative: str = VideoSettings.settings["final_video_path"]
    # Save the video to the specified path
    if video:
        log.info(f"Saving video to {video_path_relative}")
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name: str = "{0}-{1}.webm".format(video_name, timestamp)
        full_video_path: str = (path_utils.get_project_root() + "/" +
                                video_path_relative + "/" + file_name)
        log.info("Full video path: {0}".format(full_video_path))
        Path(os.path.dirname(full_video_path) or ".").mkdir(
            parents=True, exist_ok=True)
        try:
            log.info("Attempting to save video for {0} at {1}".format(
                video_name, full_video_path))
            video.save_as(full_video_path)
            log.info("Video saved successfully for {0} at {1}".format(
                video_name, full_video_path))
        except (RuntimeError, IOError, Exception) as e:
            log.error(f"Failed to save video for "
                      f"{video_name}: {e}")
            try:
                log.info("Retrying to save video for {0} by copying "
                         "from temp path".format(video_name))
                shutil.copy(video.path(), full_video_path)
                log.info("Video saved successfully for {0} at {1} using"
                         " copy method".format(video_name,
                                               full_video_path))
            except (RuntimeError, IOError) as e:
                log.error(f"Failed to save video for "
                          f"{video_name}: {e}")