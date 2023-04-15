# mrc-generator
Generate `.mrc` files from plain text files

## Example source file
```
ftp 235
z1 30
z2 65
z3 83
z4 98
z5 113
z6 135
z7 200
-----------
5:00 z1
5x {
    0:30 z2
    1:00 z3
    2x {
        0:15 z5
        0:15 150%
    }
    3x {
        0:20 100w
        1:00 59
    }
}
```
