import os
import yaml
import warnings
from src.arxiv_search import Arxiv
from src.translate import YouDao, Google

warnings.filterwarnings('ignore')


def get_config() -> dict:
    file_abs_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_abs_path)
    config_path = f'{file_dir}/config.yaml'
    with open(config_path, 'rb') as yml:
        config = yaml.load(yml, Loader=yaml.SafeLoader)
    return config


def main():
    days_before = 1
    config = get_config()
    translator = Google()  #
    arxiv_agent = Arxiv(config=config, translator=translator)
    results, num_papers = arxiv_agent.search_arxiv(days_before=days_before, max_results=500)
    published_date_str = arxiv_agent.today
    # with open(fr'.\daily-paper\{published_date_str}-pre-{days_before}days.md', 'w', encoding='utf-8') as f:
    with open(fr'.\daily-paper\{published_date_str}-pre-{days_before}days.md', 'w', encoding='utf-8') as f:
        for result in results:
            f.write(result)
        f.close()
    print(f"I've collected the previous {days_before} weekdays total {num_papers} published papers.")


if __name__ == "__main__":
    main()
