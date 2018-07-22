# bird_finder
Finds links to Twitter accounts in web pages.

This is useful for creating lists of Twitter accounts for
collecting.

## Installation
    git clone https://github.com/justinlittman/bird_finder.git
    pip install requests-html
        
## Usage

    python bird_finder.py -h
    usage: bird_finder.py [-h] [--output OUTPUT] [--ask] {page,pages} ...
    
    Finds Twitter accounts in web pages.
    
    positional arguments:
      {page,pages}
    
    optional arguments:
      -h, --help       show this help message and exit
      --output OUTPUT  filename of csv output
      --ask            ask about each twitter link
          
For example:

    python bird_finder.py --ask --output news_accounts.csv pages news_urls.txt