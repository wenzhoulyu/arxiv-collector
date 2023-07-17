# auto-arxiv
A simple tool to collect daily arxiv papers and write the content to a markdown file. The papers are sorted by the total score.

### Settings in `config.yaml`
``` python
# subject: the subject of the papers you want to collect
#subject: 'cat:cs.RO OR cat:cs.AI OR cat:cs.ML'
subject: 'cat:cs.*'

# keywords: the keywords of the papers you want to collect, and give the keywords a weight (score)
keywords:
        manipulation: 1
        vision-language: 1
        LLM: 1
        reinforcement learning: 3

# score_threshold: the threshold of the score, if the score of the paper is higher than the threshold, it will be collected
score_threshold: 2
```

### Thanks
- Carrier-Owl: https://github.com/fkubota/Carrier-Owl
- arxiv-py: https://github.com/lukasschwab/arxiv.py

