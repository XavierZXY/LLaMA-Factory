## cnvert alpaca to sharegpt

config the system prompt
```bash 
python tool/alpaca_to_sharegpt.py input output
```

## get the random test split
```bash
python tool/train_split.py -m random -r 0.1 -o output
```

## rewrite the test split
```bash
python tool/rewrite/rewrite_instruction.py
```