card_template = {
    "schema": "2.0",
    "config": {
        "update_multi": True,
        "style": {
            "text_size": {
                "normal_v2": {
                    "default": "normal",
                    "pc": "normal",
                    "mobile": "heading",
                }
            }
        },
    },
    "body": {
        "direction": "vertical",
        "padding": "12px 12px 12px 12px",
        "elements": [
            {
                "tag": "markdown",
                "content": "<font color='grey'>当前模型：{model}</font>",
                "text_align": "left",
                "text_size": "notation",
                "margin": "0px 0px 0px 0px",
            },
            {"tag": "hr", "margin": "0px 0px 0px 0px"},
            {
                "tag": "markdown",
                "content": "**当前进度**",
                "text_align": "left",
                "text_size": "heading",
                "margin": "0px 0px 0px 0px",
            },
        ],
    },
    "header": {
        "title": {"tag": "plain_text", "content": "🚧 已收到你的分析请求"},
        "subtitle": {"tag": "plain_text", "content": ""},
        "template": "blue",
        "padding": "12px 12px 12px 12px",
    },
}
