from logging import getLogger

from mgost.context import Context

logger = getLogger(__name__)


def post_process(context: Context) -> None:
    for name, oxml in context.post_process_links.items():
        try:
            bookmark_name = context.counters.bookmarks[name]
        except KeyError:
            logger.info(
                f"Вы пытаетесь сослаться на {name[:30]}"
                f", однако такой цели не существует. Возможные названия: "
                f"{', '.join([i for i in context.counters.bookmarks.keys()])}"
            )
            return
        oxml.set('w:name', bookmark_name)
