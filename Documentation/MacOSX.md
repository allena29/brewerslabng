# pyenv on MaxOSX

### Obtain pyenv/virtualenv
```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
PATH=~/.pyenv/bin:$PATH
eval "$(pyenv init -)"
export PYENV_ROOT="$HOME/.pyenv"
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv

cat <<'EOF' >> ~/.bashrc
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF
```


```
export LDFLAGS="${LDFLAGS} -L/usr/local/opt/zlib/lib"
export CPPFLAGS="${CPPFLAGS} -I/usr/local/opt/zlib/include"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH} /usr/local/opt/zlib/lib/pkgconfig"
export PYTHON_CONFIGURE_OPTS="--enable-framework"
pyenv install 3.6.5
eval "$(pyenv virtualenv-init -)"
pyenv virtualenv 3.6.5 brewerslabng
pip install -r requirements.lock
```



# Install sysrepo on MacOSX

Tested with Mojave 10.14.3

### Install Dependencies

```
brew install cmake # 3.14.3
brew install protobuf-c # 1.3.1.2
brew install libev # 4.24
brew install pcre # 8.43


swig-3.0.12 # from source

libyang # from source - tag v1.0-r2
libredblack # from source - commit id #a399310d99b61eec4d3c0677573ab5dddcf9395d
LIBYANG_INSTALL=system pip install libyang
```


### Sysrepo

If using pyenv then the following change is required to force the use of the pyenv version of python rather than what might be found in the system path from homebrew.

```diff
diff --git a/swig/CMakeLists.txt b/swig/CMakeLists.txt
index 50121d8c..235ec2d1 100644
--- a/swig/CMakeLists.txt
+++ b/swig/CMakeLists.txt
@@ -46,10 +46,10 @@ endif()
 # find Python package
 if(GEN_PYTHON_BINDINGS AND SWIG_FOUND)
     message(STATUS "Python version ${GEN_PYTHON_VERSION} was selected")
-    unset(PYTHON_LIBRARY CACHE)
-    unset(PYTHON_EXECUTABLE CACHE)
-    unset(PYTHON_INCLUDE_DIR CACHE)
-    unset(PYTHON_LIBRARY_DEBUG CACHE)
+    #unset(PYTHON_LIBRARY CACHE)
+    #unset(PYTHON_EXECUTABLE CACHE)
+    #unset(PYTHON_INCLUDE_DIR CACHE)
+    #unset(PYTHON_LIBRARY_DEBUG CACHE)
     if(${GEN_PYTHON_VERSION} STREQUAL "2")
         find_package(PythonLibs 2)
         find_package(PythonInterp)
```


```bash
cmake -DPYTHON_EXECUTABLE=/Users/adam/.pyenv/versions/brewerslabng/bin/python3  -DPYTHON_LIBRARY=/Users/adam/.pyenv/versions/3.6.5/lib/libpython3.6.dylib  -DPYTHON_INCLUDE_DIR=/Users/adam/.pyenv/versions/3.6.5/include/python3.6m  -DCMAKE_BUILD_TYPE=Debug -DBUILD_EXAMPLES=1 -DGEN_LUA_BINDINGS=0 -DREPOSITORY_LOC=/sysrepo -DGEN_PYTHON_VERSION=3 ..
make && cd make
sudo make install
```

# Netopeer/libnetconf/libssh

These are not designed to work on MacOSX see - https://travis-ci.org/CESNET/libnetconf2/jobs/388021303
