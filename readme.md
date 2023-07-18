# auto-arxiv
A simple tool to collect daily arxiv papers and write the content to a markdown file. The papers are sorted by the total score.

### Example Image
![example](./images/img.png)

### Settings in `config.yaml`
``` python
# subject_query: the subject of the papers you want to collect
#subject_query: 'cat:cs.RO OR cat:cs.AI OR cat:cs.ML'
subject_query: 'cat:cs.*'

# keyword_query: the keywords of the papers you want to collect, and give the keywords a weight (score)
keyword_query:
  a :
    keywords:
        - manipulation
        - robot
        - RL
    weight: 6

  b :
    keywords:
        - manipulation
        - RL
    weight: 5

  c:
    keywords:
        - manipulation
        - robot
    weight: 3

  d:
    keywords:
        - manipulation
        - robot
        - LLM
    weight: 4
  e:
    keywords:
        - manipulation
        - robot
        - VLM
    weight: 4
#  e:
#    keywords: 'LLM'
#    weight: 1
#  f:
#    keywords: 'VLM'
#    weight: 1
#  g:
#    keywords: 'vision-language'
#    weight: 1

```

### Tricks
- You can set the `days_before` to collect the papers in the past weekdays.
- You can set the `translator` to translate the title and abstract of the papers to your language (e.g. Chinese).
- The paper without keywords will be listed at the end of the markdown file. Though it doesn't include any keywords, it may be interesting to you.

### Thanks
- Carrier-Owl: https://github.com/fkubota/Carrier-Owl
- arxiv-py: https://github.com/lukasschwab/arxiv.py

