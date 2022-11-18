from typing import Iterable, Mapping, Union
from meshed import DAG

SubDagSpec = Mapping[str, Iterable[Union[Iterable[str], str]]]


def split_dag(dag: DAG, sub_dag_spec: SubDagSpec):
    sub_dags = []
    for func_name, spec in sub_dag_spec.items():
        sub_dag = dag[spec]
        sub_dag.__name__ == func_name
        sub_dags.append(sub_dag)
    return sub_dags
