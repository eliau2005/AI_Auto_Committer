from typing import List, Set

class AppState:
    def __init__(self):
        self._repo_path: str = ""
        self._current_branch: str = ""
        self._changed_files: List[str] = []
        self._selected_files: Set[str] = set()
        self._commit_title: str = ""
        self._commit_description: str = ""
        self._is_loading: bool = False

    @property
    def repo_path(self) -> str:
        return self._repo_path

    @repo_path.setter
    def repo_path(self, value: str):
        if not isinstance(value, str):
            raise TypeError("repo_path must be a string")
        self._repo_path = value

    @property
    def current_branch(self) -> str:
        return self._current_branch

    @current_branch.setter
    def current_branch(self, value: str):
        if not isinstance(value, str):
            raise TypeError("current_branch must be a string")
        self._current_branch = value

    @property
    def changed_files(self) -> List[str]:
        return self._changed_files

    @changed_files.setter
    def changed_files(self, value: List[str]):
        if not isinstance(value, list):
            raise TypeError("changed_files must be a list of strings")
        self._changed_files = value

    @property
    def selected_files(self) -> Set[str]:
        return self._selected_files

    @selected_files.setter
    def selected_files(self, value: Set[str]):
        if not isinstance(value, set):
            raise TypeError("selected_files must be a set of strings")
        self._selected_files = value

    @property
    def commit_title(self) -> str:
        return self._commit_title

    @commit_title.setter
    def commit_title(self, value: str):
        if not isinstance(value, str):
            raise TypeError("commit_title must be a string")
        self._commit_title = value

    @property
    def commit_description(self) -> str:
        return self._commit_description

    @commit_description.setter
    def commit_description(self, value: str):
        if not isinstance(value, str):
            raise TypeError("commit_description must be a string")
        self._commit_description = value

    @property
    def is_loading(self) -> bool:
        return self._is_loading

    @is_loading.setter
    def is_loading(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("is_loading must be a boolean")
        self._is_loading = value
