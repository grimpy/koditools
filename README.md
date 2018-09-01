# Kodi Tools

This contains some tools to play with Kodi written in python

## kodiremote

A CLI tool to control Kodi
Uses keyboard to control Kodi all keys will be sent as is to Kodi and will be passed trough keymaps.xml
Exceptions are the arrows keys which will be used for navigation.

### Config ~/.config/koditools/remote.conf

Used to configure shortcuts to actions http://kodi.wiki/view/Action_IDs
Or remap keys to others or configure macros http://kodi.wiki/view/Keymap

The config file should have a section called keybindings.
The key represents the key you want to bind (either numeric acsii value or the character itself or KEY_CHARACTER (can be used for numbers)).
The value should be a json string containing the action that should be performmed


```ini
[keybindings]  
f = {"action": "ActivateWindow(favourite)"} # map f key to open favourites  
v = {"key": "m"} # remap key v to m  

[server]
host = 192.168.1.3
port = 8080

[plugin.tv]
class = lgtv.TV
args = ["192.168.1.252"]
```


## kodipidgin

Forwards message from pidgin to the notification system of Kodi
