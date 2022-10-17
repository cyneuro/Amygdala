# Amygdala Repository 

Maintained by [Tyler Banks](https://github.com/tjbanks) and [Greg Glickert](https://github.com/GregGlickert)


Before running in a network folder, install the core code.
```
cd amygdala_core
python setup.py develop
```

## Network Base

This repository contains a set of core components to build Amygdala models.

| Folder                    | Purpose |
|-------------------------------|---------|
| **[`amygdala`](./amygdala)**         | Core code that will need to be installed before running networks|
| **[`components`](./components)**         | network components shared by all built networks|

## Networks

Each network is contained in its own directory.

| Network                    | Description | Maintainer
|-------------------------------|---------|------|
| **[`theta_network`](./theta_network)**         | Generate theta rhythms using PNa, PNc, Int, SOM and CR cells | [@tjbanks](https://github.com/tjbanks)|
| **[`tone_network`](./components)**         | tone and shock network| [@GregGlickert](https://github.com/GregGlickert)|
