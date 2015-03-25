#-*-encoding=utf-8-*-
rule = (
        {
            "name": "cats",
            "type": "fetch",
            "from": {
                'http://shop.lenovo.com.cn/head.html': "//div[@class='ns_category-menu-content']/div/ul/li/a/@href",
            },
            "get": {
                "type": "simple",
                "method": "get",
                "parser": "lenovo.cats_parser", 
                },
            "dst": {
                "name": "lenovo_pager",
                "type": "list",
            }
        },
        {
            "type": "fetch",
            "name": "pager",
            "src": {
                "type": "list",
                "name": "lenovo_pager",
                "batch": 30,
                "filter": "lenovo.pager_filter"
            },
            "dst": {
                "type": "list",
                "name": "lenovo_list",
                },
            "get": {
                "type": "simple",
                "method": "get",
                "parser": "lenovo.pager",
                "args": {
                    "limit": 10,
                    "interval": 1,
                    "debug": False
                }
            }
        },
        {
            "type": "fetch",
            "name": "list",
            "src": {
                "type": "list",
                "name": "lenovo_list",
                "batch": 30,
                "filter": "lenovo.list_filter"
            },
            "dst": {
                "type": "list",
                "name": "lenovo_stock",
                },
            "get": {
                "type": "simple",
                "method": "get",
                "parser": "lenovo.list_parser",
                "args": {
                    "limit": 10,
                    "interval": 1,
                    "debug": False
                }
            }
        },
        {
            "name": "stock",
            "type": "fetch",
            "src": {
                "name": "lenovo_stock",
                "type": "list",
                "batch": 10,
                "group": True,
                "filter": "lenovo.stock_filter"
                },
            "get": {
                "method": "get",
                "parser": "lenovo.stock_parser",
                "args": { 
                    "limit": 5,
                    "interval": 2, 
                    "debug": False, 
                    "timeout": 10, 
                    }, 
                "not200": "log", 
                "randua": True
                },
            "dst": {
                "name": "spider_result",
                "type": "list",
                }
        }
)