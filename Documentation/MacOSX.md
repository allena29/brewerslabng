# Install sysrepo on MacOSX

```
brew install cmake # 3.14.3

brew install protobuf-c # 1.3.1.2

brew install libev # 4.24

brew install pcre # 8.43


swig-3.0.12 # from source

libyang # from source - tag v1.0-r2
libredblack # from source - commit id #a399310d99b61eec4d3c0677573ab5dddcf9395d
sysrepo $ from source tag v0.7.7
  - cmake -DREPOSITORY_LOC=/sysrepo -DGEN_PYTHON_VERSION=3 -DGEN_LUA_BINDINGS=0 ..

LIBYANG_INSTALL=system pip install libyang
```


Note: virtualenv can make life a little bit harder, because the build process for sysrepo picks up the system version of python (brew install) not the virtualenv version.

Unfortunately it just doesn't seem to work, even though the sysrepo was compiled with pyenv activated.

```
Python 3.7.3 (default, Apr 11 2019, 22:14:31)
[Clang 10.0.0 (clang-1000.10.44.4)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import sysrepo
fish: 'python3' terminated by signal SIGSEGV (Address boundary error)
[I] git:master ~/brewersl/sysrepo/build $
```

# Netopeer/libnetconf/libssh

These are not designed to work on MacOSX
