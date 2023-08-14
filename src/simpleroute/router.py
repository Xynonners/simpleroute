#mostly made for url routing tbh, but is also a treelib

from pathlib import PurePath

from typing import (
    Any
)

from rich import print
from rich.tree import Tree

import io
from contextlib import redirect_stdout

class PathHandler():
    @staticmethod
    def split(path: str) -> list:
        return [*PurePath(path).parts]
    @staticmethod
    def join(parts: list) -> str:
        return PurePath(*parts).as_posix()

ph = PathHandler()

class BaseRouter():
    def add_node(self, path: str) -> None:
        current = self.tree
        for seg in ph.split(path):
            if not seg in current:
                if self.wc_check:
                    if seg.startswith(":"):
                        for key in current:
                            if key.startswith(":"):
                                print(f"[bold red]WARNING: segment {seg} added when wildcard segment {key} already exists.[/bold red]")
                                break
                current[seg] = {}
            current = current[seg]

    def add_nodes(self, paths: list) -> None:
        for path in paths:
            self.add_node(path)

    def __init__(self, paths: list, catchall:str="/", wc_check=True) -> None:
        self.tree = {}
        self.catchall = ph.split(catchall)
        self.wc_check = wc_check
        self.add_nodes(paths)

    def match(self, route: str) -> (str, dict):
        split = []
        kwargs = {}
        current = self.tree
        for seg in ph.split(route):
            if seg in current:
                current = current[seg]
                split.append(seg)
            else:
                for key in current:
                    if key.startswith(":"):
                        current = current[key]
                        split.append(key)
                        kwargs.update({key[1:]: seg})
                        break
                else:
                    split = self.catchall
        return ph.join(split), kwargs

    def show(self) -> None:
        tree = Tree("[bold black]root[bold black]")
        current = tree
        def iterdict(d):
            nonlocal current
            #basically a contextmanager
            for k, v in d.items():
                old_current = current
                if k.startswith(":"):
                    current = current.add(f"[bold black]{k}[/bold black]")
                else:
                    current = current.add(f"[bold white]{k}[/bold white]")
                iterdict(v)
                current = old_current
        iterdict(self.tree)
        print(tree)

    def __repr__(self) -> str:
        f = io.StringIO()
        with redirect_stdout(f):
            self.show()
        out = f.getvalue()
        return out

class Router(BaseRouter):
    def add_node(self, path: str, data:Any=None) -> None:
        super().add_node(path)
        self.data[path] = data

    def add_nodes(self, data: dict) -> None:
        for path in data:
            self.add_node(path, data=data[path])
            self.data[path] = data[path]

    def __init__(self, data: dict, catchall:str="/", wc_check=True) -> None:
        self.data = data
        super().__init__(data, catchall=catchall, wc_check=wc_check)

    def match(self, route: str) -> (str, dict, Any):
        path, kwargs, = super().match(route)
        return path, kwargs, self.data[path]

#somewhat disgusting fake node impl
class Traverse():
    @classmethod
    def go(cls, router: BaseRouter, path:str="") -> "Traverse":
        current = cls(router, router.tree, [], path)
        for seg in ph.split(path):
            current = current.get_child(seg)
        return current

    def __init__(self, router: Any, current: dict, parents: list, path: str) -> None:
        self.router = router
        self.__current = current
        self.__parents = parents
        self.path = path

    def get_child(self, name: str) -> "Traverse":
        return type(self)(self.router, self.__current[name], self.__parents + [self.__current], ph.join(ph.split(self.path) + [name]))

    def get_children(self) -> list:
        children = []
        for child in self.__current:
            children.append(self.get_child(child))
        return children

    def get_parent(self) -> "Traverse":
        return type(self)(self.router, self.__parents[-1], self.__parents[:-1], ph.join(ph.split(self.path)[:-1]))

    def get_data(self) -> Any:
        if hasattr(self.router, "data"):
            data = self.router.data.get(self.path)
        else:
            data = None
        return data

    def get_path(self) -> str:
        return self.path

    def get_sub(self) -> BaseRouter:
        sub = type(self.router)({})
        sub.tree = self.__current
        if hasattr(sub, "data"):
            sub.data = self.router.data
        return sub

    def __repr__(self) -> str:
        return f"Traverse({self.path}, {repr(self.get_data())})"


