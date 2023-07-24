import os
import yaml
import warnings
from src.arxiv_search import Arxiv
from src.translate import YouDao, Google
import argparse

warnings.filterwarnings('ignore')


def get_config() -> dict:
    file_abs_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_abs_path)
    config_path = f'{file_dir}/config.yaml'
    with open(config_path, 'rb') as yml:
        config = yaml.load(yml, Loader=yaml.SafeLoader)
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days-before', type=int, default=7, help='number of normal days before today')
    parser.add_argument('--strict', type=bool, default=True,
                        help='strict means that the keywords must be in the abstract')
    parser.add_argument('--max-results', type=int, default=5000, help='max results for arXiv search')
    args = parser.parse_args()
    config = get_config()
    translator = Google()  #
    # translator = None
    file_dir = '.\daily-paper/files_pdf'
    if args.strict:
        print(f"Searching {args.days_before} normal days before today papers in strict mode...")
    else:
        print(f"Searching papers {args.days_before} normal days before today in normal mode...")
    arxiv_agent = Arxiv(config=config, translator=translator, days_type='normal', file_dir=file_dir, strict=args.strict)
    # results, num_papers = arxiv_agent.search_arxiv(days_before=days_before, max_results=80000)
    results, num_papers = arxiv_agent.search_arxiv(days_before=args.days_before, max_results=args.max_results)
    published_date_str = arxiv_agent.today
    # with open(fr'.\daily-paper\{published_date_str}-pre-{days_before}days.md', 'w', encoding='utf-8') as f:
    if args.strict:
        path = fr'.\daily-paper\{published_date_str}-pre-{args.days_before}days-strict.md'
    else:
        path = fr'.\daily-paper\{published_date_str}-pre-{args.days_before}days.md'
    with open(path, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(result)
        f.close()
    print(f"I've collected the previous {args.days_before} normal days total {num_papers} published papers.")


if __name__ == "__main__":
    main()
