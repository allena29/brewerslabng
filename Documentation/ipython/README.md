# Auto-complete of second-level objects (ipython 7.3.0)

Somewhere along the line ipython switched to using `jedi` as an autocomplete, however this isn't quite as nice for using the Voodoo Data Access to explore the configuration.

Copying `ipython_config.py` to `~/.ipython/profile_default/ipython_config.py` will disable jedi (and avoid the **Are you sure you want to exit** prompt)>

It is possible with ipython to setup multiple profiles and customise the configuration and select a specific profile when launching.


With jedi enabled tab completion works at the top level node only.

```
root.<tab>
# this gives a list of results

root.psychedelia.<tab>
# this does not give any results (incorrect)
# if we run dir(root.psychedelia) we see 'bands and pyschedlic rock' are answers.

tmp = root.psychedelia
tmp.<tab>
# shows the results.
```

Compare to with jedi disabled, both these options tab complete as expected.

```
root.<tab>
root.pschedelia.<tab>
```
