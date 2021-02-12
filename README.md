# Galois PyToolkit

In-development Python clients for Cryptol and SAW.

The Cryptol client depends on the [cryptol-remote-api](https://github.com/galoisinc/cryptol) server.

The SAW client depends on the [saw-remote-api](https://github.com/GaloisInc/saw-script) server.

If both servers are in your path and you have installed the Python dependencies, you should be able to run the unit tests as follows:

```
$ python3 -m unittest discover tests/cryptol
$ python3 -m unittest discover tests/saw
```
