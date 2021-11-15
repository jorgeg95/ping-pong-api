# Simple ping-pong web API with throttling feature and CLI tool

This repository contains a simple ping-pong web API (``planetly-code-challenge-server.py``) with a throttling feature. The WEB API exposes a ``/ping`` endpoint that requires a request with a payload: ``{"request":"ping"}`` and a header: ``x-secret-key: "random str"``.
The API is limited to a maximum of 10 ping requests per x-secret-key header and per minute. It is also limited to 2 ping requests per second regardless of the x-secret-key header.

The CLI tool (``planetly-code-challenge-client.py``) has as arguments the endpoint and network port for the WEB API. 
It sends 1 ping request per second to the ping endpoint of API.
Stops sending requests when the limit of allowed requests is reached and starts again when throttling is expired.

Both the WEB API and the CLI tool are written in python.

## Running WEB API on Docker container

* Download all repository files to a specific folder and "cd" into it.
* To build the Docker image, run the command: `` docker build -t <name_for_the_image> . ``
* To run a Docker container with the image created run the command: `` docker run --name <name_for_the_container> -d -p 8080:8080 <name_of_the_image>`` 
* After the above steps you can access the WEB API in the port 8080 of the host running Docker.

## Running the CLI tool
* To run the CLI tool you only need to have python3 installed on your machine.
* Run ``pip install requests``
* And run the command: ``<location_for_the_python_binary> planetly-code-challenge-client.py --endpoint <api_endpoint_IP_or_fqdn> --port <api_network_port>``

## Deploy on Kubernetes

You can use Kubernetes to more easily deploy, manage, automate and scale the WEB API if needed. 

Firstly, you will need to push your custom WEB API Docker image to a registry in order for Kubernetes nodes to pull it when deploying the container. By default kubernetes uses docker.io public registry.

To deploy the WEB API on Kubernetes you can simply use a deployment as shown in the example file ``kubernetes/deployment.yaml``. A deployment is used since this WEB API is stateless and the deployment will ensure that a minimum number of replicas, as configured, are up and running even in a case of failure such as a node being down. 

Apart from that it can be easily scaled to more replicas if needed to serve more client traffic. 
In order to scale automatically I suggest an Horizontal Pod Autoscaler (HPA) to be deployed as well. To do this, you simply need to run a command similar to the following example: ``
kubectl autoscale deployment ping-pong-api-deployment --cpu-percent=50 --min=1 --max=10
``. In this case, Kubernetes will create new replicas, to the maximum of 10 replicas, of the WEB API pod every time that the cpu load is above 50%. 
Note that different configurations for different metrics (for instance memory usage, number of requests, etc) can be configured using custom implementations of the autoscaler.

In order to reach the API you would also need a Kubernetes Service, since the Pod IP address is not static and can be different every time a new pod is deployed. Furthermore, the service provides Load-Balancing capabilities whenever more that one replica is running. An example of a simple ClusterIP service is shown in the file ``kubernetes/service.yaml``.

To reach the API from outside the cluster you would also need an Ingress. It is assumed that your cluster already has an Ingress Controller such as the widely used NGINX Ingress Controller. An example of a simple Ingress for the WEB API can be found in the file ``kubernetes/ingress.yaml``.

To monitor your WEB API there are different approaches that can be used:
* The simpler one is to use the Kubernetes API with kubectl commands such as ``kubectl get pods``, ``kubectl describe pod <name_of_the_pod>``, ``kubectl logs <name_of_the_pod>``. This approach is more useful for the deployment phase and to troubleshoot some possible problems that may occur when deploying the WEB API.
* To passively monitor your application, that is, to collect metrics for status and performance of the WEB API for example, there are multiple tools that can be integrated in the Kubernetes cluster. Kubernetes provides a simple service for collecting metrics called ``Kubernetes Metrics Server``. However, the most common tools for monitoring Kubernetes are Prometheus and Grafana, for collecting metrics and disply them using graphs and dashboards, respectively. They can be easily integrated with the cluster and collect metrics from the WEB API, such as CPU, MEM, network traffic, number of request and much more. With the metrics collected you can easily create dashboards to display the information and create alerts to be triggered and send an email, slack message or other notification when a metric value crosses a defined threshold.