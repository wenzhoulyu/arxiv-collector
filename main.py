import os
import yaml
import argparse
import warnings
import arxiv
import numpy as np
import datetime

warnings.filterwarnings('ignore')


def calc_score(abst: str, keywords: dict) -> (float, list):
    sum_score = 0.0
    hit_kwd_list = []
    
    for word in keywords.keys():
        score = keywords[word]
        if word.lower() in abst.lower():
            sum_score += score
            hit_kwd_list.append(word)
    return sum_score, hit_kwd_list


def search_keyword(
        articles, keywords: dict, score_threshold: float, today: str
) -> list:
    year = today[:4]
    month = today[4:6]
    day = today[6:]
    results = [f"# {year}-{month}-{day} Paper List \n\n"]
    scores = []
    
    paper_id = 0
    
    for article in articles.results():
        published_date = article.published.strftime('%Y%m%d')
        if article.published is not None and today == published_date:
            url = f'- _**url**_: {article.entry_id}' + '\n'
            title = f"{article.title}" + '\n'
            score, hit_keywords = calc_score(article.summary, keywords)
            # description = f'- _**Keywords**_: {" ".join(hit_keywords)}; _**Score**_: {score:.2f}' + '\n'
            description = f'- _**Keywords**_: {", ".join(hit_keywords)}' + '\n'
            abstract_str = article.summary.replace('\n', ' ')
            abstract = f"- _**Abstract**_: {abstract_str} \n"
            if (score != 0) and (score >= score_threshold):
                scores.append(score)
                results.append(f'{title}{description}{abstract}{url}\n\n')
                paper_id += 1
        else:
            break
    """ sorted by score """
    scores = np.array(scores)
    results = results[:1] + [f"## Paper {id + 1} : " + x for id, (_, x) in
                             enumerate(sorted(zip(scores, results[1:]), reverse=True))]
    return results


def get_config() -> dict:
    file_abs_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_abs_path)
    config_path = f'{file_dir}/config.yaml'
    with open(config_path, 'rb') as yml:
        config = yaml.load(yml, Loader=yaml.SafeLoader)
    return config


def main():
    config = get_config()
    subject = config['subject']
    keywords = config['keywords']
    score_threshold = float(config['score_threshold'])
    
    week = datetime.datetime.now().weekday()
    
    if week >= 5:
        published_date_str = None
    elif week == 0:
        time = datetime.datetime.now()
        published_date = time - datetime.timedelta(days=3)
        published_date_str = published_date.strftime('%Y%m%d')
    else:
        time = datetime.datetime.now()
        published_date = time - datetime.timedelta(days=1)
        published_date_str = published_date.strftime('%Y%m%d')
    if published_date_str is None:
        print(f"Today is {week + 1}th day of week. So, I don't send message.")
        pass
    else:
        arxiv_query = subject
        
        articles = arxiv.Search(query=arxiv_query,
                                max_results=500,
                                sort_by=arxiv.SortCriterion.SubmittedDate,
                                sort_order=arxiv.SortOrder.Descending)
        results = search_keyword(articles, keywords, score_threshold, published_date_str)
        
        with open(fr'.\daily-paper\{published_date_str}.md', 'w') as f:
            for result in results:
                f.write(result)
            f.close()
        print(f"I've collected the {published_date_str} published papers.")


if __name__ == "__main__":
    main()
