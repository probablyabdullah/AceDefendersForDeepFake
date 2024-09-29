from google_img_source_search import ReverseImageSearcher
import traceback
from aging import diff_finder

def reverse_image_search(file_path, article_url):
    print("Reverse image search begins....")
    rev_img_searcher = ReverseImageSearcher()
    try:
        output = rev_img_searcher.search_by_file(file_path)[:5]
        print(file_path)
        ages = []
        for result in output:
            date = diff_finder(article_url, result.page_url)
            if date > 0:
                ages.append(date)

        return ages
    except:
        print("error", file_path)
        traceback.print_exc()
        return []

if __name__ == "__main__":
    import pandas as pd 
    from util import download_image
    df = pd.read_excel("/home/capemox/Downloads/dataset_end_to_end.xlsx", sheet_name="Sheet1")
    out_df = pd.DataFrame()

    for i in range(len(df)):
        row = dict()
        if not pd.isna(df.top_image_url[i]):
            try:
                url = df.news_url[i]
                if not url.startswith("http"):
                    url = "http://" + url
                path, img_data = download_image(df.top_image_url[i])
                row["image_ages"] = reverse_image_search(path, url)
            except Exception as e:
                print(e)
                print(df.top_image_url[i])
                row["image_ages"] = []
        else:
            row["image_ages"] = []

        out_df = out_df._append(row, ignore_index=True, sort=False)
        out_df.to_csv("image_ages.csv", index=False)
    
