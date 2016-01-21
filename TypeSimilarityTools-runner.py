import click
from src.TypeSimilarityTool import TypeSimilarityTool
from datetime import datetime


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
@click.option('--similarity-store', '-ss', default="data/similarities.db")
@click.option('--instance-count-store', '-ics', default="data/instance_count.db")
def main(server, user, password, type1, type2, force, log_level, n_processes, similarity_store, instance_count_store):
    if type1 is None or type2 is None:
        return 2
    similarity_tool = TypeSimilarityTool(server=server, user=user, password=password, n_processes=int(n_processes),
                                   log_level=log_level, similarity_store=similarity_store, instance_count_store=instance_count_store)
    cur_time = datetime.now()
    print("Similarity for '{}' and '{}': {}".format(type1, type2, similarity_tool.get_type_similarity(type1, type2, force_calc=force)))
    print("Time : {}".format(datetime.now() - cur_time))


if __name__ == '__main__':
    main()
