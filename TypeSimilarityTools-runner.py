import click
from src.TypeSimilarityTools import TypeSimilarityTools


@click.command()
@click.option('--type1', '-t1', default=None)
@click.option('--type2', '-t2', default=None)
@click.option('--force', '-f', default=False)
@click.option('--server', '-s', default="http://localhost:8585/bigdata/sparql",
              help='Uri to the sparql endpoint which stores the RDFS SubClass Information.')
@click.option('--user', '-u', default="admin", help='User for the sparql endpoint.')
@click.option('--password', '-p', default="dev98912011", help='Password for the sparql endpoint.')
@click.option('--n-processes', '-x', default="11",
              help='Number of processes to spawn simultaneously.')
@click.option('--log-level', '-l', default="WARN")
def main(server, user, password, type1, type2, force, log_level, n_processes):
    if type1 is None or type2 is None:
        return 2
    similarity_tool = TypeSimilarityTools(server=server, user=user, password=password, n_processes=int(n_processes),
                                   log_level=log_level)
    similarity_tool.get_type_similarity(type1, type2, force_calc=force)


if __name__ == '__main__':
    main()
