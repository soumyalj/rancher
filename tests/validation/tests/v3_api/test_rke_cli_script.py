import os
from lib.aws import AmazonWebServices
from .common import *  # NOQA
RANCHER_CLEANUP_CLUSTER = os.environ.get('RANCHER_CLEANUP_CLUSTER', "True")

DATA_SUBDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                           'resource')
AWS_SSH_KEY_NAME = os.environ.get("AWS_SSH_KEY_NAME")
AWS_NODE_COUNT = os.environ.get("AWS_NODE_COUNT", 3)


def test_rke_cluster_create():


    # Create nodes in AWS
    aws_nodes = create_nodes()
    clusterfilepath = create_rke_cluster_config(aws_nodes)

    is_file = os.path.isfile(clusterfilepath)
    assert is_file

    print("clusterfilepath")
    print(clusterfilepath)

    # Create RKE K8s Cluster
    rkecommand = '/Users/soumya/rke/rke ' + "up" \
                 + ' --config ' + clusterfilepath
    print(rkecommand)
    result = run_command_with_stderr(rkecommand)
    print(result)

    rke_config_file =  "/Users/soumya/rke/"+ "kube_config_clusternew.yml"
    rke_config_file = "kube_config_clusternew.yml"
    print(rke_config_file)


def create_nodes():

    aws_nodes = \
        AmazonWebServices().create_multiple_nodes(
            AWS_NODE_COUNT, random_test_name("soumyatest"), wait_for_ready=True)
    assert len(aws_nodes) == AWS_NODE_COUNT
    for aws_node in aws_nodes:
        print(aws_node)
        print(aws_node.public_ip_address)

    return aws_nodes


def create_rke_cluster_config(aws_nodes):

    if(AWS_NODE_COUNT == 3):
       configfile = "cluster.yml"
    if (AWS_NODE_COUNT == 5):
       configfile = "cluster_config1.yml"
    if (AWS_NODE_COUNT == 9):
       configfile = "cluster_config2.yml"


    rkeconfig = readDataFile(DATA_SUBDIR, configfile)
    for i in range(0, AWS_NODE_COUNT):
        ipstring = "$ip"+str(i)
        print (ipstring)
        rkeconfig = rkeconfig.replace(ipstring, aws_nodes[i].public_ip_address)
    rkeconfig = rkeconfig.replace("$AWS_SSH_KEY_NAME", AWS_SSH_KEY_NAME)

    print(rkeconfig)
    clusterfilepath = DATA_SUBDIR + "/" + "clusternew.yml"
    print(clusterfilepath)

    f = open(clusterfilepath, "w")
    f.write(rkeconfig)
    f.close()
    return clusterfilepath


def readDataFile(data_dir, name):

    fname = os.path.join(data_dir, name)
    print("File Name is: ")
    print(fname)
    is_file = os.path.isfile(fname)
    assert is_file
    with open(fname) as f:
        return f.read()
