from mgost.context import Context


def post_process(context: Context) -> None:
    for name, oxml in context.post_process_links.items():
        try:
            bookmark_name = context.counters.bookmarks[name]
        except KeyError:
            raise KeyError(
                f"Вы пытаетесь сослаться на {name}"
                f", однако такой цели не существует. Возможные названия: "
                f""
            ) from None
        oxml.set('w:name', bookmark_name)
