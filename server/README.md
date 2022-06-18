```
brew install zmq
export PKG_CONFIG_PATH=/usr/local/Cellar/zeromq/4.0.4/lib/pkgconfig/
sudo visudo

#add a linha:
Defaults env_keep += "PKG_CONFIG_PATH"

npm install
```