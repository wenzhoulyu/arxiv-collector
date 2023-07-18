import arxiv
import numpy as np
import datetime
from src.translate import TranslatorBase
from src.utils import get_previous_weekdays, check_multiple_strings


class Arxiv:
    def __init__(self, config: dir, translator: TranslatorBase):
        self.config = config
        self.translator = translator
        self.subject_query = self.config['subject_query']
        self.keyword_query = self.config['keyword_query']
        # self.keywords = self.config['keywords']
        # self.score_threshold = float(self.config['score_threshold'])
        self.today = datetime.datetime.now().strftime('%Y%m%d')
        self.week = datetime.datetime.now().weekday()
        self.published_date_str = None
    
    def search_arxiv(self, days_before: int, max_results: int) -> list:
        # Search the papers published in the last  'days_before' weekdays
        if days_before == 0:
            raise ValueError('variable days_before should be greater than 0')
        else:
            self.published_date_str = get_previous_weekdays(datetime.datetime.now(), days_before)[-1]
            keywords_query = ''
            logic = 'AND'
            for idx, key in enumerate(self.keyword_query.keys()):
                keywords = self.keyword_query[key]['keywords']
                if idx == 0:
                    logic = 'AND ('
                else:
                    logic = 'OR'
                if type(keywords) == str:
                    keywords_query += f' {logic} abs:{keywords}' if keywords.isupper() else f'{logic} abs:{keywords.lower()}'
                elif type(keywords) == list:
                    keywords_query += f' {logic} (abs:{keywords[0]}' if keywords[
                        0].isupper() else f'{logic} (abs:{keywords[0].lower()}'
                    for keyword in keywords[1:]:
                        keywords_query += f' AND abs:{keyword}' if keyword.isupper() else f' AND abs:{keyword.lower()}'
                    keywords_query += ') '
                else:
                    raise TypeError('variable keywords_query should be str or list')
            query = self.subject_query + ' ' + keywords_query + ' )'
            articles = arxiv.Search(query=query,
                                    max_results=max_results,
                                    sort_by=arxiv.SortCriterion.SubmittedDate,
                                    sort_order=arxiv.SortOrder.Descending,
                                    )
            results = self.search_keyword(articles)
            # 'abs:"semantic parsing" AND abs:"parsers"'
        return results
    
    def search_keyword(self, articles) -> list:
        final_year = self.published_date_str[:4]
        final_month = self.published_date_str[4:6]
        final_day = self.published_date_str[6:]
        today = datetime.datetime.now().strftime('%Y%m%d')
        today_year = today[:4]
        today_month = today[4:6]
        today_day = today[6:]
        results = [
            f"# {final_year}-{final_month}-{final_day} to {today_year}-{today_month}-{today_day} Paper List \n\n"]
        scores = []
        
        paper_id = 0
        
        for article in articles.results():
            published_date = article.published.strftime('%Y%m%d')
            if article.published is not None and published_date >= self.published_date_str:
                # print(f"Paper {paper_id + 1} : {article.title}")
                url = f'- _**url**_: {article.entry_id}' + '\n'
                title = f"{article.title}" + '\n'
                score, hit_keywords = self.calc_score(article.summary)
                # description = f'- _**Keywords**_: {" ".join(hit_keywords)}; _**Score**_: {score:.2f}' + '\n'
                if hit_keywords is not None:
                    description = f'- _**Keywords**_: {", ".join(hit_keywords)}' + '\n'
                else:
                    description = ''
                abstract_str = article.summary.replace('\n', ' ')
                abstract = f"- _**Abstract**_: {abstract_str} \n"
                scores.append(score)

                if self.translator is not None:
                    title_ch_str = self.translator.translate(article.title)
                    title_ch = f"{title} - _**标题**_: {title_ch_str}" + '\n'
                    abstract_ch_str = self.translator.translate(abstract_str)
                    abstract_ch = f"- _**摘要**_: {abstract_ch_str} \n"
                    print(title_ch_str)
                    results.append(f'{title}{description}{abstract}{title_ch}{abstract_ch}{url}\n\n')
                else:
                    results.append(f'{title}{description}{abstract}{url}\n\n')
                paper_id += 1
            
            else:
                break
        """ sorted by score """
        scores = np.array(scores)
        results = results[:1] + [f"## Paper {id + 1} : " + x for id, (_, x) in
                                 enumerate(sorted(zip(scores, results[1:]), reverse=True))]
        return results
    
    def calc_score(self, abstract: str) -> (float, list):
        scores = []
        hit_kwd_list = []
        # print(abstract)
        for key in self.keyword_query.keys():
            word = self.keyword_query[key]['keywords']
            score = self.keyword_query[key]['weight']
            if type(word) is list:
                if check_multiple_strings(abstract, word):
                    scores.append(score)
                    hit_kwd_list.append(word)
                else:
                    continue
            else:
                if word.isupper() and word in abstract:
                    scores.append(score)
                    hit_kwd_list.append(word)
                elif not word.isupper() and word.lower() in abstract.lower():
                    scores.append(score)
                    hit_kwd_list.append(word)
                else:
                    continue
        if len(hit_kwd_list) == 0:
            return 0, None
        else:
            idx = np.array(scores).argmax()
            return np.array(scores)[idx], hit_kwd_list[idx]
