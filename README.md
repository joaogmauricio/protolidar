# protolidar 
> (JS) Prototype Pollution Scanner

Scans for potentially dangerous code patterns that may lead to prototype pollution vulnerabilities. As it doesn't scan for recursive merges, clones or property definition by path patterns, one may argue that this may have a pretty limited scope (like `obj[n][m]([p])* = val`); however, you'd be surprised by how often such kind of instructions come up.

## Usage

```
usage: scanner.py [-h] [-s] [-p {0,1,2}] (-d DIRECTORY | -u URL_GIT)

Prototype Pollution Code Scanner

optional arguments:
  -h, --help            show this help message and exit
  -s, --non-recursive   simply examine the target directory, without recursivity
  -p {0,1,2}, --pickiness {0,1,2}
                        sets 'pickiness' level (how strict the scan patters are)
  -d DIRECTORY, --directory DIRECTORY
                        target directory
  -u URL_GIT, --url-git URL_GIT
                        target git repo
```  

## Contributions

Feel free to contribute, especially with new or improved regexes.

## Why 'lidar'?

Do you know any better pollution type of scanner!? ;)
