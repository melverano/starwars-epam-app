import requests
from sys import argv
import os
import subprocess

script, env_pipeline = argv
kubeconfig = os.environ['KUBECONFIG']
endpoint_nlb = subprocess.getoutput("kubectl get ingress -n " + env_pipeline + " | awk 'FNR == 2 {print $4}'")
template_url = "http://" + endpoint_nlb

urls = [template_url,
        template_url + "/characters",
        template_url + "/starships",
        template_url + "/top",
        template_url + "/updatedb"
        ]

for i in urls:
    status = requests.get(i)
    if status.status_code == 200:
        print("Страница доступна - ", i , " Статус запроса = ", str(status))
    else:
        raise SystemError("Нет доступа к странице - " + i + " Статус запроса = " + str(status))
