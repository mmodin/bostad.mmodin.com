import pandas as pd


def html_table(df):
    # Replace id column with url
    df['id'] = df['id'].apply(lambda x: '<a href="https://bostad.stockholm.se/Lista/details?aid={0}">{0}</a>'.format(x))

    # Set display options to enable long URLs
    pd.set_option('display.max_colwidth', -1)

    # Replace formatting options that come with to_html()
    html_str = df.to_html(escape=False)\
        .replace('\n', '')\
        .replace('<table border=\"1\" class=\"dataframe\">', '')\
        .replace('</table>', '')
    return html_str
