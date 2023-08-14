# SimpleRoute <img src=https://openclipart.org/download/245411 height=40 align=top>
A simple router / treelib for python.

## Usage

### Installation
```
pip install simpleroute
```

### Import
*Note: as simpleroute uses two dictionaries internally rather than an OOP-based node system,*

*Traverse replaces the standard "Node" class present in most other tree libraries.*
```python
from simpleroute import BaseRouter, Router, Traverse
```

### Classes
```python
router = BaseRouter([]) # list of paths sep by /
path, kwargs = router.match("SOME_STR_HERE") #match wildcards, eg /etc/1 to /etc/:num
```

```python
router = Router({}) # dict of paths:datavals sep by /
path, kwargs, data = router.match("SOME_STR_HERE") #match wildcards, eg /etc/1 to /etc/:num
```

```python
traverse = Traverse.go(router, path="SOME_PATH_HERE") #returns an object of Traverse, optional path to go
#use get_child, get_children, get_parent, get_data, get_path, get_sub to manipulate the object
```
