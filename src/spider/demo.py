# simulate_mysql_terminal.py

def simulate_mysql_terminal():
    lines = [
        "$ mysql -u root -p",
        "Enter password: ****",
        "mysql> USE wb;",
        "Database changed",
        "",
        "mysql> SELECT COUNT(*) AS `微博文章 (article)` FROM article;",
        "+-----------------------+",
        "| 微博文章 (article)    |",
        "+-----------------------+",
        "|                  5000 |",
        "+-----------------------+",
        "1 row in set (0.00 sec)",
        "",
        "mysql> SELECT COUNT(*) AS `相关评论 (comments)` FROM comments;",
        "+-------------------------+",
        "| 相关评论 (comments)     |",
        "+-------------------------+",
        "|                 25000   |",
        "+-------------------------+",
        "1 row in set (0.00 sec)",
        "",
        "mysql> SELECT",
        "    ->   (SELECT COUNT(*) FROM article) AS `微博文章 (article)`,",
        "    ->   (SELECT COUNT(*) FROM comments) AS `相关评论 (comments)`;",
        "+-----------------------+-------------------------+",
        "| 微博文章 (article)    | 相关评论 (comments)     |",
        "+-----------------------+-------------------------+",
        "|                  5000 |                   25000 |",
        "+-----------------------+-------------------------+",
        "1 row in set (0.00 sec)",
    ]
    for line in lines:
        print(line)

if __name__ == "__main__":
    simulate_mysql_terminal()
