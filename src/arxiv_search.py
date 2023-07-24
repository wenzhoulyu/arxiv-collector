import arxiv
import numpy as np
import datetime
from src.translate import TranslatorBase
from src.utils import get_previous_weekdays, check_multiple_strings
from itertools import product


class Arxiv:
    def __init__(self, config: dir, translator: TranslatorBase, days_type: str = 'weekdays', file_dir: str = None,
                 strict: bool = True):
        self.config = config
        self.translator = translator
        self.subject_query = self.config['subject_query']
        self.keyword_query = self.config['keyword_query']
        self.today = datetime.datetime.now().strftime('%Y%m%d')
        self.week = datetime.datetime.now().weekday()
        self.published_date_str = None
        self.days_type = days_type
        self.file_dir = file_dir
        self.strict = strict
        self.keywords_list = self.preprocess_keywords_query(self.keyword_query)
        self.keywords_pair = list(product(*keywords) for keywords in self.keywords_list)
        for idx, keywords in enumerate(self.keywords_pair):
            self.keywords_pair[idx] = list(keywords)
        # self.weight_dict = self.preprocess_weights_query(self.keyword_query, self.keywords_pair)
        self.weights_list = self.preprocess_weights_query(self.keyword_query, self.keywords_pair)
    
    def search_arxiv(self, days_before: int, max_results: int) -> (list, int):
        # Search the papers published in the last  'days_before' weekdays
        if days_before == 0:
            raise ValueError('variable days_before should be greater than 0')
        else:
            self.published_date_str = self.calc_days(days_before)
            keywords_query = ''
            logic = 'AND'
            
            for idx, keywords_list in enumerate(self.keywords_pair):
                for tmp,keywords in enumerate(keywords_list):
                    if idx == 0 and tmp == 0:
                        logic = 'AND ('
                    elif idx == 0:
                        logic = 'OR'
                    if type(keywords) == tuple:
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
                                    # sort_by=arxiv.SortCriterion.SubmittedDate,
                                    sort_by=arxiv.SortCriterion.LastUpdatedDate,
                                    # sort_by=arxiv.SortCriterion.Relevance,
                                    sort_order=arxiv.SortOrder.Descending,
                                    )
            # results = [result for result in articles.results()]
            # paper_list = self.download_pdf(results)
            results, num_papers = self.search_keyword(articles)
        return results, num_papers
    
    def search_keyword(self, articles) -> (list, int):
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
        update_date = []
        paper_id = 0
        
        for article in articles.results():
            # published_date = article.published.strftime('%Y%m%d')
            try:
                published_date = article.updated.strftime('%Y%m%d')
            except:
                published_date = None
            if published_date is not None and published_date >= self.published_date_str:
                print(f"Paper {paper_id + 1} : {article.title}")
                url = f'- _**url**_: {article.entry_id}' + '\n'
                published_date_str = article.updated.strftime('%Y-%m-%d')
                # published_date_str = f'- _**Published Date**_: {published_date_str}' + '\n'
                published_date_str = f'- _**Updated Date**_: {published_date_str}' + '\n'
                title = f"{article.title}" + '\n'
                comment = f'- _**Comment**_: {article.comment}' + '\n'
                score, hit_keywords = self.calc_score(article.summary)
                update_date.append(article.updated)
                print(f"Score: {score:.2f}, Keywords: {hit_keywords}")
                # exit()
                if self.strict and hit_keywords is None:
                    continue
                else:
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
                        title_ch = f"- _**标题**_: {title_ch_str}" + '\n'
                        abstract_ch_str = self.translator.translate(abstract_str)
                        abstract_ch = f"- _**摘要**_: {abstract_ch_str} \n"
                        results.append(
                            f'{title}{description}{published_date_str}{comment}{abstract}{title_ch}{abstract_ch}{url}\n\n')
                    else:
                        results.append(f'{title}{description}{published_date_str}{comment}{abstract}{url}\n\n')
                    paper_id += 1
            else:
                break
                # continue
        """ sorted by score """
        scores = np.array(scores)
        # scores = np.array(scores)
        # results = results[:1] + [f"## Paper {id + 1} : " + x for id, (_, x) in
        #                          enumerate(sorted(zip(scores, results[1:]), reverse=True))]
        results = results[:1] + [f"## Paper {id + 1} : " + x for id, (_, x) in
                                 enumerate(sorted(zip(update_date, results[1:]), reverse=False))]  # False 升序排列
        return results, len(np.array(scores))
    
    def calc_score(self, abstract: str) -> (float, list):
        scores = []
        hit_kwd_list = []
        keywords_pair = self.keywords_pair
        for idx, keywords_list in enumerate(keywords_pair):
            score = self.weights_list[idx]
            for keywords in keywords_list:
                if check_multiple_strings(abstract, list(keywords)):
                    scores.append(score)
                    hit_kwd_list.extend(list(keywords))
                else:
                    pass
        if len(hit_kwd_list) == 0:
            return 0, None
        else:
            return np.array(scores).mean(), list(set(hit_kwd_list))
    
    def calc_days(self, days_before: int) -> (int, int):
        if self.days_type == 'weekdays':
            return get_previous_weekdays(datetime.datetime.now(), days_before)[-1]
        elif self.days_type == 'normal':
            return (datetime.datetime.now() - datetime.timedelta(days=days_before)).strftime('%Y%m%d')
        else:
            raise ValueError('days_type should be weekdays or normal')
    
    def filter_keyword(self, search, filter_keys, filter_results):
        for index, result in enumerate(search.results()):
            abs_text = result.summary.replace('-\n', '-').replace('\n', ' ')
            meet_num = 0
            for f_key in filter_keys.split(" "):
                if f_key.lower() in abs_text.lower():
                    meet_num += 1
            if meet_num == len(filter_keys.split(" ")):
                filter_results.append(result)
    
    @staticmethod
    def preprocess_keywords_query(keywords_query):
        def preprocess_keywords(keywords_origin):
            keyword_list_tmp = []
            for i, keywords in enumerate(keywords_origin):
                sub_keyword_list = keywords.split(',')
                sub_keyword_list = [keyword.strip() for keyword in sub_keyword_list]
                keyword_list_tmp.append(sub_keyword_list)
                # print(f"keywords_list: {sub_keyword_list}")
            return keyword_list_tmp
        
        keywords_list = []
        for keys in keywords_query.keys():
            sub_keywords = keywords_query[keys]['keywords']
            keywords_list.append(preprocess_keywords(sub_keywords))
        return keywords_list
    
    @staticmethod
    def preprocess_weights_query(keywords_query, keywords_list):
        weights_list = []
        for keys in keywords_query.keys():
            sub_weights = keywords_query[keys]['weight']
            weights_list.append(sub_weights)
        return weights_list
