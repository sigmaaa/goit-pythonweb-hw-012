"""
File upload service module using Cloudinary.

This module provides the `UploadFileService` class for uploading files
(e.g., avatars) to Cloudinary and generating optimized URLs.

Classes:
    UploadFileService: Handles file uploads and avatar URL updates.
"""

import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service class for uploading files to Cloudinary and managing user avatars.

    Args:
        cloud_name (str): Cloudinary cloud name.
        api_key (str): Cloudinary API key.
        api_secret (str): Cloudinary API secret.
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initialize the UploadFileService with Cloudinary credentials.

        :param cloud_name: Cloudinary cloud name.
        :param api_key: Cloudinary API key.
        :param api_secret: Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username: str) -> str:
        """
        Upload a file to Cloudinary and generate a resized URL.

        The file is stored under the path "RestApp/{username}" and is resized
        to 250x250 pixels using a "fill" crop.

        :param file: The file object to upload (must have a `.file` attribute).
        :param username: The username to include in the public Cloudinary ID.
        :return: URL of the uploaded and resized file.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL for a user.

        :param email: The email of the user.
        :param url: The new avatar URL.
        :return: Result of the repository update operation.
        """
        return await self.repository.update_avatar_url(email, url)
