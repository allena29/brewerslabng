# Notes:


`~/.atomenv` is`dot-atom-evn`


#### Disable pyenv

Install the python extnesions we need as root system wide, individual proejcts can still use pyenv.

```
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
pip install -r requirements.lock
```


#### MAC (Workaround)

Under the very first <dict> force the path

```
    <key>LSEnvironment</key>
    <dict>
      <key>PATH</key>
      <string>/Users/adam/.atomenv:/opt/ncs/current/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
```



### Wrapper for running scripts.

Before the buffer process in `~/.atom/packages/scripts/lib/runner.js` we have hardecoded to always run our wrapper script.

If it returns a non-zero exit code a failure has occured.

Using the python script we can derrive what we want to run and use python subprocess to call bash with a login prompt to nicely run the file.

```
   23   run(command, extraArgs, codeContext, inputString = null) {
   
   35     command = "/Users/adam/.atomenv/wrapper";
   
   39     this.bufferedProcess = new BufferedProcess({
   
```

     