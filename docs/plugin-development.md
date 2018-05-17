# Plugin development
This is an important step to enjoy all flexibility and features that this framework provides.

## Steps
1. Create a new folder under *broker/plugins* with the desired plugin name and add *__init__.py*. In this tutorial, we will use MyNewPlugin as the plugin name
 
2. Write a new python class under *broker/plugins/mynewplugin*
 
It must implement the methods *get_title*, *get_description*, *to_dict* and *execute*.
 
- **get_title(self)**
  - Returns plugin title
 
- **get_description(self)**
  - Returns plugin description
 
- **to_dict(self)**
  - Return a dict with the plugin information, name, title and description
 
- **execute(self, data)**
  - Actually execute the logic of cluster creation and job execution
  - Returns information if the execution was successful or not
    
### Example:

```
from broker.plugins import base

class MyNewPluginProvider(base.PluginInterface):

    def get_title(self):
        return 'My New Plugin'

    def get_description(self):
        return 'My New Plugin'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }

    def execute(self, data):
        return True
```
 
3. Add the new plugin to *setup.py* under entry_points:

```
    entry_points={
        'console_scripts': [
            'broker=broker.cli.main:main',
        ],
        'broker.execution.plugins': [
            'my_new_plugin=broker.plugins.my_new_plugin.plugin:MyNewPluginProvider',
        ],
```
 
4. Under *broker.cfg* add the plugin to the list of desired plugins:

```
[general]
plugins = plugin1,plugin2,my_new_plugin
```
 
Note: Make sure that the name matches under *setup.py* and the *broker.cfg* otherwise the plugin won’t be loaded.
