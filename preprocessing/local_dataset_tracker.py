import json
import logging
from typing import List, Optional
from pathlib import Path


class LocalDatasetTracker:
    """
    A local implementation of the DatasetTracker that uses the local filesystem
    to store metadata, mimicking the behavior of the Firestore-based DatasetTracker.
    """

    def __init__(self, storage_path: str = "./data"):
        """
        Initializes the LocalDatasetTracker.

        Args:
            storage_path (str): The base path where metadata will be stored.
        """
        self.storage_path = Path(storage_path)
        self.raw_collection_path = self.storage_path / "raw_datasets_meta"
        self.processed_collection_path = self.storage_path / "processed_datasets_meta"
        self.raw_collection_path.mkdir(parents=True, exist_ok=True)
        self.processed_collection_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def _get_raw_meta_path(self, dataset_id: str) -> Path:
        return self.raw_collection_path / f"{dataset_id}.json"

    def _get_processed_meta_path(self, processed_dataset_id: str) -> Path:
        return self.processed_collection_path / f"{processed_dataset_id}.json"

    def track_raw_dataset(self, metadata: dict) -> None:
        """
        Tracks a raw uploaded dataset by saving its metadata to a local JSON file.
        """
        try:
            self.raw_collection_path.mkdir(parents=True, exist_ok=True)
            dataset_id = metadata["dataset_id"]
            meta_path = self._get_raw_meta_path(dataset_id)
            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=4)
            self.logger.info(f"Tracked raw dataset locally: {dataset_id}")
        except Exception as e:
            self.logger.error(f"Failed to track raw dataset {metadata.get('dataset_id', 'unknown')}: {e}")
            raise

    def track_processed_dataset(self, metadata: dict) -> None:
        """
        Tracks a processed dataset by saving its metadata to a local JSON file.
        """
        try:
            self.processed_collection_path.mkdir(parents=True, exist_ok=True)
            processed_dataset_id = metadata["processed_dataset_id"]
            meta_path = self._get_processed_meta_path(processed_dataset_id)
            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=4)
            self.logger.info(f"Tracked processed dataset locally: {processed_dataset_id}")
        except Exception as e:
            self.logger.error(f"Failed to track processed dataset {metadata.get('processed_dataset_id', 'unknown')}: {e}")
            raise

    def verify_raw_dataset_ownership(self, dataset_id: str, user_id: str) -> bool:
        """
        Verifies that a user owns a raw dataset by checking the local metadata file.
        """
        meta_path = self._get_raw_meta_path(dataset_id)
        if not meta_path.exists():
            return False
        with open(meta_path, "r") as f:
            metadata = json.load(f)
        return metadata.get("user_id") == user_id

    def verify_processed_dataset_ownership(self, processed_dataset_id: str, user_id: str) -> bool:
        """
        Verifies that a user owns a processed dataset by checking the local metadata file.
        """
        meta_path = self._get_processed_meta_path(processed_dataset_id)
        if not meta_path.exists():
            return False
        with open(meta_path, "r") as f:
            metadata = json.load(f)
        return metadata.get("user_id") == user_id

    def get_user_processed_datasets(self, user_id: str) -> List[str]:
        """
        Gets all processed dataset IDs owned by a user from the local metadata files.
        """
        user_datasets = []
        for meta_file in self.processed_collection_path.glob("*.json"):
            with open(meta_file, "r") as f:
                metadata = json.load(f)
            if metadata.get("user_id") == user_id:
                user_datasets.append(meta_file.stem)
        return user_datasets

    def get_processed_dataset_metadata(self, processed_dataset_id: str) -> Optional[dict]:
        """
        Gets processed dataset metadata by ID from the local metadata file.
        """
        meta_path = self._get_processed_meta_path(processed_dataset_id)
        if not meta_path.exists():
            return None
        with open(meta_path, "r") as f:
            return json.load(f)

    def delete_processed_dataset_metadata(self, processed_dataset_id: str) -> bool:
        """
        Deletes processed dataset metadata from the local filesystem.
        """
        meta_path = self._get_processed_meta_path(processed_dataset_id)
        if meta_path.exists():
            meta_path.unlink()
            self.logger.info(f"Deleted processed dataset metadata locally: {processed_dataset_id}")
            return True
        return False

    def delete_raw_dataset_metadata(self, dataset_id: str) -> bool:
        """
        Deletes raw dataset metadata from the local filesystem.
        """
        meta_path = self._get_raw_meta_path(dataset_id)
        if meta_path.exists():
            meta_path.unlink()
            self.logger.info(f"Deleted raw dataset metadata locally: {dataset_id}")
            return True
        return False
