# TraceMe

`TraceMe` is a performance debugging or monitoring tool for a C/C++ program. It measures each of function's duration and helps to figure out a cause of problem.

`Uprobe` , which can place probes into user-space programs, is a key facility of `TraceMe`. It tries to put a small code before and after of a function which is wanted to be traced and extracts duration of it.

Note that `TraceMe` is currently experimental stage. Because of that, it requires lot of dependency. Need heavy changes to reach production level.



### Requirements

Needs following things:

* Linux v3.15 or above (for uprobe)
* Kernel configuration
  * CONFIG_UPROBE_EVENTS
  * CONFIG_FTRACE
* perf
  * Currently `TraceMe` calls perf directly because of fast implementation.
* trace-cmd
* python3




### How to use it?

##### Command format

```bash
traceme.py [add|record|parse|list] OPTIONS
```



1. Register probes

  ```bash
  sudo traceme.py add -f BINARY -a
  ```

2. Collect traces
  sudo trace-cmd record -e "probe_*" EXECUTABLE

3. Get report
  trace-cmd report | vtrace_reg_funcs.py parse [-o OUTPUT.json]

4. Open on chrome](http://vtrace_reg_funcs.py/) add -f BINARY [-l FUNC_LIST_FILE]

5. Collect traces

  ```bash
  sudo trace-cmd record -e "probe_*" EXECUTABLE
  ```

6. Parse data into a format of report

  ```bash
  sudo trace-cmd report | vtrace_reg_funcs.py parse [-o OUTPUT.json]
  ```

7. Open the report file on chrome browser

   * chrome://tracing

chrome://tracing