# apidoc2runner


Convert apidoc data to JSON testcases for HttpRunner.

## apidoc规范
[apidoc2runner规范](http://apidoc.b9bb.cn/)

## usage

To see ``apidoc2runner`` version:

```shell
$ python main.py -V
```

To see available options, run

```shell
$ python main.py -h
usage: main.py [-h] [-V] [--log-level LOG_LEVEL]
               [apidoc_testset_file] [-- output_dir] [-- output_file_type]

Convert apidoc testcases to JSON testcases for HttpRunner.

positional arguments:
  apidoc_testset_file  Specify apidoc testset file.
  -- output_dir   Optional. Specify converted JSON testset folder.
  -- output_file_type  Optional. Generate file format , default json.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show version
  --log-level LOG_LEVEL Specify logging level, default is INFO.
```

## examples

In most cases, you can run ``apidoc2runner`` like this:

```shell
$ python3 main.py tests/data/test.json --output_dir tests/apidoc2runner --output_file_type yaml
INFO:root:Generate JSON testset successfully: output.json
```

As you see, the first parameter is apidoc source file path, and the second is converted JSON file path.

The output testset file type is detemined by the suffix of your specified file.

If you only specify apidoc source file path, the output testset is in JSON format by default and located in the same folder with source file.

```shell
$ python3 main.py tests/data/test.json
INFO:root:Generate JSON testset successfully: test/test.output.json
```

## generated testset

generated JSON testset ``output.json`` shows like this:

```json
[
    {
        "test": {
            "name": "/api/v1/Account/Login",
            "request": {
                "method": "POST",
                "url": "https://httprunner.top/api/v1/Account/Login",
                "headers": {
                    "Content-Type": "application/json"
                },
                "json": {
                    "UserName": "test001",
                    "Pwd": "123",
                    "VerCode": ""
                }
            },
            "validate": []
        }
    }
]
```

## 参考来源
【[HttpRunner](https://github.com/HttpRunner/apidoc2case)】

