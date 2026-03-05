"""API sub-clients."""

from camunda.api.decisions import DecisionsApi
from camunda.api.deployments import DeploymentsApi
from camunda.api.incidents import IncidentsApi
from camunda.api.jobs import JobsApi
from camunda.api.messages import MessagesApi
from camunda.api.processes import ProcessesApi
from camunda.api.signals import SignalsApi
from camunda.api.tasks import TasksApi
from camunda.api.topology import TopologyApi
from camunda.api.variables import VariablesApi

__all__ = [
    "DecisionsApi",
    "DeploymentsApi",
    "IncidentsApi",
    "JobsApi",
    "MessagesApi",
    "ProcessesApi",
    "SignalsApi",
    "TasksApi",
    "TopologyApi",
    "VariablesApi",
]
