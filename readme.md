# shell_gf

## getting started

0. env

``` bash
cp .env.example .env
vim .env
```

1. resolve dep

``` bash
cd shell_gf
pip install -r requirements
```

2. run

``` bash
python index.py
```


# agi

0. fc called with `query` n `epoch`
1. questioning
2. call fc in subprocess(es)
3. resolve 
4. human feedback from single str input
5. store to vector database for long-term memorization
6. loop till epoch
7. summarize
