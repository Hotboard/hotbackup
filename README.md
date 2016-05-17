# Hotboard Backup!

A simple utility to save backups to Amazon S3. Currently in initial development...



## Dependencies

* [Python 3](https://www.python.org/)
* [boto3](https://github.com/boto/boto3)
* [click](http://click.pocoo.org/5/)
* [PyYaml](http://pyyaml.org/wiki/PyYAMLDocumentation)
* [simple-crypt](https://github.com/andrewcooke/simple-crypt)



## Installation for developers (w/ venv)

```bash
git clone https://github.com/Hotboard/hotbackup.git
cd hotbackup
python3 -m venv <venv>
source <venv>/bin/activate
pip install --editable .
```



## Help for current functionality

```python
hotbackup --help

Usage: hotbackup [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug  In debug mode all log messages are shown.
  --help                Show this message and exit.

Commands:
  backup     Backup a file to Amazon AWS S3.
  configure  Amazon AWS Configuration.
  list       List all files in the default S3 Bucket.
```



## Configuring AWS credentials

Before using the app you will need to configure it. Simply invoke

```python
hotbackup configure
```



## Usage

Currently in initial development the application is still very limited but you can already perfom the following actions.


### List available files

Lists the files in the default configured S3 Bucket

```python
hotbackup list
```


### Backup a file

To simply upload a file to the default configured bucket just invoke.

```python
hotbackup backup filetobackup.tmp
```

To encrypt and upload a file to the default configured bucket you will need to provide a password.

```python
hotbackup backup filetobackup.tmp --password mypass
```


### Restore a file

To restore an encrypted file

```python
hotbackup restore filetorestore.enc --password mypass
```

To restore an plain text file

```python
hotbackup restore filetorestore.txt
```



## Bugs

Please log your bugs on the "[Github issues tracker](https://github.com/Hotboard/hotbackup/issues)"



## License

MIT.


